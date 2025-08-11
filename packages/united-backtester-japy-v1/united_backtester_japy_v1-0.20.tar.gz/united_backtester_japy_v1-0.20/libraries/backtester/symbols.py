"""
테스트에 필요한 심볼을 정의합니다.
"""

from typing import List  # 타입 힌팅을 위한 import 추가

def get_binance_symbols_for_backtest() -> List[str]:
    """백테스트용 바이낸스 심볼 리스트를 반환합니다."""
    return [
    "BTCUSDT", "ETHUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"
]
