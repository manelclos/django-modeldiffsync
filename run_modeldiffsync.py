from modeldiffsync.models import ModeldiffSync
from modeldiffsync.utils import run_sync


for sync in ModeldiffSync.objects.all():
    run_sync(sync)
