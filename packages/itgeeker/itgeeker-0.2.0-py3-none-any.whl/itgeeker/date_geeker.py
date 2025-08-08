# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, date, timedelta
import pytz

tday = date.today()
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_start_time(yr, mo, d):
    start_time = datetime(int(yr), int(mo), int(d), 0, 0, 0)
    print(f'start_time: {start_time}')
    return start_time


def get_end_time(yr, mo, d=None):
    if not d:
        d = calendar.monthrange(yr, mo)[1]
        print(f"The last day of the month is: {d}")
    end_time = datetime(int(yr), int(mo), int(d), 23, 59, 59)
    print(f'end_time: {end_time}')
    return end_time


def get_pre_yr_mo(yr, mo):
    d = date(yr, mo, 1)
    last_month = d - timedelta(days=1)
    print(f'pre mo yr: {last_month.year}, pre mo mo: {last_month.month}')
    return last_month.year, last_month.month


def get_last_day_of_month(year, month):
    """
  This function takes a year and month as input and returns the last day of the month.
  """
    _, num_days = calendar.monthrange(year, month)
    print(f'last day of the month: {num_days}')
    return num_days

####################### deal with time #######################
# convert second to x hours x minutes x seconds
def format_seconds_duration(seconds):
    try:
        duration = timedelta(seconds=seconds)
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        # return f"{int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds"
        # return f"{int(hours)}小时{int(minutes)}分{int(seconds)}秒"
        if minutes > 0 and seconds > 0:
            return f"{int(hours)}小时{int(minutes)}分{int(seconds)}秒"
        elif minutes > 0:
            return f"{int(hours)}小时{int(minutes)}分"
        elif seconds > 0:
            return f"{int(hours)}小时{int(seconds)}秒"
        else:
            return f"{int(hours)}小时"
    except Exception as err:
        print('err@format seconds duration: %s' % err)
        return ''

# 该方法返回自 Unix 纪元以来的毫秒数，并始终使用 UTC 表示时间js const utcTimestamp = new Date().getTime();
def convert_timestamp_to_dt(cur_utc_timestamp):
    try:
        print('not million sec timestamp')
        last_time = datetime.fromtimestamp(int(cur_utc_timestamp))
    except (ValueError, OSError):
        print('it is million sec timestamp / 1000')
        last_time = datetime.fromtimestamp(int(cur_utc_timestamp) / 1000)
    return last_time

def get_time_with_tz(zone_name='Asia/Shanghai'):
    # Get the Beijing timezone - 'Asia/Shanghai'
    location_tz = pytz.timezone(zone_name)
    utc_now = datetime.now(pytz.utc)
    cur_time_with_tz = utc_now.astimezone(location_tz)
    # print(f'cur_time_with_tz in bj tz: {cur_time_with_tz}')
    return cur_time_with_tz

def remove_time_zone(dt_with_tz):
    dt_no_tz = dt_with_tz.replace(tzinfo=None)
    print("removed datetime tz:", dt_no_tz)
    return dt_no_tz

def convert_datetime_to_utc(dt_with_tz):
    dt_utc_with_tz = dt_with_tz.astimezone(pytz.utc)
    print("convert to UTC with tz:", dt_utc_with_tz)
    return dt_utc_with_tz

def convert_dt_with_tz(dt, tz_name='Asia/Shanghai'):
    # set as tz
    bj = pytz.timezone('Asia/Shanghai')
    dt_bj_tz = bj.localize(dt)
    print("dt_bj_tz:", dt_bj_tz)

    # convert to new tz
    new_tz = pytz.timezone(tz_name)
    dt_to_spec_tz = dt_bj_tz.astimezone(new_tz)
    print("dt_to_spec_tz:", dt_to_spec_tz)
    return dt_to_spec_tz

def check_two_time_diff_sec(cur_time, last_time):
    print(f'cur_time: {cur_time}')
    print(f'last_time: {last_time}')
    try:
        diff_sec = (cur_time - last_time).total_seconds()
        print(f'diff_sec: {diff_sec}')
        return diff_sec
    except Exception as err:
        print('err@check two time diff: %s' % err)
        return 0

def is_summer_vacation(cur_date=None):
    if cur_date is None:
        cur_date = date.today()
    year = cur_date.year
    start = date(year, 7, 1)
    end = date(year, 9, 30)
    return start <= cur_date <= end


