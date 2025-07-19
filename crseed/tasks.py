from background_task import background
from background_task.models import Task
from crseed.models import ProcessLog
from crseed.CrossSeedAutoDL import iterTorrents, checkTaskCanclled, test_download_result
from .torclient import getDownloadClient
from . import views as crview
from django.utils import timezone
import time


class SeedLog():
    def __init__(self, log_object):
        self.log_object = log_object

    def message(self, str, error_abort=0):
        self.log_object.refresh_from_db()
        self.log_object.log_message += str + '\n'

        if error_abort > 0:
            self.log_object.error_abort += 1
        self.log_object.save()

    def status(self,
               flow_limit=-1,
               total_in_client=-1,
               progress=-1,
               query_count=-1,
               match_count=-1):
        self.log_object.refresh_from_db()
        if flow_limit > 0:
            self.log_object.flow_limit = flow_limit
        if total_in_client > 0:
            self.log_object.total_in_client = total_in_client
        if progress > 0:
            self.log_object.progress = progress
        if query_count > 0:
            self.log_object.query_count = query_count
        if match_count > 0:
            self.log_object.match_count = match_count
        self.log_object.save()

    def inc(self, download_count=-1, match_count=-1):
        self.log_object.refresh_from_db()
        if match_count > 0:
            self.log_object.match_count += match_count
        if download_count > 0:
            self.log_object.download_count += download_count
        self.log_object.save()

    def canceled(self):
        self.log_object.refresh_from_db()
        return not self.log_object.live

    def abort(self):
        self.log_object.refresh_from_db()
        return self.log_object.error_abort  > 0
    
    def finish(self):
        self.log_object.live = False
        self.log_object.save()


@background(schedule=0)
def backgroundCrossSeedTask():
    torclient = crview.getClient()
    param = crview.getConfig()

    logobj = ProcessLog.objects.all().last()
    log = SeedLog(logobj)
    if checkTaskCanclled():
        log.finish()
        return
    
    s = 'Starting at:' + timezone.now().strftime("%m/%d/%Y, %H:%M:%S")
    log.message(s)
    print(s)

    dlclient = getDownloadClient(torclient, log)
    if dlclient:
        log.message('Connecting: ' + dlclient.scsetting.host)
        c = dlclient.connect()
        if c:
            iterTorrents(dlclient, param, log)
            # Test the downloadResult function
            test_download_result(dlclient, param, log)
        else:
            log.message('Connect failed: ' + dlclient.scsetting.host)
    else:
        log.message('Connect failed: ' + dlclient.scsetting.host)

    log.message('Finished of this session')
    # time.sleep(5)
    log.finish()


def killAllBackgroupTasks():
    Task.objects.all().delete()


def checkTaskExists(task_vname):
    tasks = Task.objects.filter(verbose_name=task_vname)
    return len(tasks) > 0

