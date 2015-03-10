from django.contrib import admin

from models import ModeldiffSync

from django.forms import TextInput, Textarea
from django.db import models

from utils import run_sync


class ModeldiffSyncAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active', 'last_id', 'last_checked', 'last_sync')
    list_display_links = ('id', 'name',)

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'80'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    actions = ['run_syncs', 'run_syncs_background']

    def run_syncs(self, request, queryset):
        for r in queryset:
            run_sync(r)
    run_syncs.short_description = "Run modelsyncs"

    def run_syncs_background(self, request, queryset):
        from django_beanstalkd_jobs import BeanstalkClient
        client = BeanstalkClient()
        client.call('modeldiffsync.run_sync', '')
    run_syncs_background.short_description = "Run modelsyncs in background"


admin.site.register(ModeldiffSync, ModeldiffSyncAdmin)
