# -*- coding: utf-8 -*-
import datetime


def get_start_end_ts_by_date(date, back_days=0):
    # type: (datetime.date) -> (int, int)
    if back_days:
        end_date = date - datetime.timedelta(days=back_days)
        return int(end_date.strftime('%s')), int(date.strftime('%s'))
    else:
        return int(date.strftime('%s')), int((date + datetime.timedelta(days=1)).strftime('%s'))
