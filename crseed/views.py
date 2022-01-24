from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .tasks import backgroundCrossSeedTask
from .tasks import checkTaskExists, killAllBackgroupTasks
from django.contrib.auth.decorators import login_required
from .forms import ParamSettingForm
from .models import ProcessParam, TorClientSetting, CrossTorrent, SearchedHistory, ProcessLog, TaskControl
from ajax_datatable.views import AjaxDatatableView
from django.core import serializers
from django.contrib import messages
import json


def getConfig():
    c = ProcessParam.objects.all().first()
    if c:
        return c
    else:
        return ProcessParam()


def getClient():
    c = TorClientSetting.objects.all().first()
    if c:
        return c
    else:
        return TorClientSetting()


@login_required
def settingsView(request):
    client = getClient()
    config = getConfig()
    if request.method == "POST":
        form = ParamSettingForm(request.POST)
        if form.is_valid():
            config.jackett_prowlarr = form.cleaned_data['jackett_prowlarr']
            config.jackett_url = form.cleaned_data['jackett_url']
            config.jackett_api_key = form.cleaned_data['jackett_api_key']
            config.trackers = form.cleaned_data['jackett_trackers']
            config.fc_count = form.cleaned_data['fc_count']
            config.fc_interval = form.cleaned_data['fc_interval']
            client.clienttype = form.cleaned_data['client_type']
            client.host = form.cleaned_data['client_host']
            client.port = form.cleaned_data['client_port']
            client.username = form.cleaned_data['client_username']
            client.password = form.cleaned_data['client_password']
            config.save()
            client.save()
            return redirect('cs_list')
        else:
            messages.error(request, "Check error messages")
            return render(request, 'crseed/settings.html', {'form': form})
            # form = ParamSettingForm()

    form = ParamSettingForm(
        initial={
            "client_type": client.clienttype,
            "client_host": client.host,
            "client_port": client.port,
            "client_username": client.username,
            "client_password": client.password,
            "jackett_prowlarr": config.jackett_prowlarr,
            "jackett_url": config.jackett_url,
            "jackett_api_key": config.jackett_api_key,
            "jackett_trackers": config.trackers,
            "fc_count": config.fc_count,
            "fc_interval": config.fc_interval,
        })
    return render(request, 'crseed/settings.html', {
        'form': form,
    })


def validSettings():
    client = getClient()
    config = getConfig()
    return client.host and client.port and config.jackett_url.startswith(
        'http') and config.jackett_api_key


def StartTask():
    taskctrl = TaskControl.objects.all().last()
    if not taskctrl:
        taskctrl = TaskControl()
    taskctrl.cancel_task = 0
    taskctrl.save()

    log = ProcessLog()
    log.live = True
    log.save()


def StopTask():
    taskctrl = TaskControl.objects.all().last()
    if taskctrl:
        taskctrl.cancel_task = 1
        taskctrl.save()
    log = ProcessLog.objects.all().last()
    if log and log.live:
        log.log_message += 'User canceled! \n'
        log.save()


@login_required
def proceedCrossSeed(request):
    killAllBackgroupTasks()

    if not validSettings():
        print('config not ready...')
        return redirect('cs_setting')

    StartTask()

    vname = "proceed_cross_seed"
    backgroundCrossSeedTask(schedule=0, verbose_name=vname)
    return redirect('cs_list')


@login_required
def cancelTasks(request):
    StopTask()
    return JsonResponse({'stopped': True})


class CrossedTorrentTable(AjaxDatatableView):
    model = CrossTorrent
    title = 'Crossed torrents'
    show_column_filters = False
    initial_order = [
        ["added_date", "desc"],
    ]
    length_menu = [[30, 50], [30, 50]]
    column_defs = [
        {
            'name': 'added_date',
            'visible': True,
            'title': 'Added on',
            'searchable': False,
        },
        {
            'name': 'name',
            'visible': True,
            'title': 'Torrent Name',
            'searchable': True,
        },
        {
            'name': 'sizeStr',
            'visible': True,
            'title': 'Size',
            'sort_field': 'size',
            'searchable': False,
        },
        {
            'name': 'tracker',
            'title': 'Tracker',
            'visible': True,
            'searchable': False,
        },
        {
            'name': 'crossed_with',
            'foreign_field': 'crossed_with__name',
            'title': 'Crossed with (local)',
            'visible': True,
            'searchable': True,
        },
        {
            'name': 'crossed_with_tracker',
            'foreign_field': 'crossed_with__tracker',
            'title': 'Tracker (local)',
            'visible': True,
            'searchable': False,
        },
        {
            'name': 'location',
            'visible': True,
            'title': 'Location',
            'searchable': False,
        },
    ]


@login_required
def crossTorrentListView(request):
    livelog = ProcessLog.objects.all().last()
    return render(request, 'crseed/list.html', {'log_data': livelog})


class SearchHistoryTable(AjaxDatatableView):
    model = SearchedHistory
    title = 'Search history'
    show_column_filters = False
    initial_order = [
        ["added_date", "desc"],
    ]
    length_menu = [[30, 50], [30, 50]]
    column_defs = [
        {
            'name': 'added_date',
            'visible': True,
            'title': 'Added on',
            'searchable': False,
        },
        {
            'name': 'name',
            'visible': True,
            'title': 'Torrent Name',
        },
        {
            'name': 'sizeStr',
            'visible': True,
            'title': 'Size',
            'sort_field': 'size',
            'searchable': False,
        },
        {
            'name': 'location',
            'title': 'Location',
            'visible': True,
            'searchable': False,
        },
        {
            'name': 'tracker',
            'title': 'Tracker',
            'visible': True,
            'searchable': False,
        },
    ]


@login_required
def searchHistoryListView(request):
    return render(request, 'crseed/history.html')


@login_required
def clearHistory(request):
    SearchedHistory.objects.all().delete()
    ProcessLog.objects.all().delete()
    return render(request, 'crseed/history.html')


@login_required
def clearCrossed(request):
    CrossTorrent.objects.all().delete()
    return redirect('cs_list')


@login_required
def ajaxRefreshProcessLog(request):
    log = ProcessLog.objects.all().last()
    if not log:
        log = ProcessLog()
    data = serializers.serialize(
        "json", [log],
        fields=('live', 'total_in_client', 'flow_limit', 'progress',
                'query_count', 'match_count', 'download_count', 'log_message'))
    # log.refresh_from_db()
    if len(log.log_message) > 0:
        log.log_message = ''
        log.save()
    return HttpResponse(data, content_type="application/json")


# @login_required
# def ajaxRefreshProcessLog2(request):
#     log = ProcessLog.objects.all().last()
#     return render(request, 'crseed/logdiv.html', {
#         'log_data': log,
#     })
