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
    "libc": {"depends": []},
    "pcre": {"depends": []},
    "openssl": {"depends": []},
    "libffi": {"depends": []},
    "my-project": {"depends": ["nginx", "curl", "python3"]}
}

# -----------------------------------------------------------

def parse_arguments():
    """
    Разбирает аргументы командной строки.
    """
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей пакетов.",
        epilog="Пример: python Program.py -p my-project -r https://repo.url.com -m remote --ascii-mode tree | Тест: python Program.py -p A -r test_repo.json -m local"
    )
    
    parser.add_argument('-p', '--package', type=str, required=True, help="Имя анализируемого пакета.")
    parser.add_argument('-r', '--repo-path', type=str, required=True, help="URL репозитория или путь к файлу (для режима 'local').")
    
    parser.add_argument(
        '-m', '--repo-mode',
        choices=['remote', 'local'],
        required=True,
        help="Режим работы: 'remote' (рабочий URL) или 'local' (тестовый JSON файл)."
    )
    
    parser.add_argument(
        '--ascii-mode', 
        choices=['tree', 'list'], 
        default='list', 
        help="Режим вывода зависимостей: 'tree' (ASCII-дерево) или 'list' (плоский список)."
    )
    
    return parser.parse_args()

def fetch_repo_data(repo_path: str, repo_mode: str) -> Optional[Dict[str, Dict]]:
    """
    Имитирует получение данных репозитория.
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

def build_dependency_graph_bfs(
    start_package: str, 
    repo_data: Dict[str, Dict]
) -> Tuple[Dict[str, List[str]], List[Tuple[str, str]]]:
    """
    Строит граф транзитивных зависимостей с помощью алгоритма BFS без рекурсии.
    """
    dependency_graph: Dict[str, List[str]] = {}

    queue = deque([ start_package ]) 
    
    visited: set = {start_package}
    
    cycles_found: List[Tuple[str, str]] = []

    while queue:
        current_package = queue.popleft()
        
        package_info = repo_data.get(current_package)
        if not package_info:
            continue

        direct_dependencies = package_info.get("depends", [])
        dependency_graph.setdefault(current_package, [])
        
        for dep in direct_dependencies:
            dependency_graph[current_package].append(dep)
            
            if dep in visited:
                 if (current_package, dep) not in cycles_found and (dep, current_package) not in cycles_found:
                     cycles_found.append((current_package, dep))
                 continue 
            
            visited.add(dep)
            queue.append(dep)

    return dependency_graph, cycles_found

def invert_graph(repo_data: Dict[str, Dict]) -> Dict[str, List[str]]:
    """
    Создает обратный граф из полных данных репозитория (repo_data).
    Ключ - это зависимость, значение - пакеты, которые от нее зависят.
    """
    reverse_graph: Dict[str, List[str]] = {}
    
    for parent_pkg, info in repo_data.items():
        dependencies = info.get("depends", [])
        
        for dep in dependencies:
            reverse_graph.setdefault(dep, []).append(parent_pkg)
            
    for pkg in repo_data.keys():
        reverse_graph.setdefault(pkg, []) 
            
    return reverse_graph

def find_reverse_dependencies(
    start_package: str, 
    reverse_graph: Dict[str, List[str]]
) -> List[str]:
    """
    Находит все прямые и транзитивные обратные зависимости.
    """
    reverse_deps = set()
    queue = deque([start_package])
    visited = {start_package} 
    
    while queue:
        current = queue.popleft()
        dependents = reverse_graph.get(current, [])
        
        for dependent in dependents:
            if dependent not in visited:
                reverse_deps.add(dependent)
                visited.add(dependent)
                queue.append(dependent)

    return sorted(list(reverse_deps - {start_package}))

def print_ascii_tree(graph: Dict[str, List[str]], start_package: str, repo_data: Dict[str, Dict]):
    """
    Выводит граф зависимостей в формате ASCII-дерева.
    """
    print("\nВизуализация графа (ASCII-дерево):")

    def print_node(package: str, prefix: str, is_last: bool, current_path: set):
        version = repo_data.get(package, {}).get('version', 'N/A')
        
        print(prefix + ("└── " if is_last else "├── ") + f"{package} ({version})")

        if package in current_path:
            print(prefix + ("    " if is_last else "│   ") + "└── (Циклическая зависимость)")
            return

        dependencies = graph.get(package)
        if not dependencies:
            return

        current_path.add(package)
        
        next_prefix = prefix + ("    " if is_last else "│   ")
        
        sorted_deps = sorted(dependencies)
        
        for i, dep in enumerate(sorted_deps):
            is_last_dep = (i == len(sorted_deps) - 1)
            print_node(dep, next_prefix, is_last_dep, current_path)
            
        current_path.remove(package)
        
    print_node(start_package, "", True, set())

def run_prototype():
    """
    Главная функция запуска.
    """
    try:
        args = parse_arguments()
        
        print("Запуск инструмента визуализации графа зависимостей\n")
        print("НАСТРОЕННЫЕ ПАРАМЕТРЫ:")
        for key, value in vars(args).items():
            print(f"- **{key.replace('_', '-').capitalize()}**: {value}")

        repo_data = fetch_repo_data(args.repo_path, args.repo_mode)
        
        if not repo_data:
            print("\nНе удалось получить данные репозитория. Завершение.")
            sys.exit(1)
            
        print(f"\nСтроим транзитивный граф зависимостей для пакета **{args.package}** (алгоритм BFS)...")
        forward_graph, cycles = build_dependency_graph_bfs(args.package, repo_data)

        reverse_graph = invert_graph(repo_data)
        reverse_deps = find_reverse_dependencies(args.package, reverse_graph)
        
        print(f"\nОбратные зависимости (пакеты, зависящие от **{args.package}** :")
        if reverse_deps:
            print(f"   -> Прямые и транзитивные потребители: {', '.join(reverse_deps)}")
        else:
            print(f"   -> Пакет **{args.package}** не используется другими пакетами в графе.")
        
        if args.ascii_mode == 'tree':
            print_ascii_tree(forward_graph, args.package, repo_data)
        else:
            print("\n--- Результат построения графа (родитель -> потомок) ---")
            sorted_packages = sorted(forward_graph.keys())
            for parent in sorted_packages:
                if forward_graph[parent]:
                     print(f"**{parent}** -> {', '.join(forward_graph[parent])}")
        
        if cycles:
            print("\nОбнаружены циклические зависимости:")
            for p1, p2 in cycles:
                print(f"   - Цикл: {p1} <-> {p2}")
        else:
            print("\nЦиклических зависимостей не обнаружено.")

        print("\nВсе этапы завершены успешно!")

    except SystemExit as e:
        if e.code != 0:
            print("\nОшибка разбора аргументов. Пожалуйста, проверьте синтаксис.", file=sys.stderr)
        sys.exit(e.code)


if __name__ == "__main__":
    run_prototype()