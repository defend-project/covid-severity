"""
Python package `defend-covid-severity` to generate severity-prediction views of
the datasets provided by FAPESP COVID-19 DataSharing/BR.
"""

import pandas as pd


def read_patients(filepath_or_buffer, sep='|'):
    """
    Read and organizes patients file.
    """
    data = pd.read_table(filepath_or_buffer, sep=sep)
    assert data.shape[1] == 7

    data.rename(str.upper, axis='columns', inplace=True)
    data.rename(columns={
        'ID_PACIENTE': 'patient',
        'IC_SEXO': 'sex',
        'AA_NASCIMENTO': 'birth_year',
        'CD_PAIS': 'country',
        'CD_UF': 'state',
        'CD_MUNICIPIO': 'city',
        'CD_CEPREDUZIDO': 'postal_code'}, inplace=True)

    for column in ['birth_year', 'postal_code']:
        data[column] = pd.to_numeric(
            data[column], errors='coerce', downcast='integer')

    missing_values = [
        ('country', 'XX'),
        ('state', 'UU'),
        ('city', 'MMMM'),
    ]

    for column, value in missing_values:
        data[column].loc[data[column] == value] = None

    return data
