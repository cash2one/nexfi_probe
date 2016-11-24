# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import defaultdict

from django.db import models
from django.db.models import Count

from clients import utils


class Clients(models.Model):
    nodeid = models.CharField(max_length=128)
    addr = models.CharField(max_length=128)
    from_field = models.CharField(db_column='from', max_length=128)
    model = models.CharField(max_length=128)
    rssi = models.IntegerField()
    ssid = models.CharField(max_length=128, blank=True, null=True)
    action = models.IntegerField(blank=True, null=True)
    timestamp = models.IntegerField()
    time = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'clients'

    @classmethod
    def get_unique_node_ids(cls):
        return list(cls.objects.values_list('nodeid', flat=True).annotate().distinct())

    @classmethod
    def get_all_clients(cls, node_id=None, start_datetime=None, end_datetime=None):
        query = cls.objects
        if node_id:
            query = query.filter(nodeid=node_id)

        if start_datetime and end_datetime:
            query = query.filter(timestamp__gte=start_datetime, timestamp__lt=end_datetime)

        return query.order_by('-id').all()

    @classmethod
    def get_client_daily_activities(cls, node_ids, date):
        start_ts, end_ts = utils.get_start_end_ts_by_date(date)
        hours = range(24)
        result = defaultdict(list)
        count = defaultdict(int)
        for node_id in node_ids:
            dt = cls.objects.filter(
                timestamp__gte=start_ts,
                timestamp__lt=end_ts,
                nodeid=node_id,
            ).extra(
                select={'hr': 'hour(time)'}
            ).values('hr').annotate(n_count=Count('nodeid'))
            for d in hours:
                for item in dt:
                    if item['hr'] == d:
                        result[node_id].append(item['n_count'])
                        count[node_id] += item['n_count']
                        break
                else:
                    result[node_id].append(0)

        return result, count

    @classmethod
    def get_client_all_day_activities(cls, node_ids, date, end_date):
        start_ts, end_ts = utils.get_start_end_ts_by_dates(date, end_date)
        dates = []
        while date <= end_date:
            dates.append(str(date))
            date += datetime.timedelta(days=1)

        result = defaultdict(list)
        count = defaultdict(int)
        for node_id in node_ids:
            dt = cls.objects.filter(
                timestamp__gte=start_ts,
                timestamp__lt=end_ts,
                nodeid=node_id,
            ).extra(
                select={'day': 'date(time)'}
            ).values('day').annotate(n_count=Count('nodeid'))

            for d in dates:
                for item in dt:
                    if str(item['day']) == d:
                        result[node_id].append(item['n_count'])
                        count[node_id] += item['n_count']
                        break
                else:
                    result[node_id].append(0)

        return result, count

    @classmethod
    def get_client_monthly_activities(cls, node_ids, year):
        start_ts, end_ts = utils.get_start_end_ts_by_year(year)
        months = range(1, 13)
        result = defaultdict(list)
        count = defaultdict(int)
        for node_id in node_ids:
            dt = cls.objects.filter(
                timestamp__gte=start_ts,
                timestamp__lt=end_ts,
                nodeid=node_id,
            ).extra(
                select={'month': 'month(time)'}
            ).values('month').annotate(n_count=Count('nodeid'))

            for d in months:
                for item in dt:
                    if str(item['month']) == str(d):
                        result[node_id].append(item['n_count'])
                        count[node_id] += item['n_count']
                        break
                else:
                    result[node_id].append(0)

        return result, count


class NodeInfo(models.Model):
    nodeid = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=128)

    @classmethod
    def get_node_info_mapping(cls, node_ids):
        info = cls.objects.filter(nodeid__in=node_ids)
        result = defaultdict(lambda: None)
        for i in info:
            result[i.nodeid] = i

        return result

    @classmethod
    def get_or_create(cls, nodeid):
        return cls.objects.get_or_create(nodeid=nodeid)
