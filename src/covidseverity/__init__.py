"""
Python package `defend-covid-severity` to generate severity-prediction views of
the datasets provided by FAPESP COVID-19 DataSharing/BR.
"""

import pandas as pd


def read_patients(filepath_or_buffer, sep='|'):
    """
    Reads and organizes patients file.
    """
    data = pd.read_table(filepath_or_buffer, sep=sep)
    assert data.shape[1] == 7

    data.rename(str.upper, axis='columns', inplace=True)

    for column in ['AA_NASCIMENTO']:
        data[column] = pd.to_numeric(
            data[column], errors='coerce', downcast='integer')

    missing_values = [
        ('CD_PAIS', 'XX'),
        ('CD_UF', 'UU'),
        ('CD_MUNICIPIO', 'MMMM'),
        ('CD_CEPREDUZIDO', 'CCCC')
    ]

    for column, value in missing_values:
        data.loc[data[column] == value, column] = None

    return data


def read_tests(filepath_or_buffer, sep='|'):
    """
    Reads and organizes tests file.
    """
    data = pd.read_table(filepath_or_buffer, sep=sep)
    assert data.shape[1] == 9

    data.rename(str.upper, axis='columns', inplace=True)

    nominal_columns = [col for col in data if col.startswith('DE_')]
    for column in nominal_columns:
        data[column] = data[column].str.strip()

    date_columns = [col for col in data if col.startswith('DT_')]
    for column in date_columns:
        data[column] = pd.to_datetime(data[column], format='%d/%m/%Y')

    return data
