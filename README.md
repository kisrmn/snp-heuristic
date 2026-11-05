# SNP Heuristic: распределение дефицита

Нужен только [uv](https://docs.astral.sh/uv/). Python 3.10+ и зависимости uv поставит сам.

```bash
uv run snp-alloc            # посчитать все кейсы из data/ и вывести план
uv run pytest               # тесты
```

Другой каталог с CSV: `uv run snp-alloc --data path/to/dir`.

## Структура

| Файл | Что внутри |
|---|---|
| `src/snp_alloc/models.py` | Схемы `Request` и `Supply` (pydantic): типы, ограничения, `step`, `min_qty` |
| `src/snp_alloc/allocate.py` | Ядро `allocate(available_qty, requests) -> dict[str, int]` |
| `src/snp_alloc/io.py` | Чтение CSV в кейсы; невалидные строки уходят в `rejected` |
| `src/snp_alloc/cli.py` | Точка входа `snp-alloc` |
| `tests/` | Планы CSV-кейсов, собственные кейсы, property-тесты на hypothesis |

Правило распределения и обоснование решений описаны в [REPORT.md](REPORT.md).
