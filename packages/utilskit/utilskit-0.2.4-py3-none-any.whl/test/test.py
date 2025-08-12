import sys
import os
# import time

sys.path.append('/home/kimyh/library/utilskit')
def main():
    from utilskit import classificationutils as clu
    label2id_dict = {
        '고양이':0,
        '개':1
    }
    t = ['고양이', '개', '개', '고양이', '고양이', '개']
    p = ['개', '개', '고양이', '고양이', '고양이', '개']
    id2label_dict = {
        0:'고양이',
        1:'개'
    }
    t = [1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0]
    p = [1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1]
    
    print(type(id2label_dict))
    cm = clu.confusion_matrix(
        class_dict=id2label_dict,
        true_list=t,
        pred_list=p,
        ignore_idx=None,
        round_num=2,
        percentage=True
    )
    print(cm)
    cm.to_csv('cm.csv', encoding='utf-8-sig')

def main2():
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    from utilskit import dataframeutils as dfu
    start_time = datetime.strptime('2025-07-22 10:05:15', '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(seconds=5)
    time_range = pd.date_range(start=start_time, end=end_time, freq='S')
    value_ary = np.random.randint(10, 20, len(time_range))
    df = pd.DataFrame({
        'time':time_range,
        'value':value_ary
    })
    print(df)
    df = dfu.utc2kor(
        dataframe=df, 
        column='time', 
        extend=True
    )
    print(df)


def main3():
    import numpy as np
    import pandas as pd
    from utilskit import dataframeutils as dfu

    value_ary1 = [1, 6, 3, 8, 5]
    value_ary2 = [5, 7, 2, 6, 9]
    df = pd.DataFrame({'col1':value_ary1, 'col2':value_ary2})
    df = dfu.adnormal2nan(
        dataframe=df,
        column='col1',
        max_value=7,
        min_value=2
    )
    print(df)


def main4():
    import numpy as np
    import pandas as pd
    from datetime import datetime
    from utilskit import dataframeutils as dfu

    time_ary = ['2024-05-11 03:45:12', '2024-05-11 03:45:15', '2024-05-11 03:45:16']
    value_ary = [1, 5, 6]
    df = pd.DataFrame({
        'time':time_ary,
        'value':value_ary
    })
    print(df)
    df = dfu.time_filling(
        dataframe=df,
        start='2024-05-11 03:45:10',
        end='2024-05-11 03:45:20',
        column='time'
    )
    print(df)
    df = pd.DataFrame([1, 2, 3, 4], columns=['value'])
    if dfu.isdfvalid(df, ['value']):
        print('컬럼이 전부 존재합니다.')


def main5():
    import pandas as pd
    import numpy as np
    from utilskit import dataframeutils as dfu

    value_ary1 = [1, np.nan, np.nan, 2, 3, np.nan, np.nan, np.nan]
    value_ary2 = np.random.randint(0, 10, size=len(value_ary1))
    df = pd.DataFrame({
        'value1':value_ary1,
        'value2':value_ary2
    })
    print(df)
    df = dfu.fill_repeat_nan(
        dataframe=df,
        column='value1',
        repeat=3
    )
    print(df)


def main6():
    import pandas as pd
    import numpy as np
    from utilskit import dataframeutils as dfu

    # value_ary1 = [20, 20, 20, 20, 2, 20, 20, 20, 1, 1, 2, 1]
    # # value_ary2 = np.random.randint(0, 10, size=len(value_ary1))
    # df = pd.DataFrame({
    #     'value1':value_ary1
    # })
    # # print(df)
    # df = dfu.pin2nan(
    #     dataframe=df, 
    #     column='value1', 
    #     max_diff=0.1,
    #     repeat=3
    # )
    # print(df)

    import pandas as pd

    data = [19, 19, 20, 20, 1, 21, 21, 22, 1, 1, 2, 1]
    df = pd.DataFrame({'val': data})

    # 이전, 현재, 다음 값을 비교하기 위해 shift를 활용
    df['prev'] = df['val'].shift(1)
    df['next'] = df['val'].shift(-1)
    print(df)

    # [1]만 추출: 이전값과 다음값이 모두 1이 아니면서 현재값이 1인 경우
    isolated_ones = df[(df['val'] == 1) & (df['prev'] != 1) & (df['next'] != 1)]

    print(isolated_ones)

def main7():
    from utilskit import logutils as lu
    log = lu.get_logger(
        log_path='./log3',
        log_name='whole', 
        rollover=True
    )

    log.debug("DEBUG 메시지입니다.")
    log.info("INFO 메시지입니다.")
    log.warning("WARNING 메시지입니다.")
    log.error("ERROR 메시지입니다.")
    log.critical("CRITICAL 메시지입니다.")
    lu.log_sort('./log3')


def main8():
    import numpy as np
    from utilskit import plotutils as plu
    np.random.seed(42)
    x = np.arange(100)
    data = np.random.randint(5, 20, size=100)
    data1 = np.random.randint(5, 20, size=100)
    data2 = np.random.randint(5, 20, size=100)
    
    plu.draw_plot(
        title='whole2', 
        x=x,
        y=data, 
        fig_size=(30, 8),
        x_range=(-10, 120), 
        y_range=(0, 25),
        x_label='x data', 
        y_label='y data', 
        legend=True,
        title_font=25, 
        x_font=20, 
        y_font=20,
        x_label_font=23, 
        y_label_font=23,
        line_style='dash', 
        line_size=3, 
        marker_style='circle', 
        marker_size=10, 
        marker_color='white',
        marker_border_size=2, 
        marker_border_color='black',
        add_x_list=[x, x],
        add_y_list=[data1, data2],
        add_color_list=['red', 'violet'],
        focus_list=[(22, 27), (42, 53), (70, 76)],
        focus_color_list=['red', 'red', 'blue'],
        alpha_list=[0.1, 0.5, 1],
        save_path='./image'
    )

def main9():
    import numpy as np
    from utilskit import plotutils as plu
    np.random.seed(42)
    x = np.arange(100)
    data = np.random.randint(5, 20, size=100)
    data1 = np.random.randint(50, 90, size=100)
    data2 = np.random.randint(180, 190, size=100)
    
    plu.draw_subplot(
        sub_title_list=['data', 'data1', 'data2'],
        x_list=[x, x, x],
        y_list=[data, data1, data2],
        # sub_row_idx=3,
        # sub_col_idx=1,
        # fig_size=(30, 5*3),
        # x_range_list=[(0, 100), (-10, 110), (-20, 120)],
        # y_range_list=[(-10, 100), (-10, 100), (150, 240)],
        # title_font=25,
        # x_font=15,
        # y_font=5,
        focus_list=[(22, 27), (42, 53), (70, 76)],
        focus_color_list=['red', 'red', 'green'],
        alpha_list=[0.2, 0.2, 0.2],
        save_path='./sub_image',
        save_name='sub-focus'
    )


def main10():
    import numpy as np
    from utilskit import repeatutils as rpu
    data = np.array(
        [
            1, 1, 1, 1, 1,  # 0 ~ 4
            2, 2, 2, 2,     # 5 ~ 8
            3, 3,           # 9 ~ 10
            4, 4, 4,        # 11 ~ 13
            np.nan, np.nan, np.nan, np.nan,  # 14 ~ 17
            1, 1, 1, 1,     # 18 ~ 21
            3, 3, 3,        # 22 ~ 24
            np.nan, np.nan, np.nan, np.nan, np.nan, # 25 ~ 29
            1, 1, 1, 1, 1, 1, 1,    # 30 ~ 36
            np.nan  # 37
        ]
    )
    data = ['아', '아', '아', '아', '아', '바', '바']
    print(data)
    repeat_section = rpu.get_repeat_section(
        data=data,
        repeat=4,
        except_nan=False
    )
    print(repeat_section)


def main11():
    import numpy as np
    from utilskit import repeatutils as rpu
    data = np.array(
        [
            1, 1, 1, 1, 1,  # 0 ~ 4
            2, 2, 2, 2,     # 5 ~ 8
            3, 3,           # 9 ~ 10
            4, 4, 4,        # 11 ~ 13
            np.nan, np.nan, np.nan, np.nan,  # 14 ~ 17
            1, 1, 1, 1,     # 18 ~ 21
            3, 3, 3,        # 22 ~ 24
            np.nan, np.nan, np.nan, np.nan, np.nan, # 25 ~ 29
            1, 1, 1, 1, 1, 1, 1,    # 30 ~ 36
            np.nan  # 37
        ]
    )
    repeat_section = rpu.get_stan_repeat_section(
        data=data,
        value=1,
        repeat=4,
        mode='a',
        reverse=True
    )
    print(repeat_section)


def main12():
    from utilskit import timeutils as tiu
    now = tiu.get_now('년|분|시|월|초|일')
    
    import time
    hh, mm, ss = tiu.time_measure(-1)
    print(f'입력된 값은 {hh}시간 {mm}분 {ss}초 입니다.')

    date_list = tiu.get_date_list(
        year=2025,
        mon_list=[2],
        start_day_list=[25],
        end_day_list=[33]
    )
    print(date_list)


def main13():
    from utilskit import utils as u
    u.envs_setting()

    a = 1
    b = '2'
    try:
        c = a + b
    except TypeError:
        error_info = u.get_error_info()
        print(error_info)
    

def main14():
    import numpy as np
    from utilskit import repeatutils as rpu
    data = np.array(
        [
            1, 1, 1, 1, 1,  # 0 ~ 4
            2, 2, 2, 2,     # 5 ~ 8
            3, 3,           # 9 ~ 10
            4, 4, 4,        # 11 ~ 13
            np.nan, np.nan, np.nan, np.nan,  # 14 ~ 17
            1, 1, 1, 1,     # 18 ~ 21
            3, 4, 5,        # 22 ~ 24
            np.nan, np.nan, np.nan, np.nan, np.nan, # 25 ~ 29
            1, 1, 1, 1, 1, 1, 1,    # 30 ~ 36
            np.nan, np.nan, np.nan  # 37 ~ 39
        ]
    )
    result = rpu.get_section(
        data, 
        repeat=4,
        # mode='e',   # 반복횟수 이상
        # key='nan',  # 최대 최소 범위 지정시 무시된다.
        max_key=3,  # 최대 3
        min_key=2,  # 최소 2
        # between=True,   # 사잇값
        # max_equal=False, # 3 이하
        # min_equal=True, # 2 이상
        # except_nan=False,   # 최대 최소 범위 지정시 무시된다.
        # reverse=True   # 반전 없음
    )
    print(result)


def main15():
    from utilskit import dbutils as dbu
    mt_id = 'GV01RD03P001T10M59'
    query = f'''
SELECT reg_no, vhcl_type FROM cmm_vhcl_info 
WHERE mt_id="{mt_id}"
'''
#     query = f'''
# UPDATE cmm_vhcl_info set vin="a"
# WHERE mt_id="GV01RD03P001T11M04"
# '''
#     query = '''
#     INSERT INTO test_db(`group_80`, `시스템`, `로거 데이터`, `정비 지침서`, `설명`, `오류검증`, `category`, `manufact`)
#     VALUES (1111, 'DPF', 'aaa', 'bbb', 'ccc', 1234, 'eee', 'fff')
# '''
#     query = """
# DELETE FROM test_db
# WHERE `로거 데이터`='aaa'
# """
    info = dbu.query2db(
        query=query,
        host='119.201.125.234',
        port=3306,
        user='theimc',
        password='theimc#10!',
        db_name='GJ2025'
    )
    print(info)


def main16():
    from utilskit import dbutils as dbu
    mt_id = 'GV01RD03P001T10M59'

    from utilskit import dataframeutils as dfu
    df = dfu.read_df('./group_df.csv')
    dbu.df2db(
        dataframe=df, 
        table='test_db', 
        host='119.201.125.234', 
        port=3306, 
        user='theimc', 
        password='theimc#10!', 
        db_name='GJ2025'
    )
    # print(df)
    # dbu.pd2db(df, table, host, port, user, passward, db_name)



if __name__ == '__main__':
    # from utilskit import logutils as lu
    # log = lu.get_logger(
    #     log_path='./log3'
    # )
    # log.info('인포메이션')
    # log.error('에러로그')
    # lu.log_sort(
    #     log_path='./log3'
    # )
    main15()