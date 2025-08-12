import sys
import os
import numpy as np
import pandas as pd
import warnings

__all__ = ['get_section']


def issame(value1, value2):
    # 서로 같은 경우
    if value1 == value2:
        return True
    # 서로 다른 경우
    else:
        # 어느 한 쪽 이라도 str type 인 경우
        if isinstance(value1, str) or isinstance(value2, str):
            if str(value1) == str(value2):
                return True # ex) value1 = 1, value2 = '1'
            else:
                return False # ex) value1 = 1, value2 = 'nan'
        # 어느 한 쪽이라도 str type 이 아닌 경우
        else:
            # value1 이 NaN 일때
            if np.isnan(value1):
                # value2 도 NaN 이면
                if np.isnan(value2):
                    return True
                # value2 가 NaN 이 아니면
                else:
                    return False
            else:
                return False


# def get_repeat_section2(data, repeat_num, refer_value=None, except_nan=True):
#     '''
#     '''
#     raw_ary = np.array(data)
#     ary = raw_ary.copy()
#     same_tf = (ary[:-1] == ary[1:])
#     is_nan = np.isnan(ary)

#     for i, j, k, l in zip(ary[:-1], ary[1:], same_tf, is_nan):
#         print(i, j, k, l)

#     a = np.where(same_tf==1)
#     print(a)

#     sys.exit()

#     value_list = []
#     start_idx_list = []
#     end_idx_list = []
#     start_idx = 0
#     # pre_value = 'nan'
#     repeat_num = 1    
#     for idx, value in enumerate(ary):
        
#         # 가장 처음인 경우
#         if idx == 0:
#             pre_value = value
#             continue
        
#         # 현재 값이 이전 값과 동일할때
#         if issame(value, pre_value):
#             repeat_num += 1

#         # 현재 값이 이전 값과 다를때
#         else:
#             if repeat_num >= stan_repeat:
#                 value_list.append(pre_value)
#                 start_idx_list.append(start_idx)
#                 end_idx_list.append(idx-1)
#             # 시작 지점 갱신 & 반복횟수 초기화
#             start_idx = idx
#             repeat_num = 1
#         pre_value = value

#     # 마지막 값이 이전 값과 같을때
#     if issame(value, pre_value):
#         if repeat_num >= stan_repeat:
#             value_list.append(value)
#             start_idx_list.append(start_idx)
#             end_idx_list.append(idx)
#     # --------------------------------------
#     # 함수 수정중
#     # 결과 정리
#     result = {'nan':None}
#     for v, si, ei in zip(value_list, start_idx_list, end_idx_list):
#         result[str(v)] = (si, ei)
#     if except_nan:
#         del result['nan']
#     return result



def get_repeat_section(data, repeat, except_nan=True):
    '''
    데이터 array 에서 정해놓은 반복 횟수 (stan_repeat) 만큼 반복되는 숫자구간이 있다면
    그 구간의 시작, 끝 위치 index 값을 추출한다.
    NaN 가 반복되는지 여부를 포함시킬 수 있다.
    '''
    ary = data.copy()

    value_list = []
    start_idx_list = []
    end_idx_list = []
    start_idx = 0
    # pre_value = 'nan'
    repeat_num = 1    
    for idx, value in enumerate(ary):
        
        # 가장 처음인 경우
        if idx == 0:
            pre_value = value
            continue
        
        # 현재 값이 이전 값과 동일할때
        if issame(value, pre_value):
            repeat_num += 1
            
        # 현재 값이 이전 값과 다를때
        else:
            if repeat_num >= repeat:
                value_list.append(pre_value)
                start_idx_list.append(start_idx)
                end_idx_list.append(idx-1)
            # 시작 지점 갱신 & 반복횟수 초기화
            start_idx = idx
            repeat_num = 1

        pre_value = value

    # 마지막 값이 이전 값과 같을때
    if issame(value, pre_value):
        if repeat_num >= repeat:
            value_list.append(value)
            start_idx_list.append(start_idx)
            end_idx_list.append(idx)
    # --------------------------------------
    # 함수 수정중
    # 결과 정리
    # print(value_list)
    # sys.exit()
    result = {}
    for v, si, ei in zip(value_list, start_idx_list, end_idx_list):
        try:
            result[str(v)].append((si, ei))
        except KeyError:
            result[str(v)] = [(si, ei)]
    if except_nan:
        del result['nan']
    return result


def get_stan_repeat_section(data, value, repeat, mode='a', reverse=False):
    '''
    ary 에서 기준값(stan_value)이 지정한 횟수(stan_repeat) 
    이상(above) 또는 이하(below) 만큼 반복되는 구간의 시작, 끝 위치 index 값을 추출하는 함수
    reverse 를 True 로 지정하면 해당 각 구간의 끝->시작, 시작->끝 으로 반전된다.
    mode 는 a (above) 와 b (below)만 존재
    '''
    ary = data.copy()

    start_idx = 0
    start_idx_list = []
    end_idx_list = []
    repeat_num = 1

    if len(ary) == 0:
        return [], []
            
    # stan_value = float(stan_value)
    for idx, val_ in enumerate(ary):

        # 가장 처음인 경우
        if idx == 0:
            pre_value = val_
            continue

        # 현재 값이 기준값(stan_value) 인 경우
        if issame(val_, value):
            # 이전값이 기준값과 동일하면
            if issame(pre_value, value):
                # 반복횟수 +1
                repeat_num += 1
            # 이전 값이 기준값과 다르면
            else:
                # 반복횟수 초기화
                repeat_num = 1
                # 현재 위치를 시작로 위치 지정
                start_idx = idx
        # 현재 값이 기준값과 다른 경우
        else:
            # 이전 값이 기준값과 동일하면
            if issame(pre_value, value):
                # idx 끝 위치 지정

                # 반복 횟수 기준 이상인 경우
                if mode == 'a':
                    # 기록된 반복 횟수가 기준 횟수 이상이면
                    if repeat_num >= repeat:
                        # 지정해둔 시작 위치 index 값을 구간시작 index 로 저장
                        start_idx_list.append(start_idx)
                        # 현재 위치 바로 이전 위치 index 값을 구간끝 index 로 저장
                        end_idx_list.append(idx-1)
                # 반복 횟수 기준 이하인 경우
                elif mode == 'b':
                    # 기록된 반복 횟수가 기준 횟수 이하면
                    if repeat_num <= repeat:
                        start_idx_list.append(start_idx)
                        end_idx_list.append(idx-1)
                elif mode == 'e':
                    # 기록된 반복 횟수가 기준 횟수와 동일하면
                    if repeat_num == repeat:
                        start_idx_list.append(start_idx)
                        end_idx_list.append(idx-1)
                else:
                    print('mode 를 a (above:이상), b (below:이하) 또는 e (equal:동일) 중 하나로 지정해주세요')
                    raise KeyError()
        # 현재 위치 값을 이전 위치로 저장
        pre_value = val_
    
    # 가장 마지막 데이터가 기준값과 동일한 경우
    if issame(val_, value):
        if mode == 'a':
            if repeat_num >= repeat:
                start_idx_list.append(start_idx)
                # 현재 위치 index 를 구간 끝 index 로 저장
                end_idx_list.append(idx)
        elif mode == 'b':
            if repeat_num <= repeat:
                start_idx_list.append(start_idx)
                end_idx_list.append(idx)
        elif mode == 'e':
            if repeat_num == repeat:
                start_idx_list.append(start_idx)
                end_idx_list.append(idx)
        else:
            raise KeyError('mode 를 a (above:이상), b (below:이하) 또는 e (equal:동일) 중 하나로 지정해주세요')
    # 가장 마지막 데이터가 기준값과 다르면 반복 계산할 필요 없음
    
    # 반전
    if reverse:
        rev_start_idx_list = [0]
        rev_end_idx_list = [len(ary)-1]
        for ns_idx, ne_idx in zip(start_idx_list, end_idx_list):
            if ns_idx == 0:
                rev_start_idx_list.pop(0)
                rev_start_idx_list.append(ne_idx+1)
                continue
            if ne_idx == len(ary)-1:
                rev_end_idx_list.pop(-1)
                rev_end_idx_list.append(ns_idx-1)
                continue
            rev_start_idx_list.append(ne_idx+1)
            rev_end_idx_list.insert(-1, ns_idx-1)
        
        start_idx_list = rev_start_idx_list.copy()
        end_idx_list = rev_end_idx_list.copy()
    
    # 결과 정리
    result = []
    for si, ei in zip(start_idx_list, end_idx_list):
        result.append((si, ei))

    return result



def reversing(data, start_idx_list, end_idx_list):
    ary = data.copy()
    # 반전
    rev_start_idx_list = [0]
    rev_end_idx_list = [len(ary)-1]
    for ns_idx, ne_idx in zip(start_idx_list, end_idx_list):
        if ns_idx == 0:
            rev_start_idx_list.pop(0)
            rev_start_idx_list.append(ne_idx+1)
            continue
        if ne_idx == len(ary)-1:
            rev_end_idx_list.pop(-1)
            rev_end_idx_list.append(ns_idx-1)
            continue
        rev_start_idx_list.append(ne_idx+1)
        rev_end_idx_list.insert(-1, ns_idx-1)
    
    start_idx_list = rev_start_idx_list.copy()
    end_idx_list = rev_end_idx_list.copy()
    
    # 결과 정리
    result = []
    for si, ei in zip(start_idx_list, end_idx_list):
        result.append((si, ei))

    return result


def get_section(data, repeat, mode='a', key=None, 
                max_key=None, min_key=None, between=False, max_equal=True, min_equal=True,
                except_nan=True, reverse=False):
    
    # ===============================================================
    # 값 설정

    # nan 설정 필터링
    if str(key) == 'nan' and except_nan:
        raise ValueError('연산결과에 NaN이 제외되어있습니다. NaN 의 구간을 산정하려면 except_nan 을 False 로 설정해주세요')
    
    # 최소 2이상 반복 횟수 설정
    if repeat <= 1:
        raise ValueError('반복횟수(repeat)는 최소 2 이상을 입력해야합니다.')

    # 최대값 기준 설정
    if max_key is not None:
        # key 값이 있는 경우 경고
        if key is not None:
            warnings.warn('max_key 또는 min_key 값이 설정되어있는 경우 key 값은 무시됩니다.')
        # key 값을 무효화
        key = None
        # 기준값이 숫자가 아닌 경우
        if not isinstance(max_key, (int, float)):
            raise ValueError('최대값 기준은 숫자값(int, float)으로 입력해야합니다.')
        # 사잇값이 아닌경우
        if not between:
            # 최댓값 이상인 값을 전부 최댓값으로 변환
            if max_equal:
                data = list(map(lambda x:max_key if x >= max_key else x, data))
            # 최댓값 초과인 값을 전부 최댓값으로 변환
            else:
                data = list(map(lambda x:max_key+1 if x > max_key else x, data))

    # 최소값 기준 설정
    if min_key is not None:
        # key 값이 있는 경우 경고
        if key is not None:
            warnings.warn('max_key 또는 min_key 값이 설정되어있는 경우 key 값은 무시됩니다.')
        # key 값을 무효화
        key = None
        # 기준값이 숫자가 아닌 경우
        if not isinstance(min_key, (int, float)):
            raise ValueError('최소값 기준은 숫자값(int, float)으로 입력해야합니다.')
        # 사잇값이 아닌 경우
        if not between:
            # 최솟값 이하인 값을 전부 최솟값으로 변환
            if min_equal:
                data = list(map(lambda x:min_key if x <= min_key else x, data))
            else:
                data = list(map(lambda x:min_key if x < min_key else x, data))

    # 사잇값인 경우
    if between:
        # 최댓값 및 최솟값이 설정되어있는지 여부
        if max_key is not None and min_key is not None:
            # 최소~최대 사잇값을 전부 최소_최대 형태로 변환
            if max_equal:
                if min_equal:
                    data = list(map(lambda x:f'{min_key}_{max_key}' if x >= min_key and x <= max_key else x, data))
                else:
                    data = list(map(lambda x:f'{min_key}_{max_key}' if x > min_key and x <= max_key else x, data))
            else:
                if min_equal:
                    data = list(map(lambda x:f'{min_key}_{max_key}' if x >= min_key and x < max_key else x, data))
                else:
                    data = list(map(lambda x:f'{min_key}_{max_key}' if x > min_key and x < max_key else x, data))
        
        else:
            raise ValueError('between = True 로 설정한 경우 max_key 및 min_key 양쪽 다 값이 설정되어있어야합니다.')
    # numpy array 화
    data = np.array(data)

    # key
    # key 값의 형태를 데이터와 동일하게 설정
    if key is not None:
        key_df = pd.DataFrame([key, np.nan], columns=['key']).astype(str)
        key = key_df['key'][0]

    # =================================================================
    # 반복 구간 판단 
    # data 라는 이름을 가진 string 열 생성
    df = pd.DataFrame(data, columns=['data']).astype(str)
    # 한 칸 앞으로 이동
    df['data_next'] = df['data'].shift(-1)
    # 한 칸 뒤로 이동
    df['data_pre'] = df['data'].shift(1)
    # 이전, 이후 간의 동일성을 기준으로 True, False 산정
    df['next_tf'] = df['data'] == df['data_next']
    df['pre_tf'] = df['data'] == df['data_pre']
    # 값을 더하여 수치값으로 환산
    df['tf'] = df['next_tf'].astype(int) + df['pre_tf'].astype(int)
    '''
    규칙상 1 에서 시작해서 1 로 끝나는 구간은 같은 값이 반복되는 구간임
    1 과 1 의 사잇값은 반드시 2임
    '''

    # =================================================================
    # 반복 구간 추출
    data_ary = df['data'].values
    tf_ary = df['tf'].values
    result = {'nan':[]}
    flag = 0
    for idx, (d, tf) in enumerate(zip(data_ary, tf_ary)):
        flag += tf
        # 구간 시작
        if tf == 1 and flag == 1:
            start = idx
        # 구간 끝
        elif tf == 1 and flag >= 2:
            # 반복횟수 계산
            length = (flag+2) // 2
            # 이상 모드
            if mode == 'a':
                if length >= repeat:
                    # 구간 저장
                    try: result[d].append((start, idx))
                    except KeyError: result[d] = [(start, idx)]
            # 이하 모드
            elif mode == 'b':
                if length <= repeat:
                    # 구간 저장
                    try: result[d].append((start, idx))
                    except KeyError: result[d] = [(start, idx)]
            # 동일 모드
            elif mode == 'e':
                if length == repeat:
                    # 구간 저장
                    try: result[d].append((start, idx))
                    except KeyError: result[d] = [(start, idx)]
            # 모드 설정 에러
            else:
                raise KeyError('mode 를 a (above:이상), b (below:이하) 또는 e (equal:동일) 중 하나로 지정해주세요')
            # 플래그 초기화
            flag = 0

    # =======================================================
    # 최종 결과 필터링
        
    # NaN 포함 여부
    if except_nan:
        del result['nan']

    # 기준 키 값이 존재하는 경우
    if key is not None:
        try: result = {key : result[key]}
        except KeyError:
            result = {}

    # 최대 설정이 존재하는 경우
    new_result = {}
    if max_key is not None:
        # 사잇값이 아닌 경우
        if not between:
            for k, section in result.items():
                if max_equal:                
                    if float(k) >= max_key:
                        new_result[f'{k}_over'] = section
                else:
                    if float(k) > max_key:
                        new_result[f'{float(k)-1}_over'] = section

    # 최소 설정이 존재하는 경우
    if min_key is not None:
        # 사잇값이 아닌 경우
        if not between:
            for k, section in result.items():
                if min_equal:
                    if float(k) <= min_key:
                        new_result[f'{k}_under'] = section
                else:
                    if float(k) < min_key:
                        new_result[f'{k}_under'] = section
            
    # 사잇값인 경우
    if between and max_key is not None and min_key is not None:
        for k, section in result.items():
            if '_' in k:
                try: new_result[f'{min_key}_{max_key}'] += section
                except KeyError: new_result[f'{min_key}_{max_key}'] = section

    # 새로운 결과값이 존재하면
    if min_key is not None or max_key is not None:
        result = new_result

    # 반전
    rev_result = {}
    if reverse:
        for k, section_list in result.items():
            start_idx_list = []
            end_idx_list = []
            for section in section_list:
                start = section[0]
                end = section[1]
                start_idx_list.append(start)
                end_idx_list.append(end)
            rev_section = reversing(data, start_idx_list, end_idx_list)
            rev_result[f'{k}_rev'] = rev_section
        return rev_result

    return result