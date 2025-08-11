# backtester/__init__.py

"""
Backtester

암호화폐 거래 전략을 백테스트하기 위한 프레임워크입니다.

## 모듈 구성

| 카테고리 | 모듈 | 핵심 기능 |
|----------|------|-----------|
| **데이터 유틸리티** | `data_utils` | OHLCV 로드·비공식 봉 생성 |
| **지표** | `indicators` | SuperTrend, UT Bot 등 40+ 지표 |
| **백테스터 핵심** | `Backtester` | 주문·손익·리포트 엔진 |

"""

"""
데이터를 가져오고, 비공식 봉을 만드는 함수들입니다.
"""
## 데이터 유틸리티
from .data_utils import (
    get_data,
    generate_data_for_backtest,
    make_unofficial_interval,
)

"""
트레이딩뷰에 있는 지표 계산 함수들입니다. 조금씩 업데이트 예정.
간단한 계산은 pandas_ta를 사용하세요.
"""
from .indicators import (
    # Outer functions
    calculate_supertrend,
    get_supertrend,
    calculate_ut_signal,
    get_ut_signal,
    calculate_blackflag,
    get_blackflag,
    calculate_ichimoku_senkou_a,
    get_ichimoku_senkou_a,
)

"""
백테스트 결과를 분석하고, 엑셀로 정리하는 함수들입니다.
"""
from .trade_analysis import (
    analyze_trade_history,
    analyze_trade_history_v2,
    analyze_trade_history_for_vector,
    merge_csv_to_excel
)

"""
백테스트에 필요한 트레이딩 함수들입니다.
"""
from .trade_execution import (
    record_trade,
    check_trailing_stop_exit_cond
)

"""
백테스트 클래스들입니다.
"""
from .Backtester import (
    BacktesterABS,
    BacktesterABS_v2,
    OrderType,
    OrderPositionSide,
    OrderStatus,
    CloseType,
    DataRow,
    Order,
)

from .symbols import get_binance_symbols_for_backtest

__all__ = [
    # Data Utils
    'get_data',
    'generate_data_for_backtest',
    'make_unofficial_interval',
    
    # Indicators
    'calculate_supertrend',
    'get_supertrend',
    'calculate_ut_signal',
    'get_ut_signal',
    'calculate_blackflag',
    'get_blackflag',
    'calculate_ichimoku_senkou_a',
    'get_ichimoku_senkou_a',
    'calculate_support_resistance_line',
    'get_support_resistance_line',
    
    # Trade Analysis
    'analyze_trade_history',
    'analyze_trade_history_v2',
    'analyze_trade_history_for_vector',
    'merge_csv_to_excel',
    
    # Trade Execution
    'record_trade',
    'check_trailing_stop_exit_cond',
    
    # Backtester Classes
    'BacktesterABS',
    'BacktesterABS_v2',
    'OrderType',
    'OrderPositionSide',
    'OrderStatus',
    'CloseType',
    'DataRow',
    'Order',
    

    # Symbols
    'get_binance_symbols_for_backtest'
]

# 버전 정보
__version__ = '1.0.0'
VERSION_INFO = tuple(map(int, __version__.split('.')))