# DDD CLI

This package adds custom commands to Django to make it easier to implement a Domain-Driven Design (DDD) architecture.

## Available commands

- `ddd create-entity [-h] [--split] app_path entity_name`
- `ddd create-service [-h] app_path entity_name`
- `ddd create-repository [-h] app_path entity_name`
- `ddd create-dto [-h] [--split] app_path dto_name`
- `ddd create-serializer [-h] [--split] app_path serializer_name`
- `ddd create-view-api-apiview [-h] app_path entity_name`
- `ddd create-view-api-viewset [-h] app_path entity_name`
- `ddd create-view [-h] app_path entity_name`

## Show help
- `ddd --help`

## Python version
3.12.8