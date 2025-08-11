# **Библиотека для создания файлов отчетов** # 

Для формирования xlsx отчета из нескольких csv файлов.

## Разработка ##

    source venv/bin/activate

## Установка ##

    pip install MultiTabReportsLib

## Использование ##

python3 index.py OUTPUT_NAME="test/res.xlsx" HEADERS_PATH="" META_NAME="test/meta.csv" SEP=";"

<!-- python3 OUTPUT_NAME="res.xlsx" HEADERS_PATH="" META_NAME="excel.meta" SEP=;  "Опросный лист ТУ_2025-07-28_14-28-44.csv" "Опросный лист УСПД_2025-07-28_14-33-04.csv" -->