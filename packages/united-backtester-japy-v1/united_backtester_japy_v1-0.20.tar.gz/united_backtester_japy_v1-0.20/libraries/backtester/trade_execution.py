from datetime import timedelta, datetime
import pandas as pd 
import numpy as np

def record_trade(symbol, position,position_size ,entry_price, exit_price, close_type, entry_time, exit_time):
    """
    거래 기록을 trade_history 리스트에 추가하는 함수
    
    Parameters:
    - symbol: 거래 심볼
    - position: LONG, SHORT
    - position_size: 거래시 가지고 있는 포지션 볼륨
    - entry_price: 진입가격
    - exit_price: 청산가격
    - close_type: 청산 유형 ('take_profit', 'trailing_stop', 'trend_reverse')
    - entry_time: 진입 시간
    - exit_time: 청산 시간
    """
    return {
        'symbol': symbol,
        'position': "LONG" if position == 1 else "SHORT",
        'position_size': position_size,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'close_type': close_type,
        'profit_pct': ((exit_price - entry_price) / (entry_price))* 100 if position == 1
                     else ((entry_price - exit_price) / (entry_price))* 100,
        'entry_time': entry_time,
        'exit_time': exit_time
    }
    

# %%
def check_trailing_stop_exit_cond(df, _index, _position_size, _highest_or_lowest, _profit_price, _callbackrate, interval):

    minutes = int(interval.replace('m', ''))
    start_time = _index
    end_time = _index + timedelta(minutes=minutes -5)
    
    df = df.loc[start_time:end_time].copy()
    new_trailing_stop_price = _profit_price  # 초기값 설정
    for index, row in df.iterrows():
        high = row['high']
        low = row['low']
        open_price = row['open']
        close = row['close']
        positive_candle = close > open_price
        
        if _position_size > 0:
            
            # 양봉일때는 최저가를 먼저 찍었다고 가정
            if positive_candle and low <= new_trailing_stop_price:
                return _highest_or_lowest, True, new_trailing_stop_price
            
            
            # 고가가 업데이트 되었을때 
            if high > _highest_or_lowest:
                    
                _highest_or_lowest = high
                new_trailing_stop_price = _highest_or_lowest * (1 - _callbackrate)  # 새로운 변수에 저장
                # 양봉인경우 종가가 트레일링 스탑 가격보다 낮으면 청산
                if positive_candle and close < new_trailing_stop_price:
                    return _highest_or_lowest, True, new_trailing_stop_price
                # 음봉인경우 저가가 트레일링 스탑 가격보다 낮으면 청산(고가를 먼저 찍었다고 가정)
                elif not positive_candle and low <= new_trailing_stop_price:
                    return _highest_or_lowest, True, new_trailing_stop_price
                else:
                    continue
                
            if low <= new_trailing_stop_price:  # 새로운 변수로 체크
                return _highest_or_lowest, True, new_trailing_stop_price
            
        elif _position_size < 0:
            if not positive_candle and high >= new_trailing_stop_price:
                return _highest_or_lowest, True, new_trailing_stop_price
            # 저가가 업데이트 되었을때
            if low < _highest_or_lowest:
                _highest_or_lowest = low
                new_trailing_stop_price = _highest_or_lowest * (1 + _callbackrate)  # 새로운 변수에 저장
                # 음봉인 경우 종가가 트레일링 스탑 가격보다 높으면 청산
                if not positive_candle and close > new_trailing_stop_price:
                    return _highest_or_lowest, True, new_trailing_stop_price
                # 양봉인경우 고가가 트레일링 스탑 가격보다 높으면 청산(저가를 먼저 찍었다고 가정)
                elif positive_candle and high >= new_trailing_stop_price:
                    return _highest_or_lowest, True, new_trailing_stop_price
                else:
                    continue
            if high >= new_trailing_stop_price:  # 새로운 변수로 체크
                return _highest_or_lowest, True, new_trailing_stop_price
 
    # False 반환 시에도 업데이트된 trailing_stop_price 반환
    return _highest_or_lowest, False, new_trailing_stop_price
# %%
