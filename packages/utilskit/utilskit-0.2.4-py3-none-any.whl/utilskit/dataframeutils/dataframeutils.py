import sys
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import csv
import warnings
warnings.filterwarnings('ignore')

# from utilskit import utils as u
from utilskit import repeatutils as rpu

__all__ = ['read_df', 'utc2kor', 'adnormal2nan', 'time_filling',
           'isdfvalid', 'fill_repeat_nan', 'pin2nan']


def read_df(path):
    extention = path.split('.')[-1]
    if extention in ['csv', 'CSV']:
        switch = 'csv'
    elif extention in ['xlsx', 'xls']:
        switch = 'excel'
    elif extention in ['txt']:
        switch = 'txt'
    else:
        raise ValueError(f'{extention}은(는) 잘못되거나 지정되지 않은 확장자입니다.')
    
    if switch == 'csv':
        encoding = 'utf-8-sig'
        while True:
            try:
                data_df = pd.read_csv(path, encoding=encoding)
                break
            except UnicodeDecodeError:
                encoding = 'cp949'
            except pd.errors.ParserError:
                f = open(path, encoding=encoding)
                reader = csv.reader(f)
                csv_list = []
                for line in reader:
                    if len(line) != 38:
                        pass
                    csv_list.append(line)
                f.close()
                data_df = pd.DataFrame(csv_list)
                data_df.columns = data_df.iloc[0].to_list()
                data_df = data_df.drop(index=data_df.index[0])	# 0번째 행을 지움
                break
    if switch == 'excel':
        data_df = pd.read_excel(path)
    if switch == 'txt':
        line_list = []
        with open(path, 'r', encoding='utf-8-sig') as f:
            for line in f.readlines():
                line = line.replace('\n', '')
                if ',' in line:
                    line = line.split(',')
                line_list.append(line)
        data_df = pd.DataFrame(line_list[1:], columns=line_list[0])
    return data_df


def utc2kor(dataframe, column='time', extend=True):
    df = dataframe.copy()
    if df.empty:
        return df
    if extend:
        new_column = f'{column}_kor'
    else:
        new_column = column

    df[new_column] = df[column].astype('str')
    df[new_column] = df[new_column].apply(lambda x: x.replace('T', ' '))
    df[new_column] = df[new_column].apply(lambda x: x.replace('Z', ''))
    
    # UTC 시간을 한국 시간으로 (+9 시간)
    df[new_column] = df[new_column].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    df[new_column] = df[new_column].apply(lambda x: x + timedelta(hours=9))
    df[new_column] = df[new_column].astype('str')

    df = df.sort_values(by=new_column, ascending=True)
    
    return df


def adnormal2nan(dataframe, column, max_value=None, min_value=None):
    df = dataframe.copy()
    if max_value is not None:
        df[column][df[column] > max_value] = np.nan
    if min_value is not None:
        df[column][df[column] < min_value] = np.nan
    return df


def time_filling(dataframe, start, end, column='time'):
    df = dataframe.copy()
    if df.empty:
        return df
    time_range = pd.date_range(start=start, end=end, freq='S')
    time_range_df = pd.DataFrame(time_range, columns=[column])
    time_range_df = time_range_df.astype('str')

    # 합치기
    df = pd.merge(df, time_range_df, how='right')
    return df


def drop_nan(df, stan_col):
    try:
        df = df.dropna(subset=[stan_col])
    except KeyError:
        pass
    return df


def isdfvalid(dataframe, column_list):
    # 유효 컬럼 존재 여부 확인
    try:
        _ = dataframe[column_list]
        return True
    except KeyError:
        return False
    
    
def fill_repeat_nan(dataframe, column, repeat=5):
    '''
    repeat 에 지정한 수치 이상 반복되는 결측치 구간을
    앞뒤값 채우기로 보정하는 함수
    '''
    df = dataframe.copy()
    stan_ary = df[column].values

    # NaN 가 반복되는 구간 산정
    repeat_section = rpu.get_stan_repeat_section(
        ary=stan_ary,
        value='nan',
        repeat=repeat,
        mode='a'
    )

    # 결측치 채우기
    if len(repeat_section) > 0:
        repeat_section = np.array(repeat_section)
        nan_start_idx_list = repeat_section[:, :1].tolist()
        nan_end_idx_list = repeat_section[:, 1:].tolist()
        
        for nan_si, nan_ei in zip(nan_start_idx_list, nan_end_idx_list):
            nan_si = nan_si[0]
            nan_ei = nan_ei[0]
            df.loc[nan_si-1:nan_ei, column] = df.loc[nan_si-1:nan_ei, column].fillna(method='ffill')
            df.loc[nan_si:nan_ei+1, column] = df.loc[nan_si:nan_ei+1, column].fillna(method='bfill')
    
    return df


def pin2nan(dataframe, column, max_diff=0.1, repeat=3):
    '''
    이상치 범위에 속하지 않지만 
    데이터 흐름상 이상치로 볼 필요가 있는 국소 범위의 값들을 결측치로 변경하는 함수
    
    예시: 20, 20, 20, 20, [  1], 20, 20, 20, 1, 1, 2, 1
    결과: 20, 20, 20, 20, [NaN], 20, 20, 20, 1, 1, 2, 1
    '''
    df = dataframe.copy()

    # 기준 컬럼 데이터 추출
    stan_ary = df[column].values
    
    # 현재 값에서 이전값을 뺀 데이터 ary 를 생성
    stan_1_list = stan_ary.tolist()
    stan_1_list.insert(0, stan_ary[0])
    stan_1_ary = np.array(stan_1_list)[:-1]
    diff_ary = np.round(stan_ary - stan_1_ary, 4)
    diff_ary = np.array(list(map(abs, diff_ary)))
    
    #==
    a = df[column].rolling(window=3, min_periods=1).mean()
    print(a)
    sys.exit()
    #==

    # print()
    idx_list = []
    for idx, diff in enumerate(diff_ary):

        # 앞뒤 차이값이 최대 차이값 보다 작은 경우
        if diff < max_diff:
            continue

        # idx 위치 이전 10개 데이터에 대한 평균
        before_aver = np.average(stan_ary[idx-10:idx])

        # idx 위치 이후 10개 데이터에 대한 평균
        after_aver = np.average(stan_ary[idx+1:idx+11])
        
        # 구간 내 nan 이 존재하는 경우 앞뒤 평균을 동일시
        if str(before_aver) == 'nan':
            before_aver = after_aver
        if str(after_aver) == 'nan':
            after_aver = before_aver
        
        # 앞뒤 평균값 간의 차이값 절대값 계산
        aver_diff = abs(after_aver - before_aver)
        
        # 바로 앞 뒤의 차이값과 평균값 간 차이값의 차이값 p 계산
        p = np.round(diff - aver_diff, 4)
        
        # p 가 최대 차이값 보다 큰 경우 이상치로 판단
        if p > max_diff:
            idx_list.append(idx)
            
        # print(f'{idx:5d}, {before_aver:.2f}, {diff:.2f}, {after_aver:.2f}, {aver_diff:.2f}')
        # print(p)
    # print(idx_list)
    del idx
    
    # pin idx 가 존재하는 경우 해당 범위를 nan 으로 대체
    print(stan_ary)
    print(idx_list)
    sys.exit()
    temp_ary = stan_ary.copy()
    if len(idx_list) > 0:
        for idx in idx_list:
            if idx < 3:
                temp_ary[:idx+3] = np.nan
            else:
                temp_ary[idx-3:idx+3] = np.nan
    
    # NaN 가 반복되는 구간 산정
    repeat_section = rpu.get_stan_repeat_section(
        ary=stan_ary,
        value='nan',
        repeat=repeat,
        mode='a'
    )
    print(repeat_section)
    sys.exit()

    # # nan 의 위치 구하기
    # for_fill_start_idx_list, for_fill_end_idx_list = um.identify_stan_repeat_section(
    #     ary=temp_ary, 
    #     stan_value='nan',
    #     stan_repeat=repeat, 
    #     mode='below', 
    #     reverse=False
    # )
    
    
    # 해당 부분을 NaN 값으로 변환
    for fsi, fei in zip(for_fill_start_idx_list, for_fill_end_idx_list):
        df.loc[fsi:fei, column] = np.nan
        df.loc[fsi-1:fei, column] = df.loc[fsi-1:fei, column].fillna(method='ffill')
        df.loc[fsi:fei+1, column] = df.loc[fsi:fei+1, column].fillna(method='bfill')
        
    return df