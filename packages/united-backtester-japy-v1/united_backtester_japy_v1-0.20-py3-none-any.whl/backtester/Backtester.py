import backtester

from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Union
from typing import NamedTuple
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import traceback
from pathlib import Path

class OrderType(Enum):
    """
    OrderType
    - market : 포지션 정리시 시장가 주문
    - limit :  포지션 정리시 지정가 주문
    - trailing : 포지션 정리시 트레일링 주문
    """
    MARKET = "market"
    LIMIT = "limit"
    TRAILING = "trailing"

class OrderPositionSide(Enum):
    """
    OrderPositionSide
    - long : 롱 포지션
    - short : 숏 포지션
    """
    LONG = "long"
    SHORT = "short"

class OrderStatus(Enum):
    """
    OrderStatus
    - pending : 주문 대기
    - activated : 주문 활성화
    - filled : 주문 체결
    - canceled : 주문 취소
    """
    PENDING = "pending"
    ACTIVATED = "activated"
    FILLED = "filled"
    CANCELED = "canceled"

class CloseType(Enum):
    """
    CloseType
    - profit : 익절
    - loss : 손절
    """
    TAKE_PROFIT = "profit"
    STOP_LOSS = "loss"
    
class DataRow(NamedTuple):
    """
    DataRow
    - Index : 데이터 인덱스
    - high : 데이터 최고가
    - low : 데이터 최저가
    - close : 데이터 종가
    - open : 데이터 시가
    """
    Index: datetime
    high: float
    low: float
    close: float
    open: float
    

@dataclass
class Order:
    """
    Order
    - order_id : 주문 ID
    - symbol : 종목 심볼
    - position_side : 포지션 사이드
    - order_type : 주문 타입
    - entry_price : 진입 가격
    - entry_time : 진입 시간
    - margin : 마진
    - activated_time : 활성화 시간, activation price 조건 만족시 활성화
    - activation_price : 예약 매수 주문시 사용
    - exit_price : 청산 가격
    - exit_time : 청산 시간
    - close_type : 청산 타입
    - status : 주문 상태
    - limit_price : 리밋 주문 익절가격
    - stop_loss_price : 손절 주문 손절 가격
    
    # 트레일링스탑 관련
    - interval : 루프도는 캔들 interval
    - trailing_stop_activation_price : 트레일링 스탑 주문 활성화 가격
    - trailing_stop_activated_time : 트레일링 스탑 주문 활성화 시간, trailing_stop_activation_price 조건 만족시 활성화
    - callback_rate : 트레일링 스탑 주문 콜백 비율
    - highest_price : 롱 포지션용 최고가
    - lowest_price : 숏 포지션용 최저가
    - metadata : 다양한 조건 필요시 사용하는 용도
    """
    # 기본 주문 정보
    symbol: str
    position_side: OrderPositionSide
    order_type: OrderType
    entry_price: float
    entry_time: datetime
    margin: float
    order_id: Optional[int] = None
    
    # 예약 매수 주문시 사용
    activated_time: Optional[datetime] = None
    activation_price: Optional[float] = None
    
    # 청산 관련 정보
    # 실제 청산 가격
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    close_type: Optional[CloseType] = None
    
    # 주문 상태
    status: OrderStatus = OrderStatus.PENDING
    
    # 리밋 주문 익절가격
    limit_price: Optional[float] = None
    
    # 손절 주문 손절 가격
    stop_loss_price: Optional[float] = None
    
    # 트레일링 주문 관련
    # 루프도는 캔들 interval
    interval: Optional[str] = None
    trailing_stop_activation_price: Optional[float] = None
    trailing_stop_activated_time: Optional[datetime] = None
    callback_rate: Optional[float] = None
    highest_price: Optional[float] = None  # LONG 포지션용
    lowest_price: Optional[float] = None   # SHORT 포지션용
    
    # 다이나믹 데이터 저장용
    metadata: Optional[dict] = None
    
    def check_activation_price(self, row: DataRow) -> bool:
        """
        매수주문 예약 주문 체결 조건 체크
        """
        if self.activation_price is None:
            raise ValueError("check_activation_price err : Activation price is not set")
        return row.low <= self.activation_price <= row.high
    

    def check_stop_loss_conditions(self, row):
        """손절 가격 도달 조건 체크"""
        if self.position_side == OrderPositionSide.LONG:
            return row.low <= self.stop_loss_price
        else:
            return row.high >= self.stop_loss_price
        
        
    def check_limit_price(self, row: DataRow) -> bool:
        """
        limit_price 가격 도달 조건 체크
        """
            
        if self.order_type != OrderType.LIMIT:
            return False
        if self.position_side == OrderPositionSide.LONG:
            return row.high >= self.limit_price
        elif self.position_side == OrderPositionSide.SHORT:
            return row.low <= self.limit_price
        else:
            raise ValueError("Invalid position side")
    
    
    
    def check_trailing_stop_activation_price(self, row: DataRow) -> bool:
        """
        트레일링 스탑 활성화 가격 도달 조건 체크
        """
        
        if self.position_side == OrderPositionSide.LONG:
            return row.high >= self.trailing_stop_activation_price
        else:
            return row.low <= self.trailing_stop_activation_price
        

        
    def check_trailing_stop(self, row: DataRow, df_5m: pd.DataFrame) -> bool:
        """트레일링 스탑 체크
        """
        if self.order_type != OrderType.TRAILING:
            return False
        
        if self.status != OrderStatus.ACTIVATED:
            return False
        
        is_closed=False
        
        # 한캔들내에서 정리되는 경우
        if row.Index == self.trailing_stop_activated_time:
            if self.position_side == OrderPositionSide.LONG:
                if row.high * (1 - self.callback_rate) < row.close:
                    self.limit_price = row.high * (1 - self.callback_rate)
                    self.highest_price = row.high
                    is_closed=False
                else:
                    self.limit_price = row.high * (1 - self.callback_rate)
                    self.highest_price = row.high
                    is_closed=True
            else:
                if row.low * (1 + self.callback_rate) > row.close:
                    self.limit_price = row.low * (1 + self.callback_rate)
                    self.lowest_price = row.low
                    is_closed=False
                else:
                    self.limit_price = row.low * (1 + self.callback_rate)
                    self.lowest_price = row.low
                    is_closed=True
            
        else:
            highest_or_lowest = self.highest_price if self.position_side == OrderPositionSide.LONG else self.lowest_price 
            _highest_or_lowest, is_closed, new_trailing_stop_price = backtester.check_trailing_stop_exit_cond(
                df = df_5m,
                _index = row.Index,
                _position_size = 1 if self.position_side == OrderPositionSide.LONG else -1,
                _highest_or_lowest = highest_or_lowest,
                _profit_price = self.limit_price,
                _callbackrate = self.callback_rate,
                interval = self.interval
            )
            
            if _highest_or_lowest != highest_or_lowest:
                if self.position_side == OrderPositionSide.LONG:
                    self.highest_price = _highest_or_lowest
                else:
                    self.lowest_price = _highest_or_lowest
            if new_trailing_stop_price != self.limit_price:
                self.limit_price = new_trailing_stop_price
        
        return is_closed
            

    def close_order(self, row: DataRow, close_type: CloseType, close_price=None):
        """
        주문 청산 처리
        close_type : 청산 타입
        close_price : 청산 가격, None 일 경우, 주문 타입과 close_type에 따라 자동 청산 가격 설정
        
        """
        if close_price is None:
            if close_type == CloseType.TAKE_PROFIT:
                if self.order_type == OrderType.MARKET:
                    close_price = row.close
                elif self.order_type == OrderType.LIMIT:
                    close_price = self.limit_price
                elif self.order_type == OrderType.TRAILING:
                    close_price = self.limit_price
            elif close_type == CloseType.STOP_LOSS:
                if self.stop_loss_price is not None:
                    close_price = self.stop_loss_price
                else:
                    close_price = row.close
        else:
            close_price = close_price
        
        self.exit_price = close_price
        self.exit_time = row.Index
        self.close_type = close_type
        self.status = OrderStatus.FILLED
        

    def to_trade_record(self) -> dict:
        """거래 기록용 딕셔너리 반환
        - order_id : 주문 ID
        - symbol : 종목 심볼
        - position : 포지션 사이드
        - entry_price : 진입 가격
        - exit_price : 청산 가격
        - close_type : 청산 타입
        - margin : 마진
        - entry_time : 진입 시간
        - activated_time : 활성화 시간
        - exit_time : 청산 시간
        - profit_pct : 수익률
        """
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "position": self.position_side.value,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "close_type": self.close_type.value if self.close_type else None,
            'profit_pct': ((self.exit_price - self.entry_price) / (self.entry_price))* 100 if self.position_side == OrderPositionSide.LONG
                    else ((self.entry_price - self.exit_price) / (self.entry_price))* 100,
            "margin": self.margin if self.margin is not None else 0,
            "entry_time": self.entry_time,
            "activated_time": self.activated_time,
            "exit_time": self.exit_time
        }
        
    def to_dict(self) -> dict:
        """Order 객체의 모든 속성을 딕셔너리로 반환
        - order_id : 주문 ID
        - symbol : 종목 심볼
        - position_side : 포지션 사이드
        - order_type : 주문 타입
        - entry_price : 진입 가격
        - entry_time : 진입 시간
        - interval : 루프도는 캔들 interval
        - margin : 마진
        - activation_price : 예약 매수 주문시 사용
        - activated_time : 활성화 시간
        - exit_price : 청산 가격
        - exit_time : 청산 시간
        - close_type : 청산 타입
        - status : 주문 상태
        - limit_price : 리밋 주문 익절가격
        - stop_loss_price : 손절 주문 손절 가격
        - trailing_stop_activation_price : 트레일링 스탑 주문 활성화 가격
        - trailing_stop_activated_time : 트레일링 스탑 주문 활성화 시간
        - callback_rate : 트레일링 스탑 주문 콜백 비율
        - highest_price : 롱 포지션용 최고가
        - lowest_price : 숏 포지션용 최저가
        """
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "position_side": self.position_side.value,
            "order_type": self.order_type.value,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "interval": self.interval,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time,
            "close_type": self.close_type.value if self.close_type else None,
            "status": self.status.value,
            "margin": self.margin if self.margin is not None else 0,
            "limit_price": self.limit_price,
            "activation_price": self.activation_price,
            "trailing_stop_activation_price": self.trailing_stop_activation_price,
            "callback_rate": self.callback_rate,
            "highest_price": self.highest_price,
            "lowest_price": self.lowest_price,
            "activated_time": self.activated_time
        }


class BacktesterABS(ABC):
    """
    백테스트 추상 클래스
    - test_id : 테스트 ID, 파일 저장 시 사용
    - symbol : 종목 심볼
    - test_start_date : 테스트 시작 날짜, YYYY-MM-DD 형식
    - test_end_date : 테스트 종료 날짜, YYYY-MM-DD 형식
    - interval : 캔들 interval, 1m, 5m, 15m, 30m, 60m, 240m, 1440m,1w 등
    - data_type : 데이터 타입, futures, spot
    - params : 커스텀 파라미터 필요한 경우 params에 묶어서 set_params 함수에 전달
    - pyramiding : 한 포지션에 최대 오픈 가능 주문수, default 1
    - leverage : 레버리지, default 1
    - slippage : 슬리피지, default 0.0005
    - ptc : 프로파일 트레이딩 커미션, default 0.0005
    - initial_balance : 초기 자산, default 10000
    - save_trades : 거래 기록 저장 여부, default True
    - plot_results : 결과 그래프 저장 여부, default True
    """
    def __init__(self, test_id, symbol, test_start_date='2023-01-01', test_end_date='2024-06-30', 
                 interval='60m', data_type='futures', params=None ,pyramiding=1, leverage=1, slippage=0.0005, ptc=0.0005,initial_balance=10000,save_trades=True,plot_results=True):
        self.test_id = test_id
        self.symbol = symbol
        self.interval = interval
        self.leverage = leverage
        self.slippage = slippage
        self.ptc = ptc
        self.initial_balance = initial_balance
        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.trade_history = []
        self.active_orders = []
        self.cancel_orders = []
        self.data = None
        self.data_5m = None
        self.data_type = data_type
        self.result = None
        self.params = None
        self.pyramiding = pyramiding
        self.save_trades = save_trades
        self.plot_results = plot_results
        
        # balance 관련
        self.wallet_balance=initial_balance
        self.wallet_balance_with_slippage=initial_balance
        self.margin_balance=initial_balance
        
        self.wallet_balance_list = []
        self.wallet_balance_with_slippage_list = []
        self.margin_balance_list = []
        
        # 포지션 괸련
        self.long_avg_entry_price = 0
        self.long_position_size=0
        self.short_avg_entry_price = 0
        self.short_position_size=0
        self.unrealized_profit=0
        
        # order Id 추가
        self.order_id = 0
        
        self.set_params(params)
        
    def set_test_id(self, test_id):
        """테스트 ID 설정"""
        self.test_id = test_id
        
    def fetch_test_data(self):
        """테스트 데이터 가져오기"""
        self.data = backtester.get_data(self.symbol, self.interval, data_type=self.data_type)
        # 트레일링 스탑 용도
        try:
            self.data_5m = backtester.get_data(self.symbol, '5m', data_type=self.data_type)
        except:
            self.data_5m = None
        
    def check_take_profit_conditions(self, row, order: Order):
        """조건으로 인한 익절시 사용, 마켓주문에만 적용됨
        EX 마켓주문에서 골든 크로스 일 때 익절인 경우 -> 청산가는 ROW의 CLOSE가 된다."""
        pass

    def check_loss_conditions(self, row, order: Order):
        """조건으로 인한 손절시 사용, 모든 주문에 적용됨
        EX 데드 크로스 일 때 손절인 경우 -> 청산가는 ROW의 CLOSE가 된다."""
        pass
    
    def check_cancel_conditions(self, row, order: Order):
        """order status가 pedding인 주문에 대해서 취소 조건 체크
        """
        pass
    
    def add_trade_record(self, trade):
        """거래 기록 추가"""
        self.trade_history.append(trade)

    def save_results(self):
        """결과 저장"""
        results_df = pd.DataFrame(self.result)
        result_path = f'{self.test_id}_results.csv'
        results_df.to_csv(result_path,index=False)
        backtester.merge_csv_to_excel(self.test_id,result_path)
        
    def prepare_for_backtest(self):
        """백테스트 실행 전 준비"""
        self.trade_history = []
        self.fetch_test_data()
        self.set_indicators()
        self.set_entry_signal()

        if self.test_start_date:
            self.data = self.data.loc[self.test_start_date:]
            if self.data_5m is not None:
                self.data_5m = self.data_5m.loc[self.test_start_date:]
        if self.test_end_date:
            self.data = self.data.loc[:self.test_end_date]
            if self.data_5m is not None:
                self.data_5m = self.data_5m.loc[:self.test_end_date]
                
    def update_avg_entry_price(self, position_size, avg_entry_price, position_side):
        """포지션 평균 진입 가격 업데이트"""
        if position_side == OrderPositionSide.LONG:
            self.long_avg_entry_price = (self.long_avg_entry_price * self.long_position_size + avg_entry_price * position_size) / (self.long_position_size + position_size)
            self.long_position_size += position_size
        elif position_side == OrderPositionSide.SHORT:
            self.short_avg_entry_price = (self.short_avg_entry_price * self.short_position_size + avg_entry_price * position_size) / (self.short_position_size + position_size)
            self.short_position_size += position_size
        else:
            raise ValueError("update_avg_entry_price err : Invalid position side")
        
    def update_wallet_balance(self,order):
        """주문 청산 후 자산 업데이트"""
        order_dict = order.to_trade_record()
        profit = (order_dict['profit_pct'] - 200*self.ptc)/100 * order_dict['margin']
        self.wallet_balance += profit
        
    def update_wallet_balance_with_slippage(self,order):
        """주문 청산 후 자산 업데이트, 슬리피지 적용"""
        if self.wallet_balance_with_slippage < 0:
            return
        order_dict = order.to_trade_record()
        profit = (order_dict['profit_pct'] - (200*self.ptc + 100*self.slippage))/100 * order_dict['margin']
        self.wallet_balance_with_slippage += profit
        
    def change_position_size(self,position_size, position_side):
        """포지션 사이즈 변경"""
        if position_side == OrderPositionSide.LONG:
            self.long_position_size -= position_size
        else:
            self.short_position_size -= position_size
            
    def update_unrealized_profit(self,row):
        """포지션 청산 후 자산 업데이트"""
        long_profit=0
        short_profit=0
        if self.long_position_size != 0:
            long_profit = (row.close - self.long_avg_entry_price)/ self.long_avg_entry_price * self.long_position_size
        if self.short_position_size != 0:
            short_profit = (self.short_avg_entry_price - row.close)/ self.short_avg_entry_price * self.short_position_size
            
        self.unrealized_profit = long_profit + short_profit
        
    def close_order(self,order:Order,row:DataRow, close_type:CloseType, close_price):
        """주문 청산"""
        order.close_order(row, close_type, close_price)
        self.add_trade_record(order)
        self.update_wallet_balance(order)
        self.update_wallet_balance_with_slippage(order)
        self.change_position_size(order.margin,order.position_side)
        self.update_unrealized_profit(row)
    
    def create_order(self, order:Order):
        """주문 생성"""
        # 돈이 없는 경우 진입 못하도록 수정
        if self.margin_balance * self.leverage < order.margin:
            return
        
        # 피라미딩 조건 체크
        if order.status == OrderStatus.ACTIVATED:
            if self.check_pyramiding(order.position_side):
                return
        
        order.order_id = self.order_id
        self.order_id += 1
        self.active_orders.append(order)
        if order.status == OrderStatus.ACTIVATED:
            self.update_avg_entry_price(order.margin, order.entry_price,order.position_side)
            
    def process_order(self, row: DataRow):
        """주문 처리 로직
        1. 예약 매수 주문 체결 조건 체크
        2. 예약 주문 취소 체결 조건 체크
        3. 트레일링스탑 주문이 아닌경우
         3-1. order 정보에 limit price가 있는 경우 주문 체결 조건 체크
         3-2. order 정보에 stop loss price가 있는 경우 주문 체결 조건 체크
         3-3. 손절 조건 체크(모든 주문에 적용)
         3-4. 익절 조건 체크(마켓 주문만 해당)
        4. 트레일링스탑 주문인 경우
         4-1. 트레일링스탑 주문 활성화 조건 체크
         4-2. 트레일링스탑 주문 손절 조건 체크(활성화 전에만 해당됨)
         4-3. 트레일링스탑 주문 익절 조건 체크(활성화 후에만 해당됨)
        """
        remove_orders = []
        close_position=False
        for order in self.active_orders:
            if row.Index != order.entry_time:
                
                if order.status == OrderStatus.PENDING:
                    # 예약 매수 주문 체결 조건 체크
                    if order.check_activation_price(row):
                        if self.check_pyramiding(order.position_side):
                            order.status = OrderStatus.CANCELED
                            self.active_orders.remove(order)
                            self.cancel_orders.append(order)
                            continue
                        
                        order.status = OrderStatus.ACTIVATED
                        order.activated_time = row.Index
                        self.update_avg_entry_price(order.margin, order.entry_price,order.position_side)
                    else:
                        # 예약 주문 취소 체결 조건 체크
                        if self.check_cancel_conditions(row, order):
                            order.status = OrderStatus.CANCELED
                            self.active_orders.remove(order)
                            self.cancel_orders.append(order)
                    continue
                            
                if order.status == OrderStatus.ACTIVATED:
                    # 트레일링스탑 주문이 아닌경우
                    if order.order_type != OrderType.TRAILING:
                        # limit price가 있는 경우 주문 체결 조건 체크
                        if order.limit_price is not None:
                            if order.check_limit_price(row):
                                self.close_order(order,row,CloseType.TAKE_PROFIT,order.limit_price)
                                remove_orders.append(order)
                                continue
                        
                        # stop loss price가 있는 경우 주문 체결 조건 체크
                        if order.stop_loss_price is not None:
                            if order.check_stop_loss_conditions(row):
                                self.close_order(order,row,CloseType.STOP_LOSS,order.stop_loss_price)
                                remove_orders.append(order)
                                continue
                            
                        # 손절 조건 체크(모든 주문에 적용)
                        if self.check_loss_conditions(row,order):
                            self.close_order(order,row,CloseType.STOP_LOSS,row.close)
                            remove_orders.append(order)
                            continue
                        
                        # 익절 조건 체크(마켓 주문만 해당)
                        if order.order_type == OrderType.MARKET and self.check_take_profit_conditions(row,order):
                            self.close_order(order,row,CloseType.TAKE_PROFIT,row.close)
                            remove_orders.append(order)
                            continue
                        continue
                        
                    
                    # 트레일링스탑
                    else:
                        # 트레일링스탑 주문 활성화 조건 체크
                        if order.trailing_stop_activated_time is None:
                            if order.check_trailing_stop_activation_price(row):
                                order.trailing_stop_activated_time = row.Index
                                order.highest_price = row.high
                                order.lowest_price = row.low
                                order.limit_price = row.high * (1 + order.callback_rate) if position_side == OrderPositionSide.LONG else row.low * (1 - order.callback_rate)
                            else:
                                # 트레일링스탑 주문 손절 조건 체크(활성화 전에만 해당됨)
                                if order.stop_loss_price is not None:
                                    if order.check_stop_loss_conditions(row):
                                        self.close_order(order,row,CloseType.STOP_LOSS,order.stop_loss_price)
                                        remove_orders.append(order)
                                        continue
                                # 손절 조건 체크(모든 주문에 적용)
                                if self.check_loss_conditions(row,order):
                                    self.close_order(order,row,CloseType.STOP_LOSS,row.close)
                                    remove_orders.append(order)
                                    continue
                                
                        # 트레일링스탑 주문 익절 조건 체크(활성화 후에만 해당됨)
                        if order.trailing_stop_activated_time is not None:
                            if order.check_trailing_stop(row, self.data_5m):
                                self.close_order(order,row,CloseType.TAKE_PROFIT,order.limit_price)
                                remove_orders.append(order)
                                continue
                

        for order in remove_orders:
            self.active_orders.remove(order)
        
        position_clear_cond = True
        for order in self.active_orders:
            if order.status == OrderStatus.ACTIVATED:
                position_clear_cond = False
                break
            
        if position_clear_cond:
            self.long_avg_entry_price = 0
            self.short_avg_entry_price = 0
            self.long_position_size = 0
            self.short_position_size = 0
            
    def check_pyramiding(self, position_side: OrderPositionSide):
        """포지션별 활성화된 주문 수 조회
        피라미딩 조건 체크 시 사용"""
        long_order_num = 0
        short_order_num = 0
        for order in self.active_orders:
            if order.position_side == OrderPositionSide.LONG and order.status == OrderStatus.ACTIVATED:
                long_order_num += 1
            elif order.position_side == OrderPositionSide.SHORT and order.status == OrderStatus.ACTIVATED:
                short_order_num += 1

        if position_side == OrderPositionSide.LONG:
            return long_order_num >= self.pyramiding
        elif position_side == OrderPositionSide.SHORT:
            return short_order_num >= self.pyramiding
        return True
    
    def is_liquidated(self):
        """청산된 경우 테스트 종료"""
        
        if self.margin_balance <= 0:
            self.wallet_balance = 0
            self.wallet_balance_with_slippage = 0
            self.margin_balance = 0
            self.wallet_balance_list.append(self.wallet_balance)
            self.wallet_balance_with_slippage_list.append(self.wallet_balance_with_slippage)
            self.margin_balance_list.append(self.margin_balance)            
            return True
        return False
    
    def run_backtest(self):
        """백테스트 실행 메인 로직"""
        self.prepare_for_backtest()
        # 백테스트 실행 로직 구현
        for row in self.data.itertuples():
            
            if self.is_liquidated():
                continue
            
            if len(self.active_orders) > 0:
                self.process_order(row)
                
            long_signal, short_signal = self.check_entry_signals(row)
            if long_signal:
                self.open_position(row, OrderPositionSide.LONG)
            elif short_signal:
                self.open_position(row, OrderPositionSide.SHORT)

                
            self.wallet_balance_list.append(self.wallet_balance)
            self.wallet_balance_with_slippage_list.append(self.wallet_balance_with_slippage)
            self.update_unrealized_profit(row)
            self.margin_balance = self.wallet_balance + self.unrealized_profit
            self.margin_balance_list.append(self.margin_balance)
            
        try:
            self.data['wallet_balance'] = self.wallet_balance_list
            self.data['wallet_balance_with_slippage'] = self.wallet_balance_with_slippage_list
            self.data['margin_balance'] = self.margin_balance_list
            self.analyze_trade_history()
        except Exception as e:
            traceback.print_exc()
            print(f'wallet update error: {e}')
    
    def set_params(self, params):
        """
        전략 파라미터 설정
        self.params = params
        if params:
            self.signal_var = params[0]
            self.blackflag_atr_period, self.blackflag_atr_factor, self.blackflag_interval = params[1]
            self.supertrend_atr_period, self.supertrend_multiplier, self.supertrend_interval = params[2]
            self.time_loss_var = params[3]
        이런식으로 필요한 파라미터 설정하여 set_indicators, set_entry_signal 함수에서 사용
        """
        pass

    def set_indicators(self):
        """
        지표 설정 로직을 구현해야 합니다.
        예: RSI, MACD, 볼린저밴드 등의 기술적 지표
        self.data['indicator'] 컬럼에 지표 값 저장 1 or 0 or -1
        """
        pass

    def set_entry_signal(self):
        """
        진입 조건 설정 로직을 구현해야 합니다.
        self.data['signal'] 컬럼에 시그널 값 저장 1 or 0 or -1
        """
        pass

    def check_entry_signals(self, row):
        """진입 시그널 체크 로직을 구현해야 합니다
        Ex row.signal = 1 이면 long_signal = True, row.signal = -1 이면 short_signal = True"""
        long_signal = False
        short_signal = False
        return long_signal, short_signal
    
    @abstractmethod
    def open_position(self, row, position_side: OrderPositionSide):
        """포지션 진입 로직을 구현해야 합니다
        
        -예시
        
        import backtester as bt
        
        order에 필요한 마진 설정
        base_margin =self.wallet_balance * self.leverage
        if base_margin <= 0:
            return
            
            
        -마켓오더 주문 예시
        order_market = bt.Order(
            symbol=self.symbol,
            position_side=position_side,
            order_type=bt.OrderType.MARKET,
            margin=base_margin,
            entry_price=row.close,
            status=bt.OrderStatus.ACTIVATED,
            entry_time=row.Index,
            interval=self.interval
        )
        self.create_order(order_market)
        
        -리밋 주문 예시
        limit_price = row.close * 1.001
        order_limit = bt.Order(
            symbol=self.symbol,
            position_side=position_side,
            order_type=bt.OrderType.LIMIT,
            margin=base_margin,
            entry_price=row.close,
            limit_price=limit_price,
            status=bt.OrderStatus.ACTIVATED,
            entry_time=row.Index,
            interval=self.interval
        )
        self.create_order(order_limit)
        
        -트레일링스탑 주문 예시
        trailing_stop_activation_price = row.close * 1.05
        order_trailing_stop = bt.Order(
            symbol=self.symbol,
            position_side=position_side,
            order_type=bt.OrderType.TRAILING,
            margin=base_margin,
            entry_price=row.close,
            status=bt.OrderStatus.ACTIVATED,
            trailing_stop_activation_price=trailing_stop_activation_price,
            entry_time=row.Index,
            interval=self.interval,
            callback_rate=0.005
        )
        self.create_order(order_trailing_stop)
        
        -> 예약 주문시, status = bt.OrderStatus.PENDING 으로 설정
        -> 예약 주문시, activation_price 설정(롱인 경우 현재 가격보다 낮아야함)
        -> 예약 주문시, entry_price 는 activation_price 로 설정
        """
        pass

    def analyze_trade_history(self):
        """거래 기록 분석 """
        trade_history = [i.to_trade_record() for i in self.trade_history]
        result = backtester.analyze_trade_history(
            trade_history, self.data, self.symbol,
            save_trades=self.save_trades,
            leverage=self.leverage,
            pyramiding=self.pyramiding,
            params=self.params if self.params is not None else {}
        )
        if self.plot_results:
            self.plot_results_and_save()
        self.result=result
        
    def plot_results_and_save(self):
        """결과 그래프 그리기"""
        margin_data = self.data[['margin_balance','wallet_balance',
                                'wallet_balance_with_slippage','close']].copy()
        
                # 2) 인덱스가 DatetimeIndex 인지 확인 (필수!)
        margin_data.index = pd.to_datetime(margin_data.index)

        # 3) ‘일’ 단위로 리샘플해 평균값 계산
        daily_data = margin_data.resample('D').last()


        # 5) 시각화 ── 깔끔한 스타일 적용
        plt.style.use('ggplot')
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 첫 번째 y축 (좌측) → wallet 관련
        ax1.plot(daily_data.index,
                daily_data['wallet_balance'],
                label='Wallet Balance',
                linewidth=2)

        ax1.plot(daily_data.index,
                daily_data['wallet_balance_with_slippage'],
                label='Wallet Balance (Slippage)',
                linewidth=2)
        
        ax1.plot(daily_data.index,
                daily_data['margin_balance'],
                label='Margin Balance',
                linewidth=2)

        ax1.set_ylabel('Wallet Balance (USDT)', fontsize=12)
        ax1.set_xlabel('Date', fontsize=12)
        ax1.tick_params(axis='y')
        ax1.grid(alpha=0.3)

        # 두 번째 y축 (우측) → close
        ax2 = ax1.twinx()
        ax2.plot(daily_data.index,
                daily_data['close'],
                label='Close Price',
                color='blue', linestyle='--', linewidth=2)
        ax2.set_ylabel('Close Price (USDT)', fontsize=12)
        ax2.tick_params(axis='y')

        # 제목 및 범례
        fig.suptitle(f'{self.symbol} {self.interval} – Daily Wallet Balance & Price', fontsize=14)

        # 범례 합치기 (두 축의 라벨을 같이 표시)
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc='upper left')

        plt.tight_layout()

        # 6) 파일 저장 (폴더 자동 생성)
        out_path = Path('result_plot') / f'{self.symbol}_test_id_{self.test_id}.png'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=300)
        plt.close()
        


class BacktesterABS_v2(ABC):
    """
    백테스트 추상 클래스
    - test_id : 테스트 ID, 파일 저장 시 사용
    - symbols : 종목 심볼 리스트
    - test_start_date : 테스트 시작 날짜, YYYY-MM-DD 형식
    - test_end_date : 테스트 종료 날짜, YYYY-MM-DD 형식
    - data_type : 데이터 타입, futures, spot
    - params : 커스텀 파라미터 필요한 경우 params에 묶어서 set_params 함수에 전달
    - pyramiding : 한 포지션에 최대 오픈 가능 주문수, default 1
    - leverage : 레버리지, default 1
    - slippage : 슬리피지, default 0.0005
    - ptc : 프로파일 트레이딩 커미션, default 0.0005
    - initial_balance : 초기 자산, default 10000
    - save_trades : 거래 기록 저장 여부, default True
    - plot_results : 결과 그래프 저장 여부, default True
    """
    def __init__(self, test_id, symbols, test_start_date='2023-01-01', test_end_date='2024-06-30', 
                data_type='futures', params=None ,pyramiding=1, leverage=1, slippage=0.0005, ptc=0.0005,initial_balance=10000,save_trades=True,plot_results=True):
        self.test_id = test_id
        self.symbols = symbols
        self.leverage = leverage
        self.slippage = slippage
        self.ptc = ptc
        self.initial_balance = initial_balance
        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.trade_history = []
        self.active_orders = []
        self.cancel_orders = []
        self.data = None
        self.data_type = data_type
        self.result = None
        self.params = None
        self.pyramiding = pyramiding
        self.save_trades = save_trades
        self.plot_results = plot_results
        
        # balance 관련
        self.wallet_balance=initial_balance
        self.wallet_balance_with_slippage=initial_balance
        self.margin_balance=initial_balance
        
        self.wallet_balance_list = []
        self.wallet_balance_with_slippage_list = []
        self.margin_balance_list = []
        
        # 포지션 괸련
        self.long_avg_entry_price = {}
        self.long_position_size={}
        self.short_avg_entry_price = {}
        self.short_position_size={}
        self.unrealized_profit=0
        
        # 시그널 관련
        self.signals = None
        
        # 데이터 구조 numpy 키워드 저장
        self.base_feats   = ['open', 'high', 'low', 'close', 'volume']
        self.indicator_map = {} 
        self.feature_order = list(self.base_feats)
        
        # order Id 추가
        self.order_id = 0
        
        self.set_params(params)
        
        # 시그널 만들기
        self.dtype_signal = np.dtype([
            ('ts'      , 'int64'),   # timestamp index
            ('sym_id'   , 'int16'),   # sym2idx 의 정수 ID
            ('type'     , 'i1'   ),   # 0=long, 1=short …
            ('meta'     , 'i1'   ),   # 메타 데이터
        ])
        
    def set_test_id(self, test_id):
        """테스트 ID 설정"""
        self.test_id = test_id
        
    def fetch_test_data(self):
        """테스트 데이터 가져오기"""
        dataframes_to_concat = []
        for symbol in self.symbols:
            data = backtester.get_data(symbol, '1m', data_type=self.data_type)
            # 필요한 컬럼만 선택하고 MultiIndex 컬럼명 설정
            symbol_df = data[['open', 'high', 'low', 'close', 'volume']].copy()
            symbol_df.columns = pd.MultiIndex.from_product([[symbol], ['open', 'high', 'low', 'close', 'volume']], 
                                                        names=['symbol', 'ohlcv'])
            dataframes_to_concat.append(symbol_df)
            
        self.data = pd.concat(dataframes_to_concat, axis=1)
        symbols= self.data.columns.levels[0].tolist()
        self.sym2idx = {sym: i for i, sym in enumerate(symbols)}
        self.idx2sym = {v: k for k, v in self.sym2idx.items()}
        
        # self.set_data_to_numpy_array()
        
    def set_data_to_numpy_array(self):  
        """데이터를 numpy array로 변환"""
        combined_df = self.data.copy()
        time_ns = combined_df.index.tz_convert('UTC').view('int64')
        symbols       = combined_df.columns.levels[0].tolist()
        T             = len(combined_df)
        N             = len(symbols)
        F             = len(self.feature_order)
        
        wide = (
            combined_df
            .swaplevel(axis=1)            # → level-0 = ohlc, level-1 = symbol
            .loc[:, self.feature_order]        # 원하는 순서
        )
        # ② 바로 3-D 뷰로 전환 (copy=False → zero-copy)
        ohlc_arr = wide.to_numpy('float32', copy=False).reshape(T, F, N)
        # shape: (time, feature, symbol)
        # ③ 접근 도우미
        sym2idx = {sym: i for i, sym in enumerate(symbols)}
        f2idx   = {f:  j for j, f   in enumerate(self.feature_order)}
        
        self.ohlc_arr = ohlc_arr
        self.sym2idx = sym2idx
        self.f2idx = f2idx
        self.time_ns = time_ns
        self.T = T
        
    def check_take_profit_conditions(self, row, order: Order):
        """조건으로 인한 익절시 사용, 마켓주문에만 적용됨
        EX 마켓주문에서 골든 크로스 일 때 익절인 경우 -> 청산가는 ROW의 CLOSE가 된다."""
        pass

    def check_loss_conditions(self, row, order: Order):
        """조건으로 인한 손절시 사용, 모든 주문에 적용됨
        EX 데드 크로스 일 때 손절인 경우 -> 청산가는 ROW의 CLOSE가 된다."""
        pass
    
    def check_cancel_conditions(self, row, order: Order):
        """order status가 pedding인 주문에 대해서 취소 조건 체크
        """
        pass
    
    def add_trade_record(self, trade):
        """거래 기록 추가"""
        self.trade_history.append(trade)

    def save_results(self):
        """결과 저장"""
        results_df = pd.DataFrame(self.result)
        result_path = f'{self.test_id}_results.csv'
        results_df.to_csv(result_path,index=False)
        backtester.merge_csv_to_excel(self.test_id,result_path)
        
    def prepare_for_backtest(self):
        """백테스트 실행 전 준비"""
        self.trade_history = []
        self.fetch_test_data()
        for symbol in self.symbols:
            self.set_indicators(symbol)
            self.set_entry_signal(symbol)
        # 시그널 시간순으로 정리
        if self.signals is not None:
            self.signals.sort(order='ts')
        # signal 관련 변수 추가
        self.sig_ptr = 0
        self.sig_len   = len(self.signals) if self.signals is not None else 0
        if self.test_start_date:
            self.data = self.data.loc[self.test_start_date:]
        if self.test_end_date:
            self.data = self.data.loc[:self.test_end_date]
        self.set_data_to_numpy_array()

                
    def update_avg_entry_price(self, position_size, avg_entry_price, position_side, symbol):
        """포지션 평균 진입 가격 업데이트"""
        if position_side == OrderPositionSide.LONG:
            self.long_avg_entry_price[symbol] = (self.long_avg_entry_price[symbol] * self.long_position_size[symbol] + avg_entry_price * position_size) / (self.long_position_size[symbol] + position_size)
            self.long_position_size[symbol] += position_size
        elif position_side == OrderPositionSide.SHORT:
            self.short_avg_entry_price[symbol] = (self.short_avg_entry_price[symbol] * self.short_position_size[symbol] + avg_entry_price * position_size) / (self.short_position_size[symbol] + position_size)
            self.short_position_size[symbol] += position_size
        else:
            raise ValueError("update_avg_entry_price err : Invalid position side")
        
    def update_wallet_balance(self,order):
        """주문 청산 후 자산 업데이트"""
        order_dict = order.to_trade_record()
        profit = (order_dict['profit_pct'] - 200*self.ptc)/100 * order_dict['margin']
        self.wallet_balance += profit
        
    def update_wallet_balance_with_slippage(self,order):
        """주문 청산 후 자산 업데이트, 슬리피지 적용"""
        if self.wallet_balance_with_slippage < 0:
            return
        order_dict = order.to_trade_record()
        profit = (order_dict['profit_pct'] - (200*self.ptc + 100*self.slippage))/100 * order_dict['margin']
        self.wallet_balance_with_slippage += profit
        
    def change_position_size(self,position_size, position_side, symbol):
        """포지션 사이즈 변경"""
        min_position_size = 1 # usdt 기준, 계산 오차를 고려해 1이하면 0으로 처리
        if position_side == OrderPositionSide.LONG:
            self.long_position_size[symbol] -= position_size
            if self.long_position_size[symbol] < min_position_size:
                self.long_position_size[symbol] = 0
                self.long_avg_entry_price[symbol] = 0
        else:
            self.short_position_size[symbol] -= position_size
            if self.short_position_size[symbol] < min_position_size:
                self.short_position_size[symbol] = 0
                self.short_avg_entry_price[symbol] = 0
            
    def update_unrealized_profit(self,row):
        """포지션 청산 후 자산 업데이트"""
        long_profit=0
        short_profit=0
        
        for symbol in self.symbols:
            sym_id = self.get_symbol_id(symbol)
            if self.long_position_size.get(symbol, 0) != 0:
                long_profit += (row[self.f2idx['close'],sym_id] - self.long_avg_entry_price[symbol])/ self.long_avg_entry_price[symbol] * self.long_position_size[symbol]
            if self.short_position_size.get(symbol, 0) != 0:
                short_profit += (self.short_avg_entry_price[symbol] - row[self.f2idx['close'],sym_id])/ self.short_avg_entry_price[symbol] * self.short_position_size[symbol]
            
        self.unrealized_profit = long_profit + short_profit
        
    def close_order(self,order:Order,row, close_type:CloseType, close_price=None):
        """주문 청산"""
        order.close_order(row, close_type, close_price)
        self.add_trade_record(order)
        self.update_wallet_balance(order)
        self.update_wallet_balance_with_slippage(order)
        self.change_position_size(order.margin,order.position_side,order.symbol)
    
    def create_order(self, order:Order):
        """주문 생성"""
        # 돈이 없는 경우 진입 못하도록 수정
        if self.margin_balance * self.leverage < order.margin:
            return
        
        # 피라미딩 조건 체크
        if order.status == OrderStatus.ACTIVATED:
            if self.check_pyramiding(order.position_side):
                return
        
        order.order_id = self.order_id
        self.order_id += 1
        self.active_orders.append(order)
        if order.status == OrderStatus.ACTIVATED:
            self.update_avg_entry_price(order.margin, order.entry_price,order.position_side,order.symbol)
            
    def process_order(self, row):
        """주문 처리 로직
        1. 예약 매수 주문 체결 조건 체크
        2. 예약 주문 취소 체결 조건 체크
        3. 트레일링스탑 주문이 아닌경우
         3-1. order 정보에 limit price가 있는 경우 주문 체결 조건 체크
         3-2. order 정보에 stop loss price가 있는 경우 주문 체결 조건 체크
         3-3. 손절 조건 체크(모든 주문에 적용)
         3-4. 익절 조건 체크(마켓 주문만 해당)
        4. 트레일링스탑 주문인 경우
         4-1. 트레일링스탑 주문 활성화 조건 체크
         4-2. 트레일링스탑 주문 손절 조건 체크(활성화 전에만 해당됨)
         4-3. 트레일링스탑 주문 익절 조건 체크(활성화 후에만 해당됨)
        """
        remove_orders = []
        close_position=False
        for order in self.active_orders:
            row_to_datarow = self.get_data_row(order.symbol,row)
            if row_to_datarow.Index != order.entry_time:
                
                if order.status == OrderStatus.PENDING:
                    # 예약 매수 주문 체결 조건 체크
                    if order.check_activation_price(row_to_datarow):
                        if self.check_pyramiding(order.position_side):
                            order.status = OrderStatus.CANCELED
                            self.active_orders.remove(order)
                            self.cancel_orders.append(order)
                            continue
                        
                        order.status = OrderStatus.ACTIVATED
                        order.activated_time = row_to_datarow.Index
                        self.update_avg_entry_price(order.margin, order.entry_price,order.position_side,order.symbol)
                    else:
                        # 예약 주문 취소 체결 조건 체크
                        if self.check_cancel_conditions(row_to_datarow, order):
                            order.status = OrderStatus.CANCELED
                            self.active_orders.remove(order)
                            self.cancel_orders.append(order)
                    continue
                            
                if order.status == OrderStatus.ACTIVATED:
                    # 트레일링스탑 주문이 아닌경우
                    if order.order_type != OrderType.TRAILING:
                        # limit price가 있는 경우 주문 체결 조건 체크
                        if order.limit_price is not None:
                            if order.check_limit_price(row_to_datarow):
                                self.close_order(order,row_to_datarow,CloseType.TAKE_PROFIT,order.limit_price)
                                remove_orders.append(order)
                                continue
                        
                        # stop loss price가 있는 경우 주문 체결 조건 체크
                        if order.stop_loss_price is not None:
                            if order.check_stop_loss_conditions(row_to_datarow):
                                self.close_order(order,row_to_datarow,CloseType.STOP_LOSS,order.stop_loss_price)
                                remove_orders.append(order)
                                continue
                            
                        # 손절 조건 체크(모든 주문에 적용)
                        if self.check_loss_conditions(row,order):
                            self.close_order(order,row_to_datarow,CloseType.STOP_LOSS,row_to_datarow.close)
                            remove_orders.append(order)
                            continue
                        
                        # 익절 조건 체크(마켓 주문만 해당)
                        if order.order_type == OrderType.MARKET and self.check_take_profit_conditions(row,order):
                            self.close_order(order,row_to_datarow,CloseType.TAKE_PROFIT,row_to_datarow.close)
                            remove_orders.append(order)
                            continue
                        continue
                        
                    
                    # 트레일링스탑
                    else:
                        # 트레일링스탑 주문 활성화 조건 체크
                        if order.trailing_stop_activated_time is None:
                            if order.check_trailing_stop_activation_price(row_to_datarow):
                                order.trailing_stop_activated_time = row_to_datarow.Index
                                order.highest_price = row_to_datarow.high
                                order.lowest_price = row_to_datarow.low
                                order.limit_price = row_to_datarow.high * (1 + order.callback_rate) if position_side == OrderPositionSide.LONG else row_to_datarow.low * (1 - order.callback_rate)
                            else:
                                # 트레일링스탑 주문 손절 조건 체크(활성화 전에만 해당됨)
                                if order.stop_loss_price is not None:
                                    if order.check_stop_loss_conditions(row):
                                        self.close_order(order,row_to_datarow,CloseType.STOP_LOSS,order.stop_loss_price)
                                        remove_orders.append(order)
                                        continue
                                # 손절 조건 체크(모든 주문에 적용)
                                if self.check_loss_conditions(row_to_datarow,order):
                                    self.close_order(order,row_to_datarow,CloseType.STOP_LOSS,row_to_datarow.close)
                                    remove_orders.append(order)
                                    continue
                                
                        # 트레일링스탑 주문 익절 조건 체크(활성화 후에만 해당됨)
                        if order.trailing_stop_activated_time is not None:
                            if order.check_trailing_stop(row_to_datarow, self.data_5m):
                                self.close_order(order,row_to_datarow,CloseType.TAKE_PROFIT,order.limit_price)
                                remove_orders.append(order)
                                continue
                

        for order in remove_orders:
            self.active_orders.remove(order)
        
        position_clear_cond = True
        for order in self.active_orders:
            if order.status == OrderStatus.ACTIVATED:
                position_clear_cond = False
                break
        # 혹시 작은 값들이 남아서 오류가 발생할 수 있으므로 초기화
        if position_clear_cond:
            for d in (
                self.long_avg_entry_price,
                self.short_avg_entry_price,
                self.long_position_size,
                self.short_position_size,
            ):
                for k in d:
                    d[k] = 0.0          # ← 가장 빠르고 메모리 효율적

            
    def check_pyramiding(self, position_side: OrderPositionSide):
        """포지션별 활성화된 주문 수 조회
        피라미딩 조건 체크 시 사용"""
        long_order_num = 0
        short_order_num = 0
        for order in self.active_orders:
            if order.position_side == OrderPositionSide.LONG and order.status == OrderStatus.ACTIVATED:
                long_order_num += 1
            elif order.position_side == OrderPositionSide.SHORT and order.status == OrderStatus.ACTIVATED:
                short_order_num += 1

        if position_side == OrderPositionSide.LONG:
            return long_order_num >= self.pyramiding
        elif position_side == OrderPositionSide.SHORT:
            return short_order_num >= self.pyramiding
        return True
    
    def is_liquidated(self):
        """청산된 경우 테스트 종료"""
        
        if self.margin_balance <= 0:
            self.wallet_balance = 0
            self.wallet_balance_with_slippage = 0
            self.margin_balance = 0
            self.wallet_balance_list.append(self.wallet_balance)
            self.wallet_balance_with_slippage_list.append(self.wallet_balance_with_slippage)
            self.margin_balance_list.append(self.margin_balance)            
            return True
        return False
    
    def run_backtest(self):
        """백테스트 실행 메인 로직"""
        self.prepare_for_backtest()
        
        # 테스트 데이터보다 이전에 시그널이 있는 경우 pass
        while self.sig_ptr < self.sig_len and self.signals['ts'][self.sig_ptr] < self.time_ns[0]:
            self.sig_ptr += 1

        # 백테스트 실행 로직 구현
        for i in range(self.T):
            row = self.ohlc_arr[i]
            self.ts = self.time_ns[i]
            
            if self.is_liquidated():
                continue
            
            if len(self.active_orders) > 0:
                self.process_order(row)
            
            # 현재 row랑 같은 시간에 발생한 시그널이 있는지 확인하고 진입.
            self.check_entry_signals(self.ts, row)


                
            self.wallet_balance_list.append(self.wallet_balance)
            self.wallet_balance_with_slippage_list.append(self.wallet_balance_with_slippage)
            self.update_unrealized_profit(row)
            self.margin_balance = self.wallet_balance + self.unrealized_profit
            self.margin_balance_list.append(self.margin_balance)
            
        try:
            self.data['wallet_balance'] = self.wallet_balance_list
            self.data['wallet_balance_with_slippage'] = self.wallet_balance_with_slippage_list
            self.data['margin_balance'] = self.margin_balance_list
            self.analyze_trade_history()
        except Exception as e:
            traceback.print_exc()
            print(f'wallet update error: {e}')
    
    def set_params(self, params):
        """
        전략 파라미터 설정
        self.params = params
        if params:
            self.signal_var = params[0]
            self.blackflag_atr_period, self.blackflag_atr_factor, self.blackflag_interval = params[1]
            self.supertrend_atr_period, self.supertrend_multiplier, self.supertrend_interval = params[2]
            self.time_loss_var = params[3]
        이런식으로 필요한 파라미터 설정하여 set_indicators, set_entry_signal 함수에서 사용
        """
        pass

    def add_indicator(self, symbol,interval ,indicator_name,series):
        minute_idx = self.data.index
        ind_vals = (
            series.shift(1).reindex(minute_idx, method='ffill')
            .astype('float32') 
            if interval != '1m' else series
            .reindex(minute_idx, method='ffill')
            .astype('float32')
        )

        # 2) MultiIndex 컬럼에 삽입
        self.data[(symbol, indicator_name)] = ind_vals.values

        # 3) feature 목록 갱신 (심볼마다 같은 이름이면 한 번만 추가)
        if indicator_name not in self.indicator_map:
            fid = len(self.feature_order)
            self.feature_order.append(indicator_name)
            self.indicator_map[indicator_name] = fid
            
    def set_indicators(self, symbol):
        """
        지표 설정 로직을 구현해야 합니다.
        예: RSI, MACD, 볼린저밴드 등의 기술적 지표
        self.data['indicator'] 컬럼에 지표 값 저장 1 or 0 or -1
        """
        df_1h = backtester.get_data(symbol, '60m', data_type=self.data_type)

        # 1) EMA 24 (1h)
        ema24 = df_1h['close'].ewm(span=24, adjust=False).mean()
        self.add_indicator(symbol, '60m','ema24_1h', ema24)
        
    def set_entry_signal(self, symbol):
        """signal 컬럼을 가진 df를 만들고 df를 반환 signal은 0 or 1 or -1 로 설정
        설정할 컬럼, entry_px, limit_px, sl_px, type"""
        pass
    
    def add_entry_signal(self, symbol, interval, signal_df):
        """
        진입 조건 설정 로직을 구현해야 합니다.
        """
        sym_id = self.sym2idx[symbol]
        if signal_df is None:return
        if interval != '1m':
            signal_df['signal'] = signal_df['signal'].shift(1)
        # 시그널 항목을 만들 것
        df_sig = signal_df.loc[signal_df['signal'] != 0].copy()
        
        if df_sig.empty:
            return   
        
        df_sig['row_time'] = (
            df_sig.index
                .tz_convert('UTC')          # ns 정수로 만들기 전 tz-aware 정리
                .view('int64')              # epoch-ns → int64
        )
        df_sig['type'] = (df_sig['signal'] < 0).astype('int8') # 0=long,1=short
        # 시그널 구분이 필요할때 meta 컬럼 만들어서 구별자로 사용
        df_sig['meta'] = df_sig.get('meta', df_sig['type']).astype('int8')
        # 컬럼이 있으면 해당 컬럼, 없으면 close로 대체 후 float32 캐스팅
        k = len(df_sig)
        sig_rec = np.empty(k, dtype=self.dtype_signal)

        sig_rec['ts']      = df_sig['row_time'].to_numpy(copy=False)
        sig_rec['sym_id']   = np.full(k, sym_id, dtype='int16')
        sig_rec['type']     = df_sig['type'].values
        sig_rec['meta']     = df_sig['meta'].values

        # ─ self.signals 에 누적(여러 심볼 지원) ─────────────────────
        if not hasattr(self, 'signals') or self.signals is None:
            self.signals = sig_rec
        else:
            self.signals = np.concatenate([self.signals, sig_rec])
            
        self.long_avg_entry_price[symbol] = 0
        self.long_position_size[symbol] = 0
        self.short_avg_entry_price[symbol] = 0
        self.short_position_size[symbol] = 0
        
    def get_symbol_name(self, sym_id):
        return self.idx2sym[sym_id]
    
    def get_symbol_id(self, symbol):
        return self.sym2idx[symbol]
    
    def get_feature_idx(self, feature_name):
        return self.f2idx[feature_name]
    
    def get_data_row(self, symbol, row):
        return DataRow(
                Index=self.ts,
                open=row[self.f2idx['open'],self.get_symbol_id(symbol)],
                high=row[self.f2idx['high'],self.get_symbol_id(symbol)],
                low=row[self.f2idx['low'],self.get_symbol_id(symbol)],
                close=row[self.f2idx['close'],self.get_symbol_id(symbol)],
            )

    def check_entry_signals(self, ts, row):
        """진입 시그널 체크 로직을 구현해야 합니다
        Ex row.signal = 1 이면 long_signal = True, row.signal = -1 이면 short_signal = True"""
            # 2. === 시그널 처리 ===
        while self.sig_ptr < self.sig_len and self.signals['ts'][self.sig_ptr] == ts:
            s = self.signals[self.sig_ptr]
            position_side  = OrderPositionSide.LONG if s['type'] ==0 else OrderPositionSide.SHORT  # 0 long 1 short
            self.open_position(s, position_side, row)
            self.sig_ptr += 1
    
    @abstractmethod
    def open_position(self, signal, position_side: OrderPositionSide):
        """포지션 진입 로직을 구현해야 합니다
        
        signal -> 
        ([
            ('row'      , 'int64'),   # timestamp index
            ('sym_id'   , 'int16'),   # sym2idx 의 정수 ID
            ('type'     , 'i1'   ),   # 0=long, 1=short …
            ('meta'     , 'i1'   ),   # 메타 데이터
        ])
        """
        pass

    def analyze_trade_history(self):
        """거래 기록 분석 """
        trade_history = [i.to_trade_record() for i in self.trade_history]
        result = backtester.analyze_trade_history_v2(
            trade_history, self.margin_balance_list,
            save_trades=self.save_trades,
            leverage=self.leverage,
            pyramiding=self.pyramiding,
            params=self.params if self.params is not None else {}
        )
        if self.plot_results:
            self.plot_results_and_save()
        self.result=result
        
    def plot_results_and_save(self):
        """결과 그래프 그리기"""
        margin_data = self.data[['margin_balance','wallet_balance',
                                'wallet_balance_with_slippage']].copy()
        
                # 2) 인덱스가 DatetimeIndex 인지 확인 (필수!)
        margin_data.index = pd.to_datetime(margin_data.index)

        # 3) ‘일’ 단위로 리샘플해 평균값 계산
        daily_data = margin_data.resample('D').last()


        # 5) 시각화 ── 깔끔한 스타일 적용
        plt.style.use('ggplot')
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 첫 번째 y축 (좌측) → wallet 관련
        ax1.plot(daily_data.index,
                daily_data['wallet_balance'],
                label='Wallet Balance',
                linewidth=2)

        ax1.plot(daily_data.index,
                daily_data['wallet_balance_with_slippage'],
                label='Wallet Balance (Slippage)',
                linewidth=2)
        
        ax1.plot(daily_data.index,
                daily_data['margin_balance'],
                label='Margin Balance',
                linewidth=2)

        ax1.set_ylabel('Wallet Balance (USDT)', fontsize=12)
        ax1.set_xlabel('Date', fontsize=12)
        ax1.tick_params(axis='y')
        ax1.grid(alpha=0.3)

        # 제목 및 범례
        fig.suptitle(f' test_id: {self.test_id} Daily Wallet', fontsize=14)

        # 범례 합치기 (두 축의 라벨을 같이 표시)
        lines, labels = ax1.get_legend_handles_labels()
        ax1.legend(lines , labels , loc='upper left')

        plt.tight_layout()

        # 6) 파일 저장 (폴더 자동 생성)
        out_path = Path('result_plot') / f'test_id_{self.test_id}.png'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=300)
        plt.close()
        
