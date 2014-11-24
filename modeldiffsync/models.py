# -*- coding: utf-8 -*-
from django.db import models


class ModeldiffSync(models.Model):
    """
    Model to store modeldiff sync configurations
    """
    name = models.CharField(max_length=100, help_text='descriptive name')
    active = models.BooleanField(default=False)
    online_check_url = models.CharField(max_length=255, blank=True,
                                        help_text='URL returning app activity'
                                                  ' status')
    source_url = models.CharField(max_length=255, blank=True,
                                  help_text='REST endpoint providing the'
                                            ' modeldiffs')
    source_username = models.CharField(max_length=50, blank=True, null=True)
    source_password = models.CharField(max_length=50, blank=True, null=True)
    target_url = models.CharField(max_length=255, blank=True,
                                  help_text='REST endpoint to create the '
                                            ' modeldiffs in')
    target_username = models.CharField(max_length=50, blank=True, null=True)
    target_password = models.CharField(max_length=50, blank=True, null=True)
    update_callback_url = models.CharField(max_length=255, blank=True,
                                           help_text='URL to start updating')
    target_update_url = models.CharField(max_length=255,
                                         blank=True, null=True,
                                         help_text='URL to call if modeldiffs'
                                                   ' were added and an update'
                                                   ' must be run')
    username = models.CharField(max_length=50, blank=True,
                                help_text='Username to access the URLS')
    password = models.CharField(max_length=50, blank=True,
                                help_text='Password to access the URLS')
    last_id = models.IntegerField(default=0)
    last_checked = models.DateTimeField(null=True, blank=True)
    last_sync = models.DateTimeField(null=True, blank=True)
