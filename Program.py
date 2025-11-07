import argparse
import sys
import json
from collections import deque
from typing import Dict, List, Optional, Tuple

MOCKED_ALPINE_REPO: Dict[str, Dict[str, List[str]]] = {
    "curl": {"depends": ["libcurl", "zlib"]},
    "nginx": {"depends": ["pcre", "zlib", "openssl"]},
    "python3": {"depends": ["libffi", "openssl", "zlib"]},
    "libcurl": {"depends": ["libc"]},
    "zlib": {"depends": ["libc"]},
    "my-project": {"depends": ["nginx", "curl", "python3"]}
}

# -----------------------------------------------------------

def parse_arguments():
    """
    Разбирает аргументы командной строки. Возвращаем режим 'local' для тестирования.
    """
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей пакетов.",
        epilog="Пример: python Program.py -p my-project -r https://repo.url.com -m remote | Тест: python Program.py -p A -r test_repo.json -m local"
    )
    
    parser.add_argument('-p', '--package', type=str, required=True, help="Имя анализируемого пакета.")
    parser.add_argument('-r', '--repo-path', type=str, required=True, help="URL репозитория или путь к файлу (для режима 'local').")
    
    parser.add_argument(
        '-m', '--repo-mode',
        choices=['remote', 'local'],
        required=True,
        help="Режим работы: 'remote' (рабочий URL) или 'local' (тестовый JSON файл)."
    )
    
    parser.add_argument('--ascii-mode', choices=['tree', 'list'], default='list', help="Режим вывода зависимостей.")
    
    return parser.parse_args()


# --- ЧТЕНИЕ РЕПОЗИТОРИЯ ---

def fetch_repo_data(repo_path: str, repo_mode: str) -> Optional[Dict[str, Dict]]:
    """
    Получает данные репозитория:
    - remote: использует встроенную заглушку (MOCKED_ALPINE_REPO).
    - local: читает JSON файл (для режима тестирования).
    """
    print(f"\nПытаемся получить данные репозитория в режиме '{repo_mode}'...")
    
    if repo_mode == 'remote':
        if repo_path.startswith("http"):
            print(f"   -> Имитация сетевого запроса к URL: {repo_path}")
            return MOCKED_ALPINE_REPO
        else:
            print(f"Ошибка: '{repo_path}' не похож на URL. Невозможно имитировать remote-режим.")
            return None
    
    elif repo_mode == 'local':
        try:
            print(f"   -> Чтение из тестового файла: {repo_path}")
            with open(repo_path, 'r', encoding='utf-8') as f:
                 repo_data = json.load(f)
                 return repo_data
        except FileNotFoundError:
            print(f"Ошибка: Тестовый файл '{repo_path}' не найден.")
            return None
        except Exception as e:
            print(f"Ошибка при чтении тестового файла: {e}")
            return None
             
    return None

# --- ГЛАВНЫЙ АЛГОРИТМ ---

def build_dependency_graph_bfs(
    start_package: str, 
    repo_data: Dict[str, Dict]
) -> Tuple[Dict[str, List[str]], List[Tuple[str, str]]]:
    """
    Строит граф транзитивных зависимостей с помощью алгоритма BFS (без рекурсии).
    Возвращает: (словарь графа, список найденных циклических зависимостей)
    """
    dependency_graph: Dict[str, List[str]] = {}
    
    queue = deque([ (start_package, None) ]) 
    
    visited_dependencies: Dict[str, List[str]] = {start_package: []}
    
    cycles_found: List[Tuple[str, str]] = []

    while queue:
        current_package, parent_package = queue.popleft()
        
        package_info = repo_data.get(current_package)
        if not package_info:
            continue

        direct_dependencies = package_info.get("depends", [])
        
        if current_package not in dependency_graph:
             dependency_graph[current_package] = []
        
        for dep in direct_dependencies:
            dependency_graph.setdefault(current_package, []).append(dep)

            if dep in visited_dependencies:
                if dep == start_package:
                     if (dep, current_package) not in cycles_found and (current_package, dep) not in cycles_found:
                          cycles_found.append((dep, current_package))
                
                if dep in dependency_graph:
                    if dep in visited_dependencies[dep] or dep == current_package:
                         if (current_package, dep) not in cycles_found:
                            cycles_found.append((current_package, dep))

                continue 
            
            visited_dependencies[dep] = visited_dependencies.get(current_package, []) + [current_package]
            queue.append((dep, current_package))

    return dependency_graph, cycles_found

# --- ОСНОВНАЯ ФУНКЦИЯ ---

def run_prototype():
    try:
        args = parse_arguments()
        
        print("НАСТРОЕННЫЕ ПАРАМЕТРЫ:")
        for key, value in vars(args).items():
            print(f"- **{key.replace('_', '-').capitalize()}**: {value}")

        repo_data = fetch_repo_data(args.repo_path, args.repo_mode)
        
        if not repo_data:
            print("\nНе удалось получить данные репозитория. Завершение.")
            sys.exit(1)
        
        print(f"\nСтроим транзитивный граф зависимостей для пакета **{args.package}** (алгоритм BFS)...")
        
        graph, cycles = build_dependency_graph_bfs(args.package, repo_data)

        print("\n--- Результат построения графа (родитель -> потомок) ---")
        
        sorted_packages = sorted(graph.keys())
        
        all_dependencies = set()
        for parent in sorted_packages:
            if graph[parent]:
                 print(f"**{parent}** -> {', '.join(graph[parent])}")
                 all_dependencies.update(graph[parent])
        
        total_unique_deps = len(all_dependencies - {args.package})
        print(f"\nОбщее количество уникальных транзитивных зависимостей: **{total_unique_deps}**")
        
        if cycles:
            print("\nОбнаружены циклические зависимости:")
            for p1, p2 in cycles:
                print(f"   - Цикл: {p1} <-> {p2}")
        else:
            print("\nЦиклических зависимостей не обнаружено.")

        print("\nГраф зависимостей построен алгоритмом BFS.")

    except SystemExit as e:
        sys.exit(e.code)


if __name__ == "__main__":
    run_prototype()