import argparse
import sys

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


def run_prototype():
    """
    Основная функция для запуска прототипа.
    """
    try:
        #Получаем и проверяем все параметры
        args = parse_arguments()

        print("Запуск инструмента визуализации графа зависимостей\n")
        print("НАСТРОЕННЫЕ ПАРАМЕТРЫ:")
        
        #Преобразуем объект `args` в словарь для удобного вывода
        config = vars(args)
        
        for key, value in config.items():
            print(f"- **{key.replace('_', '-').capitalize()}**: {value}")

        print("\n Параметры успешно загружены.")

    #Блок обработки ошибок
    except SystemExit as e:
        if e.code != 0:
            print("\n Ошибка разбора аргументов. Пожалуйста, проверьте синтаксис.", file=sys.stderr)
            #argparse уже вывел подробное сообщение об ошибке, поэтому просто завершаем
        sys.exit(e.code)


if __name__ == "__main__":
    run_prototype()