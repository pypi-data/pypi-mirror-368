import os
from pathlib import Path

# 프로젝트 루트 디렉토리 설정 (hamoni 폴더)
PROJECT_ROOT = Path(__file__).parents[0]  # backtester -> libraries -> hamoni
FUTURES_DATA_ROOT = PROJECT_ROOT / 'data_futures'
SPOT_DATA_ROOT = PROJECT_ROOT / 'data_spot'

# 데이터 디렉토리 설정
FUTURES_DATA_DIR = {
    '1m': FUTURES_DATA_ROOT / 'data_1m',
    '5m': FUTURES_DATA_ROOT / 'data_5m',
    '15m': FUTURES_DATA_ROOT / 'data_15m',
    '30m': FUTURES_DATA_ROOT / 'data_30m',
    '45m': FUTURES_DATA_ROOT / 'data_45m',
    '60m': FUTURES_DATA_ROOT / 'data_60m',
    '90m': FUTURES_DATA_ROOT / 'data_90m',
    '120m': FUTURES_DATA_ROOT / 'data_120m',
    '180m': FUTURES_DATA_ROOT / 'data_180m',
    '240m': FUTURES_DATA_ROOT / 'data_240m',
    '360m': FUTURES_DATA_ROOT / 'data_360m',
    '1440m': FUTURES_DATA_ROOT / 'data_1440m',
    '1w': FUTURES_DATA_ROOT / 'data_1w',
}

# 데이터 디렉토리 설정
SPOT_DATA_DIR = {
    '1m': SPOT_DATA_ROOT / 'data_1m',
    '5m': SPOT_DATA_ROOT / 'data_5m',
    '15m': SPOT_DATA_ROOT / 'data_15m',
    '30m': SPOT_DATA_ROOT / 'data_30m',
    '45m': SPOT_DATA_ROOT / 'data_45m',
    '60m': SPOT_DATA_ROOT / 'data_60m',
    '90m': SPOT_DATA_ROOT / 'data_90m',
    '120m': SPOT_DATA_ROOT / 'data_120m',
    '180m': SPOT_DATA_ROOT / 'data_180m',
    '240m': SPOT_DATA_ROOT / 'data_240m',
    '360m': SPOT_DATA_ROOT / 'data_360m',
    '1440m': SPOT_DATA_ROOT / 'data_1440m',
    '1w': SPOT_DATA_ROOT / 'data_1w',
}
