#!/usr/bin/env python
from io import BytesIO, StringIO

import pytest

from martens import martens


@pytest.mark.parametrize("file_path", [
    './tests/test_data/file_example_XLSX_10.xlsx',
    './tests/test_data/file_example_XLS_10.xls',
])
def test_total_ages_women(file_path):
    total_ages_women = martens.SourceFile(file_path=file_path) \
        .dataset.headings_lower.filter(lambda gender: gender == 'Female') \
        .long_apply(lambda age: sum(age))
    assert total_ages_women == 263


@pytest.mark.parametrize("file_path", [
    './tests/test_data/file_example_XLSX_10.xlsx',
    './tests/test_data/file_example_XLS_10.xls',
])
def test_total_ages_women_bytes_stream(file_path):
    total_ages_women = martens.SourceStream(stream=BytesIO(open(file_path, 'rb').read()), file_type=file_path.split('.')[-1]) \
        .dataset.headings_lower.filter(lambda gender: gender == 'Female') \
        .long_apply(lambda age: sum(age))
    assert total_ages_women == 263


@pytest.mark.parametrize("file_path", ['./tests/test_data/file_example_XLS_10.xls'])
def test_chart_generator(file_path):
    data = martens.SourceFile(file_path=file_path) \
        .dataset.headings_lower \
        .group_by(['gender', 'country'], count='count') \
        .mutate(lambda country: {'Great Britain': 1, 'France': 2, 'United States': 3}[country], 'country_order') \
        .mutate(lambda gender: {'Male': 1, 'Female': 2}[gender], 'gender_order') \
        .pivot_chart_constructor(x_name='country', colour='gender', y_name='count', colour_sort_keys=['gender_order'], x_sort_keys=['country_order'])
    # print(data)


@pytest.mark.parametrize("file_path", ['./tests/test_data/junk.csv'])
def test_csv_import(file_path):
    data = martens.SourceFile(file_path=file_path, from_row=3) \
        .dataset.headings_lower.replace(float, ['age'])
    assert sum(data['age']) == 115


@pytest.mark.parametrize("file_path", ['./tests/test_data/junk.csv'])
def test_csv_import_from_stringio(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        stream = StringIO(f.read())
        data = martens.SourceStream(stream, file_type="csv", from_row=3).dataset.headings_lower.infer_types
        assert sum(data['age']) == 115
