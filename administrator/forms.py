from django import forms
from .models import Item, ItemType, ItemImage, Partnership

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
            'remarks',
        ]

    def clean_property_number(self):
        property_number = self.cleaned_data.get('property_number')
        # Check for duplicates, excluding the current item (for updates)
        existing_items = Item.objects.filter(property_number=property_number)
        if self.instance.pk:  # If editing an existing item
            existing_items = existing_items.exclude(pk=self.instance.pk)
        if existing_items.exists():
            raise forms.ValidationError("An item with this property number already exists.")
        return property_number


class ItemTypeForm(forms.ModelForm):
    class Meta:
        model = ItemType
        fields = ['name', 'image']

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image', 'caption']  # Include any other fields as needed

class PartnershipForm(forms.ModelForm):
    url = forms.URLField(required=False)  # Make URL field optional

    class Meta:
        model = Partnership
        fields = ['continent', 'country', 'partner', 'type_of_organization', 'description', 'logo', 'status', 'url']
