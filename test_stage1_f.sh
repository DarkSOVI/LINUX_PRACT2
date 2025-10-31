#!/bin/bash

# Функция для запуска теста с ожидаемой ошибкой
run_error_test() {
    local test_name=$1
    local command=$2
    local expected_code=1 # Ожидаем код ошибки (ненулевой)

    echo -e "\n--- Тест: $test_name ---"
    
    # Запускаем команду, перенаправляя вывод в /dev/null, чтобы не загромождать терминал
    # Запуск с "|| true" предотвращает немедленное завершение скрипта при ошибке Python
    $command > /dev/null 2>&1
    local actual_code=$?

    if [ $actual_code -ne 0 ]; then
        echo "Успех: Программа корректно завершилась с кодом ошибки: $actual_code."
    else
        echo "Ошибка: Программа завершилась с кодом 0, хотя должна была завершиться с ошибкой."
        exit 1
    fi
}

echo "--- 2. Тест обработки ошибок ---"

# Сценарий 1: Отсутствует обязательный аргумент (--package)
run_error_test \
    "Отсутствие обязательного параметра (--package)" \
    "python Program.py --repo-path /temp --repo-mode local"

# Сценарий 2: Неверный выбор (invalid choice для --repo-mode)
run_error_test \
    "Неверное значение для параметра выбора (--repo-mode)" \
    "python Program.py --package test --repo-path /temp --repo-mode invalid_choice"

echo -e "\n--- Все тесты обработки ошибок пройдены успешно ---"