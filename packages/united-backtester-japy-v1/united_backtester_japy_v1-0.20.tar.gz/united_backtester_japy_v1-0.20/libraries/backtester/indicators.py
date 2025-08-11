# utils/indicators.py
import pandas as pd
import numpy as np
import pandas_ta as ta
from .data_utils import get_data

# inner function
def standardize_column_names(df):
    """
    데이터프레임의 컬럼명을 소문자로 표준화하는 함수입니다.
    
    Parameters
    ----------
    df : pandas.DataFrame
        표준화할 데이터프레임
        
    Returns
    -------
    pandas.DataFrame
        컬럼명이 표준화된 데이터프레임
    """
    column_mapping = {
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Open': 'open',
        'Volume': 'volume',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'open': 'open',
        'volume': 'volume'
    }
    
    df = df.copy()
    df.columns = [column_mapping.get(col, col.lower()) for col in df.columns]
    return df


def calculate_supertrend(df, multiplier, atr_period=10,return_df=False):
    """
    슈퍼트렌드 지표를 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    multiplier : float
        ATR 승수
    atr_period : int, optional
        ATR 계산 기간, by default 10
    return_df : bool, optional
        True 인 경우 데이터프레임 반환, by default False
    Returns
    -------
    pandas.Series
        슈퍼트렌드 방향을 나타내는 시리즈 (1: 상승추세, -1: 하락추세)
        
    return_df True 인 경우 데이터프레임 반환
    
    """
    df = standardize_column_names(df)
    df['atr'] = ta.atr(high=df['high'], low=df['low'], close=df['close'], length=atr_period)
    df['hl2'] = (df['high'] + df['low']) / 2
    df['up'] = df['hl2'] - (multiplier * df['atr'])
    df['dn'] = df['hl2'] + (multiplier * df['atr'])
    df['supertrend_direction'] = 1  # Initialize trend to 1

    df['up1'] = df['up'].shift(1)
    df['dn1'] = df['dn'].shift(1)
    df['close1'] = df['close'].shift(1)

    for i in range(len(df)):
        if i == 0:
            df.loc[df.index[i], 'up'] = df.loc[df.index[i], 'up']
            df.loc[df.index[i], 'dn'] = df.loc[df.index[i], 'dn']
            df.loc[df.index[i], 'supertrend_direction'] = 1
        else:
            up = df.loc[df.index[i], 'up']
            up1 = df.loc[df.index[i - 1], 'up']
            dn = df.loc[df.index[i], 'dn']
            dn1 = df.loc[df.index[i - 1], 'dn']
            close1 = df.loc[df.index[i - 1], 'close']
            trend_prev = df.loc[df.index[i - 1], 'supertrend_direction']
            
            if close1 > up1:
                df.loc[df.index[i], 'up'] = max(up, up1)
            else:
                df.loc[df.index[i], 'up'] = up

            if close1 < dn1:
                df.loc[df.index[i], 'dn'] = min(dn, dn1)
            else:
                df.loc[df.index[i], 'dn'] = dn

            if trend_prev == -1 and df.loc[df.index[i], 'close'] > dn1:
                df.loc[df.index[i], 'supertrend_direction'] = 1
            elif trend_prev == 1 and df.loc[df.index[i], 'close'] < up1:
                df.loc[df.index[i], 'supertrend_direction'] = -1
            else:
                df.loc[df.index[i], 'supertrend_direction'] = trend_prev
    
    if return_df:
        return df
    else:
        return df['supertrend_direction']

def get_supertrend(symbol, multiplier=4, atr_period=100, interval='60m',start=None, end=None, get_data_type='futures', return_df=False):
    """
    슈퍼트렌드 지표를 계산하여 반환합니다.

    Parameters
    ----------
    symbol : str
        코인 심볼
    multiplier : float
        슈퍼트렌드 계산에 사용되는 ATR 승수
    atr_period : int, optional
        ATR 계산 기간, by default 10
    interval : str, optional
        캔들 간격, by default '60m'
    start : str, optional
        시작 날짜, by default None, format='YYYY-MM-DD'
    end : str, optional
        종료 날짜, by default None, format='YYYY-MM-DD'
    get_data_type : str, optional
        데이터 타입, by default 'futures'
        'futures': 선물 데이터
        'spot': 현물 데이터
        
    return_df : bool, optional
        True 인 경우 데이터프레임 반환, by default False

    Returns
    -------
    pd.Series
        슈퍼트렌드 방향 시리즈 (1: 상승추세, -1: 하락추세)
        
    return_df True 인 경우 데이터프레임 반환
    """
    df = get_data(symbol, interval,start=start,end=end,data_type=get_data_type)
    super_trend = calculate_supertrend(df, multiplier, atr_period,return_df=return_df)
    return super_trend

def calculate_ut_signal(df, atr_period_ut=100, key_Val=2,return_df=False):
    """
    UT 시그널을 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    atr_period_ut : int
        ATR 계산 기간
    key_Val : float
        ATR 승수
        
    return_df : bool, optional
        True 인 경우 데이터프레임 반환, by default False

    Returns
    -------
    pandas.Series
        UT 시그널 시리즈 (1: 매수 신호, -1: 매도 신호, 0: 중립)
        
    return_df True 인 경우 데이터프레임 반환

    Notes
    -----
    - ATR을 이용한 트레일링 스탑을 계산하여 매수/매도 시그널을 생성합니다
    - 가격이 트레일링 스탑을 상향 돌파하면 매수(1), 하향 돌파하면 매도(-1) 시그널이 발생합니다
    - atr_period_ut 기간만큼의 초기 데이터는 NaN 값이 발생합니다
    """
    data = standardize_column_names(df)
    # Calculate ATR
    data['ATR'] = ta.atr(data['high'],data['low'],data['close'],length=atr_period_ut)
    data['nLoss'] = key_Val * data['ATR']

    data['src'] = data['close']

    # Initialize variables
    data['xATRTrailingStop'] = 0.0
    data['pos'] = 0

    # Calculate ATR Trailing Stop
    for i in range(1, len(data)):
        prev_trailing_stop = data['xATRTrailingStop'].iat[i-1]
        prev_src = data['src'].iat[i-1]
        curr_src = data['src'].iat[i]
        nLoss = data['nLoss'].iat[i]

        iff_1 = curr_src - nLoss if curr_src > prev_trailing_stop else curr_src + nLoss
        iff_2 = min(prev_trailing_stop, curr_src + nLoss) if (curr_src < prev_trailing_stop and prev_src < prev_trailing_stop) else iff_1
        data['xATRTrailingStop'].iat[i] = max(prev_trailing_stop, curr_src - nLoss) if (curr_src > prev_trailing_stop and prev_src > prev_trailing_stop) else iff_2
        
        iff_3 = -1 if (prev_src > prev_trailing_stop and curr_src < prev_trailing_stop) else data['pos'].iat[i-1]
        data['pos'].iat[i] = 1 if (prev_src < prev_trailing_stop and curr_src > prev_trailing_stop) else iff_3
        
    # for buy (src > xATRTrailingStop) & (beforde_src < before_xATRTrailingStop)
    data['buy'] = (data['src'] > data['xATRTrailingStop']) & (data['src'].shift(1) < data['xATRTrailingStop'].shift(1))
    # for sell (src < xATRTrailingStop) & (beforde_src > before_xATRTrailingStop)
    data['sell'] = (data['src'] < data['xATRTrailingStop']) & (data['src'].shift(1) > data['xATRTrailingStop'].shift(1))
    data['ut_signal'] = np.where(data['buy'], 1, np.where(data['sell'], -1, 0))
    if return_df:
        return data
    else:
        return data['ut_signal']

def get_ut_signal(symbol, atr_period_ut=100, key_Val=2, interval='60m', start=None, end=None, get_data_type='futures', return_df=False):
    """
    UT 시그널을 계산하는 함수입니다.

    Parameters
    ----------
    symbol : str
        거래 심볼 (예: 'BTCUSDT')
    atr_period_ut : int 
        ATR 계산 기간
    key_Val : float
        ATR 승수
    interval : str, optional
        캔들 간격, by default '60m'
    start : str, optional
        시작 날짜, by default None, format='YYYY-MM-DD'
    end : str, optional
        종료 날짜, by default None, format='YYYY-MM-DD'
    get_data_type : str, optional
        데이터 타입 ('futures' 또는 'spot'), by default 'futures'
        
    return_df : bool, optional
        True 인 경우 데이터프레임 반환, by default False

    Returns
    -------
    pandas.Series
        UT 시그널 시리즈 (1: 매수 신호, -1: 매도 신호, 0: 중립)
        
    return_df True 인 경우 데이터프레임 반환

    Notes
    -----
    - 주어진 심볼에 대한 OHLCV 데이터를 가져와서 UT 시그널을 계산합니다
    - calculate_ut_signal() 함수를 내부적으로 호출하여 시그널을 생성합니다
    """
    data = get_data(symbol, interval,start=start,end=end,data_type=get_data_type)
    data = calculate_ut_signal(data, atr_period_ut, key_Val,return_df=return_df)
    return data


def calculate_blackflag(df, ATRPeriod, ATRFactor=6):
    """
    블랙플래그 지표를 계산하는 함수입니다.
    
    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    ATRPeriod : int
        ATR 계산에 사용할 기간
    ATRFactor : int, optional
        ATR 승수 (기본값: 6)
        
    Returns
    -------
    pandas.Series
        블랙플래그 트렌드 시그널 (-1: 하락, 1: 상승)
    """
    df = standardize_column_names(df)
    df['HiLo'] = np.minimum(df['high'] - df['low'], 
                           1.5 * (df['high'].rolling(window=ATRPeriod).mean() - 
                                 df['low'].rolling(window=ATRPeriod).mean()))
    
    df['HRef'] = np.where(df['low'] <= df['high'].shift(1),
                         df['high'] - df['close'].shift(1),
                         (df['high'] - df['close'].shift(1)) - 
                         0.5 * (df['low'] - df['high'].shift(1)))
    
    df['LRef'] = np.where(df['high'] >= df['low'].shift(1),
                         df['close'].shift(1) - df['low'],
                         (df['close'].shift(1) - df['low']) - 
                         0.5 * (df['low'].shift(1) - df['high']))
    
    df['TrueRange'] = df[['HiLo', 'HRef', 'LRef']].max(axis=1)
    df = df.iloc[ATRPeriod+1:].copy()
    df['Loss'] = ATRFactor * calculate_wilders_ma(df['TrueRange'], ATRPeriod)
    df['Up'] = df['close'] - df['Loss']
    df['Dn'] = df['close'] + df['Loss']
    
    df['TrendUp'] = df['Up']
    df['TrendDown'] = df['Dn']
    df['Trend'] = 1
    before_index=None
    for i, row in df.iterrows():
        if i == df.index[0]:
            before_index=i
            continue  # 첫 번째 행은 건너뜁니다.
        df.loc[i, 'TrendUp'] = max(row['Up'], df.loc[before_index, 'TrendUp']) if df.loc[before_index, 'close'] > df.loc[before_index, 'TrendUp'] else row['Up']
        df.loc[i, 'TrendDown'] = min(row['Dn'], df.loc[before_index, 'TrendDown']) if df.loc[before_index, 'close'] < df.loc[before_index, 'TrendDown'] else row['Dn']
        df.loc[i, 'Trend'] = 1 if row['close'] > df.loc[before_index, 'TrendDown'] else (-1 if row['close'] < df.loc[before_index, 'TrendUp'] else df.loc[before_index, 'Trend'])
        before_index=i
        
    df['Trail'] = np.where(df['Trend'] == 1, df['TrendUp'], df['TrendDown'])

    df['ex'] = df['high']
    for i, row in df.iterrows():
        if i == df.index[0]:
            continue  # 첫 번째 행은 건너뜁니다.
        prev_index = df.index.get_loc(i) - 1
        if df.loc[i, 'Trend'] == 1:
            df.loc[i, 'ex'] = max(df.iloc[prev_index]['ex'], row['high'])
        elif df.loc[i, 'Trend'] == -1:
            df.loc[i, 'ex'] = min(df.iloc[prev_index]['ex'], row['low'])
    return df['Trend']

def get_blackflag(symbol, ATRPeriod, interval='240m', ATRFactor=6, start=None, end=None, get_data_type='futures'):
    """
    블랙플래그 지표를 계산하는 함수입니다.

    Args:
        symbol (str): 거래 심볼 (예: 'BTCUSDT')
        ATRPeriod (int): ATR 계산 기간
        interval (str): 캔들 간격 (예: '240m', '1h', '4h', '1d')
        ATRFactor (float): ATR 승수 (기본값: 6)
        start (str, optional): 데이터 시작 시간 (예: '2023-01-01')
        end (str, optional): 데이터 종료 시간 (예: '2023-12-31')
        get_data_type (str): 데이터 타입 ('futures' 또는 'spot', 기본값: 'futures')

    Returns:
        pandas.Series: 블랙플래그 신호값 (-1: 매도, 1: 매수)
    """
    df = get_data(symbol, interval,start=start,end=end,data_type=get_data_type)
    df['Trend'] = calculate_blackflag(df, ATRPeriod, ATRFactor)
    return df['Trend']


    
def calculate_ichimoku_senkou_a(df, conversion_periods=9, base_periods=26, displacement=26):
    """
    이치모쿠 선행스펜 A를 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    conversion_periods : int, optional
        전환선(Tenkan-sen) 계산 기간, by default 9
    base_periods : int, optional
        기준선(Kijun-sen) 계산 기간, by default 26  
    displacement : int, optional
        선행스팬 이동 기간, by default 26

    Returns
    -------
    pandas.Series
        선행스펜 A 값
    """
    def middle_donchian(high_series, low_series, length):
        """
        중간 동치안 채널 값을 계산
        """
        upper = high_series.rolling(window=length).max()
        lower = low_series.rolling(window=length).min()
        return (upper + lower) / 2
    
    df = standardize_column_names(df)  
    # Tenkan-sen (전환선) 계산
    tenkan = middle_donchian(df['high'], df['low'], conversion_periods)
    
    # Kijun-sen (기준선) 계산
    kijun = middle_donchian(df['high'], df['low'], base_periods)
    
    # Senkou Span A (선행스펜 A) 계산
    senkou_span_a = (tenkan + kijun) / 2
    
    # displacement 적용
    senkou_span_a = senkou_span_a.shift(displacement)
    return senkou_span_a

def get_ichimoku_senkou_a(symbol,interval='60m', conversion_periods=9, base_periods=26, displacement=26, start=None, end=None, get_data_type='futures'):
    """
    이치모쿠 선행스펜 A를 계산하는 함수입니다.

    Parameters:
    ----------
    symbol (str): 거래 심볼 (예: 'BTCUSDT')
    interval (str): 캔들 간격 (예: '60m', '1h', '4h', '1d')
    conversion_periods (int): 전환선(Tenkan-sen) 계산 기간 (기본값: 9)
    base_periods (int): 기준선(Kijun-sen) 계산 기간 (기본값: 26)
    displacement (int): 선행스팬 이동 기간 (기본값: 26)
    start (str, optional): 데이터 시작 시간 (예: '2023-01-01')
    end (str, optional): 데이터 종료 시간 (예: '2023-12-31')
    get_data_type (str): 데이터 타입 ('futures' 또는 'spot', 기본값: 'futures')

    Returns:
        pandas.Series: 선행스펜 A 값
    """
    df = get_data(symbol, interval,start=start,end=end, data_type=get_data_type)
    df['ichimoku_senkou_a'] = calculate_ichimoku_senkou_a(df, conversion_periods, base_periods, displacement)
    return df['ichimoku_senkou_a']
