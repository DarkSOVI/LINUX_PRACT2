#!/bin/bash

echo "--- Тест успешного запуска с корректными параметрами ---"

# Определяем тестовые параметры
PACKAGE="test-app"
REPO_PATH="https://api.testrepo.com/packages"
REPO_MODE="remote"
ASCII_MODE="tree"

# Запускаем программу
python Program.py \
    --package "$PACKAGE" \
    --repo-path "$REPO_PATH" \
    --repo-mode "$REPO_MODE" \
    --ascii-mode "$ASCII_MODE"

# Проверяем код завершения
if [ $? -eq 0 ]; then
    echo -e "\n Успех: Программа завершилась с кодом 0."
else
    echo -e "\n Ошибка: Программа завершилась с кодом $? вместо 0."
    exit 1
fi