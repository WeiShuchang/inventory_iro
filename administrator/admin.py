from django.contrib import admin
from .models import Item, ItemType, ItemImage, Partnership, PartnershipFiles, Expenditure, Year, InternationalVisitor, Purpose, Center, Sector, Office

# Register your models here.
admin.site.register(Item)
admin.site.register(ItemType)
admin.site.register(ItemImage)
admin.site.register(Partnership)
admin.site.register(PartnershipFiles)
admin.site.register(Expenditure)
admin.site.register(Year)
admin.site.register(InternationalVisitor)
admin.site.register(Sector)
admin.site.register(Office)
admin.site.register(Purpose)
admin.site.register(Center)


