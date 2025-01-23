from django import forms
from .models import Item, ItemType, ItemImage

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'sector_office_division_college',
            'operating_unit_project',
            'property_number',
            'responsible_person',
            'quantity',
            'unit',
            'item_type',
            'description',
            'date_acquired',
            'fund',
            'ppe_class',
            'estimated_useful_life',
            'unit_price',
            'total_amount',
            'remarks'
        ]

class ItemTypeForm(forms.ModelForm):
    class Meta:
        model = ItemType
        fields = ['name', 'image']

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image', 'caption']  # Include any other fields as needed