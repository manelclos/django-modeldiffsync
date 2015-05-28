import json

from django.db import transaction, connection
from django.db.models.loading import get_model
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.utils.wkt import precision_wkt
from django.forms.models import model_to_dict

from modeldiff.models import Geomodeldiff


def get_current_object_from_db(modeldiff):
    model = get_model(*modeldiff.model_name.rsplit('.', 1))
    unique_field = getattr(model.Modeldiff, 'unique_field', None)

    if unique_field:
        kwargs = {unique_field: modeldiff.unique_id}
        obj = model.objects.get(**kwargs)
    else:
        obj = model.objects.get(pk=modeldiff.model_id)
    return obj, model


def get_object_values(obj, model):
    geom_field = model.Modeldiff.geom_field
    geom_precision = model.Modeldiff.geom_precision

    values = model_to_dict(obj)
    geom = getattr(obj, geom_field)
    values[geom_field] = precision_wkt(geom, geom_precision)
    return values


def get_fields(modeldiff):
    sync_conf = getattr(settings, 'MODELDIFFSYNC_CONF', {})

    conf = sync_conf.get(modeldiff.key, None)
    if conf:
        model = conf.get(modeldiff.model_name, None)
        if model:
            return model.get('fields', None)
    return None


def save_object(obj):
    disable_triggers = getattr(settings, 'MODELDIFFSYNC_DISABLE_TRIGGERS',
                               False)
    if disable_triggers:
        with transaction.atomic():
            # This code executes inside a transaction.
            cursor = connection.cursor()
            cursor.execute("ALTER TABLE %s DISABLE TRIGGER USER" %
                           obj._meta.db_table)
            obj.save(modeldiff_ignore=True)
            cursor.execute("ALTER TABLE %s ENABLE TRIGGER USER" %
                           obj._meta.db_table)
    else:
        obj.save(modeldiff_ignore=True)


def apply_modeldiffs(limit=None):
    qs = Geomodeldiff.objects.filter(applied=False).order_by('date_created')
    qs = qs.exclude(key=settings.MODELDIFF_KEY)

    if limit:
        qs = qs[:limit]

    stats = lambda: None
    stats.rows_processed = 0

    rows = lambda: None
    rows.applied = []
    rows.skipped = []
    models_fields = {}

    for r in qs:
        obj, model = get_current_object_from_db(r)
        geom_field = model.Modeldiff.geom_field
        geom_precision = model.Modeldiff.geom_precision

        old_data = json.loads(r.old_data)
        ok_to_apply = True

        fields = old_data.keys()

        models_fields[r.model_name] = fields

        current = get_object_values(obj, model)
        
        for k in old_data:
            current_value = current.get(k)

            if k == geom_field:
                # early check to detect precision errors
                if not current_value == old_data[k]:
                    # recreate the geometry and the wkt back again
                    geom = GEOSGeometry(old_data[k])
                    old_data[k] = precision_wkt(geom, geom_precision)
    
            if not unicode(current_value) == unicode(old_data[k]):
                ok_to_apply = False
    
        stats.rows_processed += 1
        r.fields = fields

        if ok_to_apply:
            fields = get_fields(r) or old_data.keys()
            new_data = json.loads(r.new_data)
            for k in set(fields) & set(new_data.keys()):
                setattr(obj, k, new_data[k])
            save_object(obj)
            r.applied = True
            r.save()
            rows.applied.append(r)
        else:
            rows.skipped.append(r)

    result = {
        'qs': qs,
        'models_fields': models_fields,
        'rows_applied': rows.applied,
        'rows_skipped': rows.skipped,
        'stats': stats.__dict__
    }

    return result
