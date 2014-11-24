from django.contrib import admin

from models import ModeldiffSync

from django.forms import TextInput, Textarea
from django.db import models


class ModeldiffSyncAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active', 'last_checked', 'last_sync')
    list_display_links = ('id', 'name',)

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'80'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    actions = ['run_syncs']

    def run_syncs(self, request, queryset):
        from django_beanstalkd_jobs import BeanstalkClient
        client = BeanstalkClient()
        client.call('modeldiffsync.run_sync', '')
    run_syncs.short_description = "Run modelsyncs"


admin.site.register(ModeldiffSync, ModeldiffSyncAdmin)
