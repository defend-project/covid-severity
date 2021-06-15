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

    data.drop_duplicates(inplace=True)

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

    data.drop_duplicates(inplace=True)

    return data


def read_outcomes(filepath_or_buffer, sep='|'):
    """
    Reads and organizes outcomes file.
    """
    data = pd.read_table(filepath_or_buffer, sep=sep)
    assert data.shape[1] == 8

    missing_values = [
        ('DT_DESFECHO', 'DDMMAA'),
    ]

    for column, value in missing_values:
        data.loc[data[column] == value, column] = None

    date_columns = [col for col in data if col.startswith('DT_')]
    for column in date_columns:
        data[column] = pd.to_datetime(data[column], format='%d/%m/%Y')

    data.drop_duplicates(inplace=True)

    data['UI_DIAS_DESFECHO'] = (data['DT_DESFECHO'] -
                                data['DT_ATENDIMENTO']).dt.days

    return data


def assess_sample_severity(sample):
    if sample['UI_DIAS_DESFECHO'] > 9 and sample['DE_TIPO_ATENDIMENTO'] == 'Internado':
        return 1

    if not pd.isna(sample['DE_DESFECHO']
                   ) and sample['DE_DESFECHO'].find('Óbito'):
        return 1

    return 0


def assess_severity(data):
    """
    Computes severity for each sample in `data`.

    Parameters
    ----------
    data: DataFrame (n_samples, 9)
        Data with outcomes, see `read_outcomes`.
    """
    return data.apply(assess_sample_severity, axis=1)
