# hamoni/test/utils/data_utils.py
import pandas as pd
import pytz
from pathlib import Path
from typing import List, Optional, Union, Tuple, Dict, Any
import os
from urllib.request import urlretrieve
import zipfile
import csv
from binance.client import Client
import itertools
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging
import gc
from .config import FUTURES_DATA_DIR, SPOT_DATA_DIR, PROJECT_ROOT

# 상수 정의
MAX_WORKERS = 10
BATCH_SIZE = 10
DEFAULT_INTERVAL = '60m'
COLUMNS = [
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_volume', 'count',
    'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'
]

# 외부 함수
def get_data(
    symbol: str,
    interval: str = DEFAULT_INTERVAL,
    start: Optional[str] = None,
    end: Optional[str] = None,
    data_type: str = 'futures'
) -> pd.DataFrame:
    """OHLCV 데이터를 로드하고 전처리합니다.
    
    Args:
        symbol: 자산 심볼 (e.g. ``"BTCUSDT"``).
        interval: 시간 간격 (e.g. ``"60m"``).
        start: 시작 날짜 (e.g. ``"2024-01-01"``).
        end: 종료 날짜 (e.g. ``"2025-01-01"``).
        data_type: 데이터 타입 (e.g. ``"futures"`` 또는 ``"spot"``).
    
    Returns:
        pd.DataFrame: 전처리된 OHLCV 데이터
    
    Raises:
        FileNotFoundError: 데이터 파일이 존재하지 않는 경우
        DataProcessingError: 데이터 처리 중 오류 발생
    """
    try:
        data_dir = FUTURES_DATA_DIR if data_type == 'futures' else SPOT_DATA_DIR
        tz = pytz.timezone('Asia/Seoul')
        data_path = Path(data_dir[interval]) / f'{symbol}.csv'
        
        if not data_path.exists():
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")
        
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df.index = df.index.tz_localize(pytz.UTC).tz_convert(tz)
        
        if start is not None:
            df = df[start:]
        if end is not None:
            df = df[:end]
        
        return df
    
    except Exception as e:
        raise DataProcessingError(f"데이터 처리 중 오류 발생: {str(e)}")
    
    
def generate_data_for_backtest(
    symbols: List[str],
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    intervals: List[str],
    data_types: List[str]
) -> None:
    """백테스트용 데이터를 생성합니다.
    
    주의: 병렬처리를 사용하므로 Jupyter Notebook에서 실행하지 마세요.

    Args:
        symbols: 심볼 리스트 ['BTCUSDT', 'ETHUSDT', ...]
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        intervals: 시간 간격 리스트 시간 간격 리스트 ['1m', '5m', '15m','60m','240m','360m','720m','1440m','1w']
        data_types: 데이터 타입 리스트 ['futures', 'spot']
    """
    setup_logging()
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    for data_type in data_types:
        data_type_dir = Path(PROJECT_ROOT) / f'data_{data_type}'
        data_type_dir.mkdir(exist_ok=True)
        
        for interval in intervals:
            str_interval = (f"{interval}" if 'm' in interval else
                          f'{int(interval.replace("h",""))*60}m' if 'h' in interval
                          else f'{int(interval.replace("d",""))*1440}m')
            
            base_dir = Path(f"{data_type_dir}/data_{str_interval}")
            base_dir.mkdir(exist_ok=True)
            
            for i in range(0, len(symbols), BATCH_SIZE):
                symbol_batch = symbols[i:i + BATCH_SIZE]
                
                with ProcessPoolExecutor(max_workers=BATCH_SIZE) as executor:
                    args = [
                        (symbol, interval, base_dir, start_date, end_date, data_type)
                        for symbol in symbol_batch
                    ]
                    list(executor.map(process_symbol, args))
            gc.collect()

def make_unofficial_interval(
    symbols: List[str],
    resample_minutes: int,
    data_type: str
) -> None:
    """비공식 시간 간격의 데이터를 생성합니다.
    
    Args:
        symbols: 심볼 리스트
        resample_minutes: 리샘플링할 분 단위 45분 ->45, 2시간 -> 120
        data_type: 데이터 타입, [data_futures,data_spot]
    """
    def resampler(df: pd.DataFrame, resample_minutes: int = 45) -> pd.DataFrame:
        """데이터프레임을 리샘플링합니다."""
        if not isinstance(df.index, pd.DatetimeIndex):
            df.set_index('datetime', inplace=True)
        
        return df.resample(f'{resample_minutes}min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
    
    for symbol in symbols:
        input_path = Path(f'{data_type}/data_5m/{symbol}.csv')
        df_5m = pd.read_csv(input_path, index_col=0, parse_dates=True)
        
        new_df = resampler(df_5m, resample_minutes=resample_minutes)
        
        output_dir = Path(f'{data_type}/data_{resample_minutes}m')
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f'{symbol}.csv'
        new_df.to_csv(output_path)
        
# 내부 함수

class DataProcessingError(Exception):
    """데이터 처리 중 발생하는 예외를 처리하기 위한 커스텀 예외 클래스"""
    pass

def setup_logging() -> None:
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_last_timestamp(file_path: Path) -> Optional[datetime]:
    """파일에서 마지막 데이터의 timestamp를 가져옵니다.
    
    Args:
        file_path: 데이터 파일 경로
        
    Returns:
        Optional[datetime]: 마지막 타임스탬프 또는 None
    """
    try:
        if file_path.exists():
            df = pd.read_csv(file_path, parse_dates=['datetime'], index_col='datetime')
            return pd.to_datetime(df.index[-1]) if not df.empty else None
    except Exception as e:
        logging.error(f"타임스탬프 읽기 오류 {file_path}: {e}")
    return None

def generate_daily_urls(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    interval: str,
    data_type: str = 'futures'
) -> List[str]:
    """일별 데이터 URL을 생성합니다.
    
    Args:
        symbol: 거래 심볼
        start_date: 시작 날짜
        end_date: 종료 날짜
        interval: 시간 간격
        data_type: 데이터 타입
        
    Returns:
        List[str]: URL 리스트
    """
    base_url = ("https://data.binance.vision/data/spot/daily/klines" 
                if data_type == 'spot' 
                else "https://data.binance.vision/data/futures/um/daily/klines")
    
    urls = []
    if interval == '60m':
        interval = '1h'
    if interval == '240m':
        interval = '4h'
    if interval =='360m':
        interval = '6h'
    if interval =='720m':
        interval = '12h'
    if interval =='1440m':
        interval = '1d'
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        urls.append(f"{base_url}/{symbol}/{interval}/{symbol}-{interval}-{date_str}.zip")
        current_date += timedelta(days=1)
    return urls

def has_header(file_path: Path) -> bool:
    """CSV 파일의 헤더 존재 여부를 확인합니다."""
    try:
        with open(file_path, 'r') as f:
            sniffer = csv.Sniffer()
            sample = ''.join(list(itertools.islice(f, 10)))
            return sniffer.has_header(sample)
    except Exception:
        return False

def download_single_file(args: Tuple[str, Path]) -> bool:
    """단일 파일을 다운로드하고 압축을 해제합니다.
    
    Args:
        args: (url, 추출 디렉토리) 튜플
        
    Returns:
        bool: 성공 여부
    """
    url, extract_dir = args
    try:
        filename = url.split('/')[-1]
        file_path = extract_dir / filename
        
        urlretrieve(url, str(file_path))
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        file_path.unlink()
        return True
    except Exception as e:
        logging.error(f"파일 처리 오류 {url}: {e}")
        return False

def download_and_unzip(urls: List[str], extract_dir: Path) -> None:
    """여러 파일을 병렬로 다운로드하고 압축을 해제합니다."""
    max_workers = min(MAX_WORKERS, len(urls))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        args = [(url, extract_dir) for url in urls]
        list(executor.map(download_single_file, args))

def process_single_file(file_path: Path) -> Optional[pd.DataFrame]:
    """단일 CSV 파일을 처리합니다."""
    try:
        if has_header(file_path):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_csv(file_path, header=None, names=COLUMNS)
        return df
    except Exception as e:
        logging.error(f"파일 읽기 오류 {file_path}: {e}")
        return None
    finally:
        gc.collect()

def merge_data_files(
    extract_dir: Path,
    output_filename: Path,
    existing_df: Optional[pd.DataFrame] = None
) -> None:
    """데이터 파일들을 병합합니다."""
    csv_files = list(extract_dir.glob('*.csv'))
    
    new_df = None
    
    for i in range(0, len(csv_files), BATCH_SIZE):
        batch = csv_files[i:i + BATCH_SIZE]
        df_list = []
        
        for file in batch:
            df = process_single_file(file)
            if df is not None:
                df_list.append(df)
        
        if df_list:
            batch_df = pd.concat(df_list, ignore_index=True)
            new_df = batch_df if new_df is None else pd.concat([new_df, batch_df], ignore_index=True)
            
            del df_list, batch_df
            gc.collect()
    
    if new_df is not None:
        new_df['datetime'] = pd.to_datetime(new_df['open_time'], unit='ms')
        new_df.set_index('datetime', inplace=True)
        new_df = new_df[["open", "high", "low", "close", "volume"]]
        new_df.sort_index(inplace=True)
        
        final_df = (pd.concat([existing_df, new_df]).loc[~pd.concat([existing_df, new_df])
                   .index.duplicated(keep='last')].sort_index()
                   if existing_df is not None else new_df)
            
        final_df.to_csv(output_filename)
    
    # Cleanup
    for file in csv_files:
        try:
            file.unlink()
        except Exception as e:
            logging.error(f"파일 삭제 오류 {file}: {e}")

def process_symbol(args: Tuple[str, str, Path, datetime, datetime, str]) -> bool:
    """단일 심볼에 대한 데이터를 처리합니다."""
    symbol, interval, base_dir, start_date, end_date, data_type = args
    try:
        logging.info(f"처리 중: {symbol} (간격: {interval})")
        output_filename = base_dir / f'{symbol}.csv'
        temp_dir = base_dir / f'temp_dir_{symbol}'
        
        last_timestamp = get_last_timestamp(output_filename)
        if last_timestamp is not None:
            start_date = (last_timestamp + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            logging.info(f"{symbol}: {start_date}부터 재개")
            
            if start_date > end_date:
                logging.info(f"{symbol}: 이미 최신 상태")
                return True
            
            existing_df = pd.read_csv(
                output_filename,
                parse_dates=['datetime'],
                index_col='datetime'
            )
        else:
            existing_df = None
        
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        urls = generate_daily_urls(symbol, start_date, end_date, interval, data_type)
        if urls:
            download_and_unzip(urls, temp_dir)
            merge_data_files(temp_dir, output_filename, existing_df)
            logging.info(f"{symbol} 처리 완료")
        
        if temp_dir.exists():
            for file in temp_dir.iterdir():
                try:
                    file.unlink()
                except Exception:
                    pass
            try:
                temp_dir.rmdir()
            except Exception:
                pass
            
        return True
    except Exception as e:
        logging.error(f"심볼 처리 오류 {symbol}: {e}")
        return False
    finally:
        gc.collect()


