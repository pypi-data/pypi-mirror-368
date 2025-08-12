import numpy as np
import pandas as pd
import shutil
import os
import sys
import json
import time
import csv
from datetime import date, datetime, timedelta


__all__ = ['envs_setting', 'get_error_info']


def save_yaml(path, obj):
    import yaml
    with open(path, 'w') as f:
        yaml.dump(obj, f, sort_keys=False)


def load_yaml(path):
    import yaml
    with open(path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def envs_setting(seed=42):
    '''
    난수지정 등의 환경설정

    parameters
    ----------
    random_seed: int
        설정할 random seed

    returns
    -------
    torch, numpy, random 등에 대한 랜덤 시드 고정    
    '''
    import random
    import numpy as np

    # seed
    np.random.seed(seed)
    random.seed(seed)



def normalize_1D(ary):
    '''
    1차원데이터를 0~1 사이 값으로 normalize 하는 함수

    parameters
    ----------
    ary: numpy array
        noramlize 를 적용할 1차원 array
    
    returns
    -------
    0 ~ 1 사이로 noramalize 된 array
    '''
    ary = np.array(ary)
    
    if len(ary.shape) > 1:
        return print('1 차원 데이터만 입력 가능')
    
    ary_min = np.min(ary)
    ary_min = np.subtract(ary, ary_min)
    ary_max = np.max(ary_min)
    ary_norm = np.divide(ary_min, ary_max)
    
    return ary_norm
    

def get_error_info():
    import traceback
    traceback_string = traceback.format_exc()
    return traceback_string


def read_jsonl(data_path):
    try:
        data_list = validate_data(
            data_path=data_path,
            encoding='utf-8-sig'
        )
        
    except UnicodeDecodeError:
        
        data_list = validate_data(
            data_path=data_path,
            encoding='cp949'
        )
    return data_list
    
    
def validate_data(data_path, encoding):
    data_list = []
    try:
        with open(data_path, 'r', encoding=encoding) as f:
            prodigy_data_list = json.load(f)
        data_list.append(prodigy_data_list)
    except json.decoder.JSONDecodeError:
        with open(data_path, 'r', encoding=encoding) as f:
            for line in f:
                line = line.replace('\n', '')
                line.strip()
                if line[-1] == '}':
                    json_line = json.loads(line)
                    data_list.append(json_line)
    return data_list


def tensor2array(x_tensor):
    x_ary = x_tensor.detach().cpu().numpy()
    return x_ary


def save_tensor(x_tensor, mode):
    x_ary = tensor2array(x_tensor=x_tensor)
    
    if mode == 1:
        b = x_ary[0]
        # b = np.round(b, 3)
        b = np.where(np.absolute(b) > 2, np.round(b, 0), np.round(b, 3))
        df = pd.DataFrame(b)
        df.to_csv(f'./temp.csv', index=False, encoding='utf-8-sig')
        print(df)
        print(x_ary.shape)
    
    if mode == 2:
        ary = x_ary[0]
        i, j, k = ary.shape
        print(i, j, k)
        for idx in range(k):
            a = np.squeeze(ary[:, :, idx:idx+1])
            a = np.where(np.absolute(a) > 2, np.round(a, 0), np.round(a, 3))
            df = pd.DataFrame(a)
            df.to_csv(f'./temp{idx}.csv', index=False, encoding='utf-8-sig')
            print(df)
        print(x_ary.shape)