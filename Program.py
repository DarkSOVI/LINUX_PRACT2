import argparse
import sys
from typing import Dict, List, Optional

# Имитация данных репозитория Alpine Linux.
MOCKED_ALPINE_REPO: Dict[str, Dict[str, List[str]]] = {
    "curl": {
        "description": "Client for URLs",
        "version": "8.4.0-r0",
        "depends": ["libcurl", "zlib", "libssh2"]  #Прямые зависимости
    },
    "nginx": {
        "description": "High performance web server",
        "version": "1.24.0-r0",
        "depends": ["pcre", "zlib", "openssl", "libc"]
    },
    "python3": {
        "description": "Python 3 interpreter",
        "version": "3.11.5-r0",
        "depends": ["libffi", "openssl", "zlib", "expat", "libc"]
    },
    "libcurl": {
        "description": "Shared library for curl",
        "version": "8.4.0-r0",
        "depends": ["libc"]
    },
    "zlib": {
        "description": "Compression library",
        "version": "1.2.13-r0",
        "depends": ["libc"]
    },
    "my-project": {
        "description": "The custom project",
        "version": "1.0.0-r0",
        "depends": ["nginx", "curl", "python3"] #Зависимости нашего пакета
    }
}

#-------------------------------------------------------------------------------------------------

def parse_arguments():
    """
    Разбирает аргументы командной строки и возвращает объект с параметрами.
    Реализует обработку ошибок для всех параметров.
    """
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей пакетов.",
        epilog="Пример использования: python Program.py --package my-app --repo-url https://myrepo.com --repo-mode remote --ascii-mode tree"
    )

    #Имя анализируемого пакета
    parser.add_argument(
        '-p', '--package',
        type=str,
        required=True,
        help="Имя анализируемого пакета (например, 'requests')."
    )

    #URL-адрес репозитория или путь к файлу
    parser.add_argument(
        '-r', '--repo-path',
        type=str,
        required=True,
        help="URL-адрес репозитория или путь к файлу тестового репозитория."
    )

    #Режим работы с тестовым репозиторием (выбор из ограниченного списка)
    parser.add_argument(
        '-m', '--repo-mode',
        choices=['local', 'remote'],
        required=True,
        help="Режим работы с репозиторием: 'local' (файл) или 'remote' (URL)."
    )

    #Режим вывода зависимостей в формате ASCII-дерева (булевый флаг)
    parser.add_argument(
        '--ascii-mode',
        choices=['tree', 'list'],
        default='list',
        help="Режим вывода зависимостей: 'tree' (ASCII-дерево) или 'list' (список). По умолчанию: 'list'."
    )

    return parser.parse_args()

#-------------------------------------------------------------------------------------------------

def fetch_repo_data(repo_path: str) -> Optional[Dict[str, Dict]]:
    """
    Имитирует сетевой запрос к URL-адресу и возвращает смоделированные данные.
    """
    print(f"\nПытаемся получить данные репозитория...")
    
    #Имитация проверки, что передан URL
    if repo_path.startswith("http://") or repo_path.startswith("https://"):
        print(f"  -> Имитация сетевого запроса к URL: {repo_path}")
        #Возвращаем встроенные данные
        return MOCKED_ALPINE_REPO
    else:
         print(f"Ошибка: Указанный путь '{repo_path}' не похож на URL-адрес.")
         return None

def get_dependencies(package_name: str, repo_data: Dict[str, Dict]) -> List[str]:
    """
    Извлекает список прямых зависимостей для заданного пакета.
    """
    if package_name in repo_data:
        package_info = repo_data[package_name]
        dependencies = package_info.get("depends", [])
        return dependencies
    else:
        return []

#-------------------------------------------------------------------------------------------------

def run_prototype():
    """
    Основная функция для запуска.
    """
    try:
        args = parse_arguments()
        
        #Вывод настроенных параметров
        print("НАСТРОЕННЫЕ ПАРАМЕТРЫ:")
        config = vars(args)
        for key, value in config.items():
            print(f"- **{key.replace('_', '-').capitalize()}**: {value}")

        #Получение данных репозитория
        repo_data = fetch_repo_data(args.repo_path)
        
        if not repo_data:
            print("\nНе удалось получить данные репозитория. Завершение.")
            sys.exit(1)

        #Получение и вывод прямых зависимостей
        package_deps = get_dependencies(args.package, repo_data)

        if package_deps:
            version = repo_data.get(args.package, {}).get('version', 'N/A')
            print(f"\nПрямые зависимости для пакета **{args.package}** (Версия: {version}):")
            for dep in package_deps:
                print(f"   - {dep}")
        else:
            print(f"\nПакет **{args.package}** не найден в репозитории или не имеет прямых зависимостей.")

        print("\nДанные о прямых зависимостях собраны.")

    except SystemExit as e:
        if e.code != 0:
            print("\nОшибка разбора аргументов. Пожалуйста, проверьте синтаксис.", file=sys.stderr)
        sys.exit(e.code)


if __name__ == "__main__":
    run_prototype()