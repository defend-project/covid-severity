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
    data.rename(lambda x: x[3:], axis='columns', inplace=True)

    data.drop(columns=['PAIS', 'UF', 'MUNICIPIO', 'CEPREDUZIDO'], inplace=True)
    data['NASCIMENTO'] = pd.to_numeric(
        data['NASCIMENTO'], errors='coerce', downcast='integer')

    data.drop_duplicates(inplace=True)

    return data


def read_tests(filepath_or_buffer, sep='|'):
    """
    Reads and organizes tests file.
    """
    data = pd.read_table(filepath_or_buffer, sep=sep)
    assert data.shape[1] == 9

    data.rename(str.upper, axis='columns', inplace=True)
    data.rename(lambda x: x[3:], axis='columns', inplace=True)
    data.rename({ 'COLETA' : 'DATA_COLETA' }, axis='columns', inplace=True)

    data.drop(columns=['ORIGEM', 'VALOR_REFERENCIA'], inplace=True)

    for column in ['EXAME', 'ANALITO', 'RESULTADO', 'UNIDADE']:
        data[column] = data[column].str.strip()

    date_columns = [col for col in data if col.startswith('DATA_')]
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

    data.rename(str.upper, axis='columns', inplace=True)
    data.drop(columns=['ID_CLINICA', 'DE_CLINICA'], inplace=True)

    for column in ['DT_DESFECHO', 'DT_ATENDIMENTO']:
        data.loc[data[column] == 'DDMMAA', column] = None

    data['XX_DIAS_ATE_DESFECHO'] = (
            pd.to_datetime(data['DT_DESFECHO'], format='%d/%m/%Y') -
            pd.to_datetime(data['DT_ATENDIMENTO'], format='%d/%m/%Y')).dt.days

    data.drop(columns=['DT_DESFECHO', 'DT_ATENDIMENTO'], inplace=True)
    data.rename(lambda x: x[3:], axis='columns', inplace=True)

    data.drop_duplicates(inplace=True)

    data['CLASSE'] = assess_severity(data)
    data.drop(columns=['DIAS_ATE_DESFECHO'], inplace=True)

    return data


def assess_sample_severity(sample):
    if sample['DIAS_ATE_DESFECHO'] >= 10 and sample['TIPO_ATENDIMENTO'] == 'Internado':
        return 'Grave'

    if "Óbito" in sample['DESFECHO']:
        return 'Grave'

    return 'Leve'


def assess_severity(data):
    """
    Computes severity for each sample in `data`.

    Parameters
    ----------
    data: DataFrame (n_samples, 9)
        Data with outcomes, see `read_outcomes`.
    """
    return data.apply(assess_sample_severity, axis=1)
