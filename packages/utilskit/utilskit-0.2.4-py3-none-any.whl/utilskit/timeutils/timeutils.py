from datetime import date, datetime, timedelta
import time

__all__ = ['get_now', 'time_measure', 'get_date_list']

# 오늘 날짜 추출
def get_now(form='년-월-일 시:분:초'):
    now = datetime.now()
    form = form.replace('년', '%Y')
    form = form.replace('월', '%m')
    form = form.replace('일', '%d')
    form = form.replace('시', '%H')
    form = form.replace('분', '%M')
    form = form.replace('초', '%S')
    result = now.strftime(form)
    return result


def time_measure(t):
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    return h, m ,s


def get_date_list(year, mon_list, start_day_list, end_day_list):
    date_list = []
    for idx, mon in enumerate(mon_list):
        if mon > 12 or mon < 1:
            continue
        start_day = start_day_list[idx]
        end_day = end_day_list[idx]
        for dd in range(start_day, end_day+1):
            if dd > 31 or dd < 1: 
                continue
            if mon in [4, 6, 9, 11]:
                if dd > 30:
                    continue
            if mon == 2:
                if dd > 29:
                    continue
            dd = str(dd).zfill(2)
            mm = str(mon).zfill(2)
            date_list.append(f'{year}-{mm}-{dd}')
    date_list.sort()
    return date_list