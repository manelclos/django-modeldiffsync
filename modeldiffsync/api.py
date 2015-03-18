import json

from django.conf import settings
from django.db.models.loading import get_model
from django.forms.models import model_to_dict
from django.contrib.gis.utils.wkt import precision_wkt
from django.contrib.gis.geos import GEOSGeometry

from restless.views import Endpoint
from restless.modelviews import ListEndpoint, DetailEndpoint
from restless.models import serialize
from restless.http import HttpError, Http200, Http201


from modeldiff.models import Geomodeldiff


class GeomodeldiffList(ListEndpoint):
    model = Geomodeldiff

    def get_query_set(self, request, *args, **kwargs):
        last_id = request.GET.get('last_id', 0)
        limit = request.GET.get('limit', 0)

        if self.model:
            queryset = (
                self.model.objects.all()
                .filter(key=settings.MODELDIFF_KEY)
                .filter(pk__gt=last_id)
                .order_by('id')
            )
            if limit > 0:
                queryset = queryset[:limit]
            return queryset
        else:
            raise HttpError(404, 'Resource Not Found')

    def serialize(self, objs):
        return serialize(objs, exclude=('applied',))

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        qs = Geomodeldiff.objects.filter(key=data['key'],
                                         key_id=data['key_id'])
        if qs.count() == 0:
            obj = Geomodeldiff(**data)
            try:
                obj.save()
                return Http201(self.serialize(obj))
            except:
                raise HttpError(400, 'Invalid Data')
        else:
            print 'Already exists!'
            print 'key=%s, key_id=%s' % (data['key'], data['key_id'])
            return Http200('Already exists!')


class Update(Endpoint):
    def get(self, request):
        qs = Geomodeldiff.objects.filter(applied=False)
        qs = qs.exclude(key=settings.MODELDIFF_KEY)

        sync_conf = getattr(settings, 'MODELDIFFSYNC_CONF', {})

        for r in qs:
            model = get_model(*r.model_name.rsplit('.', 1))
            geom_field = model.Modeldiff.geom_field
            geom_precision = model.Modeldiff.geom_precision
            unique_field = getattr(model.Modeldiff, 'unique_field', None)

            if unique_field:
                kwargs = {unique_field: r.unique_id}
                obj = model.objects.get(**kwargs)
            else:
                obj = model.objects.get(pk=r.model_id)
            
            print obj
            old_data = json.loads(r.old_data)
            ok_to_apply = True

            conf = sync_conf.get(r.key, None)
            fields = None
            if conf:
                fields = conf.get(r.model_name, None)
            if not fields:
                fields = old_data.keys()
 
            current = model_to_dict(obj)
            for k in old_data:
                current_value = current.get(k)

                if k == geom_field:
                    geom = getattr(obj, geom_field)
                    current_value = precision_wkt(geom, geom_precision)
                    # early check to detect precision errors
                    if not current_value == old_data[k]:
                        # recreate the geometry and the wkt back again
                        geom = GEOSGeometry(old_data[k])
                        old_data[k] = precision_wkt(geom, geom_precision)

                if not current_value == old_data[k]:
                    print "BAD PREVIOUS STATUS: %s => %s == %s" % (k, old_data[k], current_value)
                    ok_to_apply = False
                else:
                    print '%s OK' % k

            print "OK_TO_APPLY:", ok_to_apply
            if ok_to_apply:
                new_data = json.loads(r.new_data)
                for k in fields:
                    setattr(obj, k, new_data[k])
                obj.save(modeldiff_ignore=True)
                r.applied = True
                r.save()

        return serialize(qs, exclude=('the_geom'))
