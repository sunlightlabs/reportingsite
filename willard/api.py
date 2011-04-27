from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from willard.models import ForeignLobbying

class ForeignLobbyingResource(ModelResource):
    class Meta:
        model = ForeignLobbying
        queryset = model.objects.all()
        model_fields = [x.name for x in model._meta.fields]
        ordering = model_fields
        filtering = dict([(x, ALL) for x in model_fields])
