# agi-med-utils

Стандартизированный компонент GRPC клиентов общей библиотеки отдела

## Ответственный разработчик

@bakulin

## Общая информация

### Фичи:

- Абстрактный grpc клиент

## Тесты

- `sudo docker-compose up --build`

### Линтеры

```shell
pip install black flake8-pyproject mypy
black .
flake8
mypy .
```

или через pre-commit

```shell
pip install pre-commit
pre-commit install
pre-commit run --all-files # проверка вручную
```
