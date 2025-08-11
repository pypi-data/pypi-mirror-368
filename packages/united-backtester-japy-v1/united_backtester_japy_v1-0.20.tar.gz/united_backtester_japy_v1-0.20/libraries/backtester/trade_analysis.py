import pandas as pd
import numpy as np
from datetime import datetime
import re
import os
from .trade_execution import record_trade

def analyze_trade_history(trade_history, df_ohlc, symbol, save_trades=True, ptc=0.0005,initial_balance=10000,**strategy_params):
    '''
    trade_history와 OHLC 데이터를 이용하여 트레이딩 성과를 분석하는 함수
    수수료를 반영하여 실제 수익률 계산. 전략 파라미터는 kwargs로 동적 처리
     
    ***
    트레이딩뷰랑 타점이 같아도 수치가 조금 안맞는 부분이 생기는데, 트레이딩뷰에서는 
    수익률 계산시에 수량을 이용하고, 틱사이즈를 반영하기 때문에 조금 차이가 있음.
    범용적으로 사용하기 위해 일단 이 부분은 구현하지 않기로 함
    ***
    
    Parameters:
    trade_history (list): 거래 내역 리스트
    df_ohlc (pd.DataFrame): OHLC 데이터프레임
    symbol (str): 거래 심볼
    save_trades (bool): 거래 내역 저장 여부
    ptc (float): 거래당 수수료 비율 (기본값: 0.0005 = 0.05%)
    **strategy_params: 전략 관련 파라미터들 (키워드 인자로 동적 전달)
    
    Returns:
    dict: 분석 결과 딕셔너리
    '''
    # trade_history를 DataFrame으로 변환
    df = pd.DataFrame(trade_history)
    
    # 거래 내역 저장
    if save_trades:
        trade_history_dir = 'trade_history'
        os.makedirs(trade_history_dir, exist_ok=True)
        df.to_csv(f'{trade_history_dir}/{symbol}.csv', index=False)
    
    # 날짜 형식 변환
    df['entry_time'] = pd.to_datetime(df['entry_time'])
    df['exit_time'] = pd.to_datetime(df['exit_time'])
    
    # 익절 비율에 따라 익절 가격 계산
    df['profit'] = df['profit_pct'] * abs(df['margin'])  / 100
    df['net_profit'] = (df['profit']) - (ptc * 2) * abs(df['margin'])
    
    # 수수료 없는 수익률 계산
    initial_balance_no_fee = initial_balance
    portfolio_values_no_fee = [initial_balance_no_fee]
    current_value_no_fee = initial_balance_no_fee
    
    for ret in df['profit']:
        # 이전 포트폴리오 가치에 대한 수익률 적용
        current_value_no_fee = current_value_no_fee + (ret)
        portfolio_values_no_fee.append(current_value_no_fee)
    df['portfolio_value_no_fee'] = portfolio_values_no_fee[1:]  # 첫 번째 값(초기자본)은 제외
    
    # 순수익용 수정된 포트폴리오 가치 계산
    initial_balance = initial_balance
    portfolio_values = [initial_balance]
    current_value = initial_balance

    for ret in df['net_profit']:
        # 이전 포트폴리오 가치에 대한 수익률 적용
        current_value = current_value + (ret)
        portfolio_values.append(current_value)

    df['portfolio_value'] = portfolio_values[1:]  # 첫 번째 값(초기자본)은 제외

    # mdd 계산
    full_portfolio_values = pd.Series(df_ohlc['margin_balance'])
    rolling_max = full_portfolio_values.cummax()
    drawdowns = (full_portfolio_values - rolling_max) / rolling_max
    max_drawdown = drawdowns.min()
    
    # 보유 시간 계산 (시간 단위)
    df['holding_time'] = (df['exit_time'] - df['entry_time']).dt.total_seconds() / 3600
    
    # 승률 계산 (수수료 차감 후 기준)
    total_trades = len(df)
    profitable_trades = len(df[df['net_profit'] > 0])
    win_rate = profitable_trades / total_trades if total_trades > 0 else 0
    
    # 단순 보유 수익률 계산
    first_price = df_ohlc.loc[df['entry_time'].min():, 'close'].iloc[0]
    last_price = df_ohlc.loc[:df['exit_time'].max(), 'close'].iloc[-1]
    buy_and_hold_return = (last_price / first_price - 1) * 100
    
    # 월별 수익률 계산 (수수료 차감 후)
    df['month'] = df['exit_time'].dt.strftime('%Y-%m')
    monthly_returns = df.groupby('month').agg({
        'net_profit': 'sum'
    }).sort_index()
    
    # 총 수익률 계산
    total_return = (df['portfolio_value'].iloc[-1] / initial_balance - 1) * 100
    total_return_no_fee = (df['portfolio_value_no_fee'].iloc[-1] / initial_balance_no_fee - 1) * 100
    
    # 단순 보유 대비 초과 수익률
    excess_return = total_return - buy_and_hold_return
    
    # 기본 결과 딕셔너리
    result_dict = {
        "symbol": symbol,
        "수익(수수료제외)": f'{round(total_return_no_fee, 2)}%',
        "순수익(수수료포함)": f'{round(total_return, 2)}%',
        "10000달러 투자시 보유 자산": f"{round(df['portfolio_value'].iloc[-1], 2)}",
        "거래횟수": total_trades,
        "단순보유수익": f'{round(buy_and_hold_return, 2)}%',
        "단순보유대비수익": f'{round(excess_return, 2)}%',
        "최대손실폭": f'{round(max_drawdown * 100, 2)}%',
        "승률(수수료포함)": f'{round(win_rate * 100, 2)}%',
        "평균보유시간": f'{round(df["holding_time"].mean(), 2)}시간',
        "최대보유시간": f'{round(df["holding_time"].max(), 2)}시간',
        "총수수료": f'{round(total_return_no_fee - total_return,2)}%'
    }
    
    # 전략 파라미터 추가
    for param_name, param_value in strategy_params.items():
        result_dict[param_name] = param_value
    
    def create_monthly_df(start_date, end_date):
        # date_range로 월별 인덱스 생성
        monthly_index = pd.date_range(
            start=start_date,
            end=end_date,
            freq='MS'  # MS는 Month Start를 의미
        )
        # 인덱스 포맷 변경 (YYYY-MM 형식으로)
        monthly_index = monthly_index.strftime('%Y-%m')
        
        # 빈 데이터프레임 생성
        df = pd.DataFrame(index=monthly_index)
        return df

    temp_df = create_monthly_df(df_ohlc.index[0], df_ohlc.index[-1])

    # 데이터프레임 병합
    merged_df = pd.merge(
        temp_df, 
        monthly_returns,
        left_index=True,
        right_index=True,
        how='left'  # left join으로 test_df의 모든 월을 유지
    )

    merged_df = merged_df.fillna(0)
    # 월별 수익률 추가
    for month, return_value in merged_df.iterrows():
        result_dict[f'{month} 수익'] = f'{round(return_value["net_profit"], 2)}USDT'
    return result_dict


def analyze_trade_history_v2(trade_history,margin_balances,save_trades=True, ptc=0.0005,initial_balance=10000,**strategy_params):
    '''
    trade_history와 OHLC 데이터를 이용하여 트레이딩 성과를 분석하는 함수
    수수료를 반영하여 실제 수익률 계산. 전략 파라미터는 kwargs로 동적 처리
     
    ***
    트레이딩뷰랑 타점이 같아도 수치가 조금 안맞는 부분이 생기는데, 트레이딩뷰에서는 
    수익률 계산시에 수량을 이용하고, 틱사이즈를 반영하기 때문에 조금 차이가 있음.
    범용적으로 사용하기 위해 일단 이 부분은 구현하지 않기로 함
    ***
    
    Parameters:
    trade_history (list): 거래 내역 리스트
    symbol (str): 거래 심볼
    save_trades (bool): 거래 내역 저장 여부
    ptc (float): 거래당 수수료 비율 (기본값: 0.0005 = 0.05%)
    **strategy_params: 전략 관련 파라미터들 (키워드 인자로 동적 전달)
    
    Returns:
    dict: 분석 결과 딕셔너리
    '''
    # trade_history를 DataFrame으로 변환
    df = pd.DataFrame(trade_history)
    
    # 변환할 시간 컬럼들
    time_columns = ['entry_time', 'activated_time', 'exit_time']

    for col in time_columns:
        if col in df.columns:
            # 1) 정수 ns → tz-aware(UTC) datetime 으로 바로 변환
            s = pd.to_datetime(df[col], unit='ns', errors='coerce', utc=True)

            # 2) 원하는 시간대로 변환
            df[col] = s.dt.tz_convert('Asia/Seoul')
    
    if len(df) == 0:
        print('No trades')
        return 
    
    # 거래 내역 저장
    if save_trades:
        trade_history_dir = 'trade_history'
        os.makedirs(trade_history_dir, exist_ok=True)
        df.to_csv(f'{trade_history_dir}/trade_history.csv', index=False)
    
    # 익절 비율에 따라 익절 가격 계산
    df['profit'] = df['profit_pct'] * abs(df['margin'])  / 100
    df['net_profit'] = (df['profit']) - (ptc * 2) * abs(df['margin'])
    
    # 수수료 없는 수익률 계산
    initial_balance_no_fee = initial_balance
    portfolio_values_no_fee = [initial_balance_no_fee]
    current_value_no_fee = initial_balance_no_fee
    
    for ret in df['profit']:
        # 이전 포트폴리오 가치에 대한 수익률 적용
        current_value_no_fee = current_value_no_fee + (ret)
        portfolio_values_no_fee.append(current_value_no_fee)
    df['portfolio_value_no_fee'] = portfolio_values_no_fee[1:]  # 첫 번째 값(초기자본)은 제외
    
    # 순수익용 수정된 포트폴리오 가치 계산
    initial_balance = initial_balance
    portfolio_values = [initial_balance]
    current_value = initial_balance

    for ret in df['net_profit']:
        # 이전 포트폴리오 가치에 대한 수익률 적용
        current_value = current_value + (ret)
        portfolio_values.append(current_value)

    df['portfolio_value'] = portfolio_values[1:]  # 첫 번째 값(초기자본)은 제외

    # mdd 계산 마진 밸런스 이용으로 대체 
    full_portfolio_values = pd.Series(margin_balances)
    rolling_max = full_portfolio_values.cummax()
    drawdowns = (full_portfolio_values - rolling_max) / rolling_max
    max_drawdown = drawdowns.min()
    
    # 보유 시간 계산 (시간 단위)
    df['holding_time'] = (df['exit_time'] - df['entry_time']).dt.total_seconds() / 3600
    
    # 승률 계산 
    total_trades = len(df)
    profitable_trades = len(df[df['net_profit'] > 0])
    win_rate = profitable_trades / total_trades if total_trades > 0 else 0
    
    
    # 월별 수익률 계산 (수수료 차감 후)
    df['month'] = df['exit_time'].dt.strftime('%Y-%m')
    monthly_returns = df.groupby('month').agg({
        'net_profit': 'sum'
    }).sort_index()
    
    # 총 수익률 계산
    total_return = (df['portfolio_value'].iloc[-1] / initial_balance - 1) * 100
    total_return_no_fee = (df['portfolio_value_no_fee'].iloc[-1] / initial_balance_no_fee - 1) * 100
    
    
    # 기본 결과 딕셔너리
    result_dict = {
        "수익(수수료제외)": f'{round(total_return_no_fee, 2)}%',
        "순수익(수수료포함)": f'{round(total_return, 2)}%',
        "10000달러 투자시 보유 자산": f"{round(df['portfolio_value'].iloc[-1], 2)}",
        "거래횟수": total_trades,
        "최대손실폭": f'{round(max_drawdown * 100, 2)}%',
        "승률(수수료포함)": f'{round(win_rate * 100, 2)}%',
        "평균보유시간": f'{round(df["holding_time"].mean(), 2)}시간',
        "최대보유시간": f'{round(df["holding_time"].max(), 2)}시간',
        "총수수료": f'{round(total_return_no_fee - total_return,2)}%'
    }
    
    # 전략 파라미터 추가
    for param_name, param_value in strategy_params.items():
        result_dict[param_name] = param_value
    
    def create_monthly_df(start_date, end_date):
        # date_range로 월별 인덱스 생성
        monthly_index = pd.date_range(
            start=start_date,
            end=end_date,
            freq='MS'  # MS는 Month Start를 의미
        )
        # 인덱스 포맷 변경 (YYYY-MM 형식으로)
        monthly_index = monthly_index.strftime('%Y-%m')
        
        # 빈 데이터프레임 생성
        df = pd.DataFrame(index=monthly_index)
        return df

    temp_df = create_monthly_df(df['entry_time'].min(), df['exit_time'].max())

    # 데이터프레임 병합
    merged_df = pd.merge(
        temp_df, 
        monthly_returns,
        left_index=True,
        right_index=True,
        how='left'  # left join으로 test_df의 모든 월을 유지
    )

    merged_df = merged_df.fillna(0)
    # 월별 수익률 추가
    for month, return_value in merged_df.iterrows():
        result_dict[f'{month} 수익'] = f'{round(return_value["net_profit"], 2)}USDT'
    return result_dict
# deprecated
def analyze_trade_history_for_vector(data, symbol, ptc=0.0005, save_trades=True, **strategy_params):
    """
    벡터연산을 이용한 거래 내역 분석 함수
    
    ***
    트레이딩뷰랑 타점이 같아도 수치가 조금 안맞는 부분이 생기는데, 트레이딩뷰에서는 
    수익률 계산시에 수량을 이용하고, 틱사이즈를 반영하기 때문에 조금 차이가 있음.
    범용적으로 사용하기 위해 일단 이 부분은 구현하지 않기로 함
    ***
    
    Args:
        data (dataframe): position이 채워진 데이터프레임
        symbol (str): 거래 심볼
        ptc (float): 거래 수수료율
        save_trades (bool): 거래 내역 저장 여부(BTCUSDT인 경우만 저장이 됨)
    """
    df = data.copy()
    # 거래 신호 계산
    df["trade"] = df.position.diff().fillna(0)

    # 포지션별 수익률 계산
    trades = []
    current_position = None
    entry_price = None
    entry_time = None

    for i in range(len(df)):
        current_row = df.iloc[i]
        # 새로운 포지션 진입
        if current_row.trade != 0:
            if current_position is not None:
                # 이전 포지션 청산
                exit_price = current_row.close
                trade_dict = record_trade(
                    symbol, 
                    current_position, 
                    current_position, 
                    entry_price, 
                    exit_price, 
                    'vector', 
                    entry_time,
                    current_row.name)
                trades.append(trade_dict)
            
            # 새로운 포지션 정보 저장
            if current_row.position != 0:  # 새로운 포지션 진입
                current_position = current_row.position
                entry_price = current_row.close
                entry_time = current_row.name
            else:  # 포지션 종료
                current_position = None
                entry_price = None
                entry_time = None

    # 결과 저장
    if save_trades and trades and symbol == 'BTCUSDT':
        trade_df = pd.DataFrame(trades)
        trade_df = trade_df.sort_values('entry_time')
        trade_df.to_csv(f'trade_details_{symbol}.csv', index=False)

    result_dict = analyze_trade_history(trades, df, symbol, ptc=ptc, **strategy_params)
    return result_dict

def filter_columns(df):
    """
    데이터프레임에서 기본 컬럼과 월별 수익 컬럼을 필터링하는 함수
    
    Parameters:
    df (pandas.DataFrame): 필터링할 데이터프레임
    
    Returns:
    list: 필터링된 컬럼 리스트
    """
    df = df.copy()
    # 기본 컬럼 리스트
    base_columns = [
        'symbol',
        '수익(수수료제외)',
        '순수익(수수료포함)',
        '10000달러 투자시 보유 자산',
        '거래횟수',
        '단순보유수익',
        '단순보유대비수익',
        '최대손실폭',
        '승률(수수료포함)',
        '평균보유시간',
        '최대보유시간',
        '총수수료'
    ]
    
    # 월별 수익 컬럼 찾기 (YYYY-MM 수익 형식)
    monthly_columns = [col for col in df.columns if re.match(r'\d{4}-\d{2}\s수익', col)]
    
    # 모든 필요한 컬럼 합치기
    selected_columns = base_columns + monthly_columns
    
    # 존재하는 컬럼만 선택
    existing_columns = [col for col in df.columns if col not in selected_columns]
    
    return existing_columns

def merge_csv_to_excel(test_id,input_file_path,save_dir=''):
    """
    CSV 파일을 읽어서 엑셀 파일로 변환하고 통계 정보를 추가하는 함수
    
    Parameters:
    test_id (str): 테스트 ID (엑셀 파일명과 시트명으로 사용)
    input_file_path (str): 입력 CSV 파일 경로
    save_dir (str): 저장할 디렉토리 경로 (기본값: 현재 디렉토리)
    
    Returns:
    None: 엑셀 파일로 저장됨
    """

    if save_dir !='':
        os.makedirs(save_dir, exist_ok=True)
        if save_dir[-1] != '/':
            save_dir += '/'
        output_file_path = f'{save_dir}/{test_id}.xlsx'
    else:
        output_file_path = f'{test_id}.xlsx'

    # 엑셀 작성기 생성
    with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
        sheet_name = test_id  # 시트 이름
        startrow = 0  # 데이터가 시작할 행 번호

        # CSV 파일 읽기
        df = pd.read_csv(input_file_path)
        
        if df.empty:
            raise ValueError("CSV 파일이 비어있습니다.")
        
        # symbol 컬럼 존재 여부 및 값 체크
        if 'symbol' not in df.columns:
            raise ValueError("CSV 파일에 'symbol' 컬럼이 없습니다.")
        
        if df['symbol'].iloc[0] is None or df['symbol'].iloc[0] == '' or pd.isna(df['symbol'].iloc[0]):
            raise ValueError("CSV 파일의 첫 번째 행에 symbol 값이 없거나 빈값입니다.")
        
        # 그룹화할 변수
        group_columns = filter_columns(df)
        if not group_columns:
            # 더미 컬럼을 추가하여 단일 그룹으로 처리
            df['_dummy'] = 1
            group_columns = ['_dummy']
            
        grouped_df = df.groupby(group_columns)
        monthly_columns = sorted([col for col in df.columns if re.match(r'\d{4}-\d{2}\s수익', col)])
        start_month = monthly_columns[0].replace('수익', '').replace(' ', '')
        end_month = monthly_columns[-1].replace('수익', '').replace(' ', '')
        
        # 모든 그룹의 성과 정보를 저장할 리스트
        performance_list = []
        
        # 각 그룹의 성과 정보 수집
        for name, group in grouped_df:
            avg_profit = group['순수익(수수료포함)'].str.replace('%', '').astype(float).mean()
            avg_win_rate = group['승률(수수료포함)'].str.replace('%', '').astype(float).mean()
            avg_mdd = group['최대손실폭'].str.replace('%', '').astype(float).mean()
            avg_trade_count = group['거래횟수'].mean()
            
            performance_data = {
                '평균 순수익': avg_profit,
                '평균 승률': avg_win_rate,
                '평균 거래횟수': avg_trade_count,
                '최대손실폭': avg_mdd,
            }
            # _dummy가 아닌 경우에만 params 추가
            if group_columns != ['_dummy']:
                performance_data['params'] = name
            
            performance_list.append(performance_data)
                
        
        # performance_list → DataFrame
        perf_df = pd.DataFrame(performance_list)

        # z-score 계산용 컬럼 구분
        cols_up   = ['평균 순수익', '평균 승률']       # 클수록 좋음 → 그대로
        cols_down = ['최대손실폭', '평균 거래횟수']     # 작을수록 좋음 → 부호 반전

        # 부호 반전
        for c in cols_down:
            perf_df[c] = -perf_df[c].abs()

        # 표준화(z) : 표준편차가 0일 때는 1로 치환
        def z(series):
            std = series.std(ddof=0)
            return (series - series.mean()) / (std if std else 1)

        z_cols = cols_up + cols_down
        perf_df_z = perf_df[z_cols].apply(z)

        # 복합 스코어 (동일 가중치 합산 ─ 필요하면 perf_df_z[col] * w 로 가중치 조정)
        perf_df['z_score'] = perf_df_z.sum(axis=1)

        # z-score 기준 1등
        top_performance_z = perf_df.loc[perf_df['z_score'].idxmax()]
        
        # Calmar 추가
        calmar_df = perf_df.copy()
        calmar_df['Calmar'] = calmar_df['평균 순수익'] / abs(calmar_df['최대손실폭'])
        top_performance_calmar = calmar_df.loc[calmar_df['Calmar'].idxmax()]
        
        
        # 수익률 기준으로 상위 1개 추출
        top_performance = sorted(performance_list, key=lambda x: x['평균 순수익'], reverse=True)[0]
        
        # 상위 1개 결과 요약 작성
        data_row = [
            '1',
            f"{top_performance['평균 순수익']:.2f}%",
            f"{top_performance['평균 승률']:.2f}%",
            f"{top_performance['평균 거래횟수']:.2f}",
            f"{top_performance['최대손실폭']:.2f}%"
        ]

        columns = ['순수익 순위', '평균 순수익', '평균 승률', '평균 거래횟수', '최대손실폭']

        # _dummy가 아닌 경우에만 params 관련 데이터 추가
        if group_columns != ['_dummy'] and 'params' in top_performance:
            data_row.extend(list(top_performance['params']))
            columns.extend([col for col in group_columns if col != '_dummy'])

        top_summary = pd.DataFrame([data_row], columns=columns, index=['값'])
        startrow += len(top_summary)
        
        # 승률 기준으로 상위 1개 추출
        top_performance_winrate = sorted(performance_list, key=lambda x: x['평균 승률'], reverse=True)[0]
        
        # 승률 기준 상위 1개 결과 요약 작성
        data_row = [
            '1',
            f"{top_performance_winrate['평균 순수익']:.2f}%",
            f"{top_performance_winrate['평균 승률']:.2f}%",
            f"{top_performance_winrate['평균 거래횟수']:.2f}",
            f"{top_performance_winrate['최대손실폭']:.2f}%"
        ]

        columns = ['승률 순위', '평균 순수익', '평균 승률', '평균 거래횟수', '최대손실폭']

        # _dummy가 아닌 경우에만 params 관련 데이터 추가
        if group_columns != ['_dummy'] and 'params' in top_performance_winrate:
            data_row.extend(list(top_performance_winrate['params']))
            columns.extend([col for col in group_columns if col != '_dummy'])

        top_summary_winrate = pd.DataFrame([data_row], columns=columns, index=['값'])
        
        # z-score 기준
        data_row = [
            '1',                                        # 순위
            f"{top_performance_z['평균 순수익']:.2f}%",   # 평균 순수익
            f"{top_performance_z['평균 승률']:.2f}%",     # 평균 승률
            f"{abs(top_performance_z['평균 거래횟수']):.2f}",   # 평균 거래횟수
            f"{-abs(top_performance_z['최대손실폭']):.2f}%",
            # 최대손실폭 (부호 원복)
        ]
        columns = ['z-score 순위', '평균 순수익', '평균 승률', '평균 거래횟수', '최대손실폭']

        # 파라미터(col 이름) 포함
        if group_columns != ['_dummy'] and 'params' in top_performance_z:
            data_row.extend(list(top_performance_z['params']))
            columns.extend([c for c in group_columns if c != '_dummy'])

        top_summary_z = pd.DataFrame([data_row], columns=columns, index=['값'])
        
        # Calmar 기준
        data_row = [
            '1',
            f"{top_performance_calmar['평균 순수익']:.2f}%",
            f"{top_performance_calmar['평균 승률']:.2f}%",
            f"({abs(top_performance_calmar['평균 거래횟수']):.2f}",
            f"{-abs(top_performance_calmar['최대손실폭']):.2f}%"
        ]
        columns = ['Calmar 순위', '평균 순수익', '평균 승률', '평균 거래횟수', '최대손실폭']

        # 파라미터(col 이름) 포함
        if group_columns != ['_dummy'] and 'params' in top_performance_calmar:
            data_row.extend(list(top_performance_calmar['params']))
            columns.extend([c for c in group_columns if c != '_dummy'])
            
        top_summary_calmar = pd.DataFrame([data_row], columns=columns, index=['값'])
        
        # 상위 1개 결과 먼저 작성
        # 순수익 기준
        top_summary.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
        startrow += len(top_summary) + 3  # 3줄 간격
        
        # 승률 기준
        top_summary_winrate.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
        startrow += len(top_summary_winrate) + 3  # 3줄 간격
        
        # z-score 기준
        top_summary_z.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
        startrow += len(top_summary_z) + 3
        
        # Calmar 기준
        top_summary_calmar.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
        startrow += len(top_summary_calmar) + 3
        
        for name, group in grouped_df:
            # _dummy 컬럼이 존재하는 경우 제거
            if '_dummy' in group.columns:
                group = group.drop('_dummy', axis=1)
            # 그룹별 평균 계산
            avg_profit = group['순수익(수수료포함)'].str.replace('%', '').astype(float).mean()
            avg_win_rate = group['승률(수수료포함)'].str.replace('%', '').astype(float).mean()
            avg_mdd = group['최대손실폭'].str.replace('%', '').astype(float).mean()
            avg_trade_count = group['거래횟수'].mean()

            # 기본 설명과 값 리스트 생성
            descriptions = ["테스트기간", '평균 순수익', '평균 거래횟수', '평균 승률', '최대손실폭']
            values = [
                f"{start_month} ~ {end_month}",
                f"{avg_profit:.2f}%",
                f"{avg_trade_count:.2f}",
                f"{avg_win_rate:.2f}%",
                f"{avg_mdd:.2f}%"
            ]

            # group_columns가 _dummy가 아닌 경우에만 추가 정보 포함
            if group_columns != ['_dummy']:
                descriptions.extend(group_columns)
                values.extend(name)

            # 그룹별 통계 정보 DataFrame 생성
            summary = pd.DataFrame({
                '설명': descriptions,
                '값': values
            })

            # 통계 정보 추가
            summary.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)

            # 그룹 데이터를 통계 정보 밑에 추가
            group.to_excel(writer, sheet_name=sheet_name, startrow=startrow + len(summary) + 2, index=False)

            # 다음 그룹 데이터를 추가할 위치 계산 (빈 줄을 두기 위해 7줄 간격)
            startrow += len(summary) + len(group) + 7

    print(f"결과가 {output_file_path} 파일에 저장되었습니다.")