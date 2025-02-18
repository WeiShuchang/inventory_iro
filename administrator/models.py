from django.db import models

class ItemType(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='item_types/', blank=True, null=True)  # Image field added

    def __str__(self):
        return self.name
    
class Item(models.Model):
    sector_office_division_college = models.CharField(max_length=200)
    operating_unit_project = models.CharField(max_length=200, default="IRO")
    property_number = models.CharField(max_length=100,) 
    responsible_person = models.CharField(max_length=200, default="BAWANG, Rex John G.")
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    item_type = models.ForeignKey(ItemType, on_delete=models.RESTRICT)
    description = models.TextField(max_length=1000)
    date_acquired = models.DateField()
    fund = models.CharField(max_length=100)
    ppe_class = models.CharField(max_length=100, null=True, blank=True)
    estimated_useful_life = models.IntegerField(help_text="Estimated useful life in years")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_archived = models.BooleanField(default=False)
    remarks = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.operating_unit_project} - {self.property_number}"

    @property
    def category(self):
        if self.unit_price >= 50000:
            return "Property, Plant and Equipment"
        elif 5000 < self.unit_price < 50000:
            return "High Value Semi-Expendable"
        else:
            return "Low Value Semi-Expendable"

class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/')
    caption = models.CharField(max_length=200, blank=True, null=True)  # Optional caption for the image

    def __str__(self):
        return f"Image for {self.item.property_number}"
    
class Partnership(models.Model):
    CONTINENT_CHOICES = [
        ('Africa', 'Africa'),
        ('South East Asia', 'South East Asia'),
        ('South Asia', 'South Asia'),
        ('East Asia', 'East Asia'),
        ('Europe', 'Europe'),
        ('North America', 'North America'),
        ('South America', 'South America'),
        ('Australia', 'Australia'),
        ('Antarctica', 'Antarctica'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    continent = models.CharField(max_length=50, choices=CONTINENT_CHOICES)
    country = models.CharField(max_length=100)
    partner = models.CharField(max_length=255)
    type_of_organization = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='partner_logos/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    is_removed_from_list = models.BooleanField(default=False)
    url = models.URLField(max_length=510, blank=True, null=True)  # New URL field

    def __str__(self):
        return f"{self.partner} ({self.country})"

class PartnershipFiles(models.Model):
    partnership = models.ForeignKey(Partnership, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='partnership_files/')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"File for {self.partnership.partner}: {self.file.name}"
    

class Year(models.Model):
    year = models.PositiveIntegerField(unique=True)
    description = models.TextField(blank=True, null=True)  # New description field

    def __str__(self):
        return str(self.year)

class Expenditure(models.Model):
    # Classification choices
    CLASSIFICATION_CHOICES = [

        ('Other Items not available at PS DBM but regularly purchased from other sources', 'Other Items not available at PS DBM but regularly purchased from other sources'),
        ('Other Supplies and Materials', 'Other Supplies and Materials'),
        ('Services, Rentals, and Others', 'Services, Rentals, and Others'),
        ('Capital Outlay', 'Capital Outlay'),
    ]

    classification = models.CharField(max_length=200, choices=CLASSIFICATION_CHOICES)
    expenditure_type = models.CharField(max_length=200)
    item_number = models.PositiveIntegerField()  # Logic for unique numbering in the model's save() method
    description = models.TextField()
    mode_of_procurement = models.CharField(max_length=200)

    # Schedule of procurement (one field per quarter)
    quarter1 = models.PositiveIntegerField(default=0)
    quarter2 = models.PositiveIntegerField(default=0)
    quarter3 = models.PositiveIntegerField(default=0)
    quarter4 = models.PositiveIntegerField(default=0)
    
    # Total quantity (calculated dynamically)
    total_quantity = models.PositiveIntegerField(editable=False, default=0)

    unit_of_measure = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Total amount (calculated dynamically)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False, default=0.00)
    
    remarks = models.TextField(blank=True, null=True)

    # Connect to the Year model using a ForeignKey
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate total quantity and total amount before saving
        self.total_quantity = self.quarter1 + self.quarter2 + self.quarter3 + self.quarter4
        self.total_amount = self.total_quantity * self.unit_price

        # Automatically assign item number
        if not self.pk:  # Only assign on create
            similar_items = Expenditure.objects.filter(
                classification=self.classification,
                expenditure_type=self.expenditure_type,
                year=self.year  # Include year in the filter
            ).count()
            self.item_number = similar_items + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.year.year} - {self.classification} - {self.expenditure_type} - Item {self.item_number}"