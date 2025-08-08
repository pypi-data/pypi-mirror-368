import credentials

from sys import path
path.append('./src/bgp_data_interface')
from s3 import S3
from utils import location


import pandas as pd



def test_init_wu() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')

    assert api is not None
    assert isinstance(api, S3)


def test_s3_retrieve() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')
    df = api.retrieve({})

    today = pd.Timestamp.now()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == (today + pd.Timedelta(days=1)).day
    assert df.iloc[-1]['date_time'].hour == 0
    assert 'temperature_2m' in df.columns
    assert 'global_tilted_irradiance' in df.columns


def test_s3_retrieve_location() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')
    df = api.retrieve({
        'location': location.ABP
    })

    today = pd.Timestamp.now()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == (today + pd.Timedelta(days=1)).day
    assert df.iloc[-1]['date_time'].hour == 0




def test_s3_retrieve_type() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.retrieve({
        'type': 'historical',
        'source': 'weather_api',
        'start_date': yesterday.strftime('%Y-%m-%d'),
        'end_date': yesterday.strftime('%Y-%m-%d')
    })

    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23




def test_s3_retrieve_date() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')
    start_date = '2025-05-08'
    end_date = '2025-05-09'
    df = api.retrieve({
        'start_date': start_date,
        'end_date': end_date
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (192, 68)
    assert df.iloc[0]['date_time'].day == 8
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == 10
    assert df.iloc[-1]['date_time'].hour == 0



def test_s3_retrieve_source() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')
    df = api.retrieve({
        'source': 'weather_api'
    })

    today = pd.Timestamp.now()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_s3_retrieve_too_early_dates() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')
    start_date = '2025-05-07'
    end_date = '2025-05-09'
    df = api.retrieve({
        'start_date': start_date,
        'end_date': end_date
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (192, 68)
    assert df.iloc[0]['date_time'].day == 8
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == 10
    assert df.iloc[-1]['date_time'].hour == 0


def test_s3_retrieve_too_late_dates() -> None:
    api = S3(credentials.AWS_ACCESS_KEY, credentials.AWS_SECRET_KEY, 'bgp-weather-data')
    start_date = '2025-05-07'
    end_date = '2025-05-09'
    df = api.retrieve({
        'start_date': start_date,
        'end_date': end_date
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (192, 68)
    assert df.iloc[0]['date_time'].day == 8
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == 10
    assert df.iloc[-1]['date_time'].hour == 0


def test_s3_store() -> None:
    api = S3(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        'bgp-energy-data'
    )

    df = pd.DataFrame({
        'date_time': pd.date_range(start='2025-05-08', periods=24, freq='h'),
        'temperature_2m': [15 + i for i in range(24)],
        'global_tilted_irradiance': [200 + i * 10 for i in range(24)]
    })

    key = 'AWS/solar/test_write.csv'
    api.store(df, key)

    assert api.object_exists(key)

    api.delete_object(key)
