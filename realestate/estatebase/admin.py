from django.contrib import admin
from models import Region, Locality, Microdistrict, Street, Estate, EstateType, EstateTypeCategory
from django.contrib.contenttypes.models import ContentType
from orderedmodel.admin import OrderedModelAdmin
from estatebase.models import ClientType, Client, ContactType, Origin, Contact,\
    ContactState, ContactHistory, Bidg, EstateStatus, Document, EstateParam

class StreetAdmin(admin.ModelAdmin):
    list_filter = ('locality',)
    raw_id_admin = ('locality',)
    search_fields = ['name',]

class EstateTypeline(admin.TabularInline):
    model = EstateType

class EstateTypeAdmin(OrderedModelAdmin):
    list_display = ['name', 'reorder']
    list_filter = ('estate_type_category',)
    raw_id_admin = ('estate_type_category',)

class EstateTypeCategoryAdmin(OrderedModelAdmin):
    list_display = ['name', 'reorder']
    inlines = [
        EstateTypeline,
    ]

class EstateParamAdmin(OrderedModelAdmin):
    list_display = ['name', 'reorder']

admin.site.register(Region)
admin.site.register(Locality)
admin.site.register(Microdistrict)
admin.site.register(Street, StreetAdmin)
admin.site.register(ContentType)
admin.site.register(Estate)
admin.site.register(EstateType,EstateTypeAdmin)
admin.site.register(EstateTypeCategory,EstateTypeCategoryAdmin)

admin.site.register(ClientType)
admin.site.register(Client)
admin.site.register(ContactType)
admin.site.register(Origin)
admin.site.register(Contact)
admin.site.register(ContactState)
admin.site.register(ContactHistory)
admin.site.register(Bidg)
admin.site.register(EstateStatus)
admin.site.register(Document)
admin.site.register(EstateParam,EstateParamAdmin)