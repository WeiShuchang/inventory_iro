from django.contrib import admin
from .models import Item, ItemType, ItemImage, Partnership, PartnershipFiles, Expenditure

# Register your models here.
admin.site.register(Item)
admin.site.register(ItemType)
admin.site.register(ItemImage)
admin.site.register(Partnership)
admin.site.register(PartnershipFiles)
admin.site.register(Expenditure)


