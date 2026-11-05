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
| `src/snp_alloc/models.py` | Схемы `Request` и `Supply` (pydantic): типы, ограничения, `rounding_step`, `min_shipment_qty` |
| `src/snp_alloc/allocate.py` | Ядро `allocate(available_qty, requests) -> dict[str, int]` |
| `src/snp_alloc/csv_reader.py` | Чтение CSV в кейсы; невалидные строки уходят в `rejection_reasons` |
| `src/snp_alloc/main.py` | Точка входа `snp-alloc` |
| `tests/` | Планы CSV-кейсов, собственные кейсы, property-тесты на hypothesis |

Правило распределения и обоснование решений описаны в [REPORT.md](REPORT.md).
