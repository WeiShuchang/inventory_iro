from django import forms
from .models import Item, ItemType, ItemImage, Partnership, Expenditure

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

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = [
            'classification', 'expenditure_type', 'description', 'mode_of_procurement',
            'quarter1', 'quarter2', 'quarter3', 'quarter4', 'unit_of_measure',
            'unit_price', 'remarks', 'year'
        ]
        widgets = {
            'classification': forms.Select(attrs={'class': 'form-control'}),
            'expenditure_type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mode_of_procurement': forms.TextInput(attrs={'class': 'form-control'}),
            'quarter1': forms.NumberInput(attrs={'class': 'form-control'}),
            'quarter2': forms.NumberInput(attrs={'class': 'form-control'}),
            'quarter3': forms.NumberInput(attrs={'class': 'form-control'}),
            'quarter4': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'year': forms.Select(attrs={'class': 'form-control'})
        }
