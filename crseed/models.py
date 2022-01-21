from django.db import models
from .humanbytes import HumanBytes

CLIENT_TYPES = [
    ('qb', 'qbittorrent'),
    ('tr', 'transmission'),
    ('de', 'deluge'),
]


class SearchedHistory(models.Model):
    torrent_id = models.BigAutoField(primary_key=True)
    hash = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    size = models.BigIntegerField(default=0)
    location = models.CharField(max_length=255, null=True)
    tracker = models.CharField(max_length=255, null=True)
    root_dir = models.CharField(max_length=255, null=True)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crseed_searched_torrent'

    @property
    def sizeStr(self):
        return HumanBytes.format(self.size)

    def natural_key(self):
        return self.name

    def __str__(self):
        return self.name


class CrossTorrent(models.Model):
    torrent_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    size = models.BigIntegerField(default=0)
    location = models.CharField(max_length=255, null=True)
    tracker = models.CharField(max_length=255, null=True)
    root_dir = models.CharField(max_length=255, null=True)
    crossed_with = models.ForeignKey(
        SearchedHistory,
        null=True,
        on_delete=models.SET_NULL,
    )
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crseed_cross_torrent'

    @property
    def sizeStr(self):
        return HumanBytes.format(self.size)


    def __str__(self):
        return self.name

class ProcessLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    added_date = models.DateTimeField(auto_now_add=True)
    live = models.BooleanField(default=False)
    total_in_client = models.IntegerField(default=0)
    flow_limit = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)
    query_count = models.IntegerField(default=0)
    match_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    log_message = models.TextField()
    error_abort = models.IntegerField(default=0)


class TaskControl(models.Model):
    task_control_id = models.BigAutoField(primary_key=True)
    cancel_task = models.IntegerField(default=0)
    

class ProcessParam(models.Model):
    process_id = models.BigAutoField(primary_key=True)
    jackett_url = models.CharField(max_length=128)
    jackett_api_key = models.CharField(max_length=255)
    delay = models.IntegerField(default=5)
    trackers = models.CharField(max_length=255, default='', null=True)
    # progress = models.IntegerField(default=0)
    strict_size = models.BooleanField(default=False)
    fc_count = models.IntegerField(default=20)
    fc_interval = models.IntegerField(default=2)

    class Meta:
        db_table = 'crseed_process_param'


class TorClientSetting(models.Model):
    client_id = models.BigAutoField(primary_key=True)
    host = models.CharField(max_length=128)
    port = models.IntegerField(default=8091)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    clienttype = models.CharField(max_length=2,
                                  choices=CLIENT_TYPES,
                                  default='de')
    inprocess = models.BooleanField(default=False)
    process_param = models.ForeignKey(
        ProcessParam,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        db_table = 'crseed_torrent_client'

    def __str__(self):
        return self.name
