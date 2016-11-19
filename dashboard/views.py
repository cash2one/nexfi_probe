# -*- coding: utf-8 -*-
import logging as log
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from clients.models import Clients, NodeInfo


def _parse_str_datetime(str_datetime, format="%Y-%m-%d %H:%M:%S"):
    # type: (str, str) -> int
    if not str_datetime:
        return 0
    try:
        return int(datetime.strptime(str_datetime, format).strftime('%s'))
    except Exception as e:
        log.error('invalid datetime: %s' % e)

    return 0


def do_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('home'))
        else:
            return render(request, 'login.html', context=dict(auth_failed=True))


def do_logout(request):
    logout(request)
    return redirect(reverse('login'))


def get_client_list(request):
    try:
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))
    except Exception as e:
        log.error('got an page error: %s' % e)
        page = 1
        rows = 10

    node_id = request.GET.get('node_id', '')
    start_datetime = _parse_str_datetime(request.GET.get('start_datetime', ''))
    end_datetime = _parse_str_datetime(request.GET.get('end_datetime', ''))

    all_clients = Clients.get_all_clients(node_id=node_id, start_datetime=start_datetime, end_datetime=end_datetime)

    try:
        p = Paginator(all_clients, rows)
        cur_page = p.page(page)
    except Exception as e:
        log.error('got an error: %s' % e)
        raise

    node_ids = [i.nodeid for i in cur_page.object_list]
    node_info_mapping = NodeInfo.get_node_info_mapping(node_ids)

    records = []
    for obj in cur_page.object_list:
        node_info = node_info_mapping[obj.nodeid]
        label = node_info.label if node_info else ''
        records.append({
            'id': obj.id,
            'nodeid': obj.nodeid,
            'addr': obj.addr,
            'from_field': obj.from_field,
            'model': obj.model,
            'rssi': obj.rssi,
            'ssid': obj.ssid,
            'action': obj.action,
            'timestamp': obj.timestamp,
            'time': obj.time,
            'label': label,
        })

    return JsonResponse({'records': p.count, 'rows': records, 'page': page, 'total': p.num_pages})


def update_node_info(request):
    nodeid = request.POST.get('nodeid', '')
    label = request.POST.get('label', '').strip()
    if not nodeid:
        return JsonResponse({'success': False, 'error': 'invalid nodeid'})

    nodeinfo, _ = NodeInfo.get_or_create(nodeid)
    if nodeinfo:
        nodeinfo.label = label
        nodeinfo.save()

    return JsonResponse({'success': True})


@login_required
def client_list(request):
    if request.method == 'POST':
        return update_node_info(request)
    else:
        return get_client_list(request)


@require_GET
@login_required
def node_list(request):
    node_ids = Clients.get_unique_node_ids()
    node_info_mapping = NodeInfo.get_node_info_mapping(node_ids)
    result = []
    for node_id in node_ids:
        node_info = node_info_mapping[node_id]
        label = node_info.label if node_info else ''
        if label:
            result.insert(0, {
                'node_id': node_id,
                'label': label,
            })
        else:
            result.append({
                'node_id': node_id,
                'label': label,
            })
    return JsonResponse({'node_ids': result})


@require_GET
@login_required
def node_activity(request):
    report_type = request.GET.get('report_type', 'daily')
    date = request.GET.get('date', '')
    days = int(request.GET.get('days', 1))
    node_ids = Clients.get_unique_node_ids()
    node_info_mapping = NodeInfo.get_node_info_mapping(node_ids)
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except Exception as e:
        return JsonResponse({'error': 'invalid date'})

    # 通过时间戳限制 count(*) group_by node_ids
    if report_type == 'daily':
        series_dict, total_count_dict = Clients.get_client_daily_activities(node_ids, date)
        x_axis = ['{}:00'.format(i) for i in range(24)]
    else:
        # monthly
        if not days:
            return JsonResponse({'error': 'invalid days'})

        series_dict, total_count_dict = Clients.get_client_all_day_activities(node_ids, date, back_days=days)
        x_axis = []
        for i in range(days):
            x_axis.insert(0, str(date))
            date -= timedelta(days=1)

    result = []
    for node_id in node_ids:
        node_info = node_info_mapping[node_id]
        label = node_info.label if node_info else ''
        result.append({
            'node_id': node_id,
            'label': label,
            'total_count': total_count_dict[node_id],
            'series': series_dict[node_id],
            'xAxis': x_axis
        })

    return JsonResponse({'data': result})
