# -*- coding: utf-8 -*-
import datetime


def get_start_end_ts_by_date(date):
    # type: (datetime.date) -> (int, int)
    return int(date.strftime('%s')), int((date + datetime.timedelta(days=1)).strftime('%s'))


def get_start_end_ts_by_dates(date, end_date):
    # type: (datetime.date, datetime.date) -> (int, int)
    return int(date.strftime('%s')), int(end_date.strftime('%s'))
