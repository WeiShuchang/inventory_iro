from django.db import models

class ItemType(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='item_types/', blank=True, null=True)  # Image field added

    def __str__(self):
        return self.name
    
class Item(models.Model):
    sector_office_division_college = models.CharField(max_length=200)  
    operating_unit_project = models.CharField(max_length=200, default="IRO")
    property_number = models.CharField(max_length=100)
    responsible_person = models.CharField(max_length=200, default="BAWANG, Rex John G.")
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)  # No choices
    item_type = models.ForeignKey(ItemType, on_delete=models.RESTRICT)
    description = models.TextField(max_length=1000)
    date_acquired = models.DateField()
    fund = models.CharField(max_length=100)
    ppe_class = models.CharField(max_length=100)
    estimated_useful_life = models.IntegerField(help_text="Estimated useful life in years")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_archived = models.BooleanField(default=False)  # Archived status
    remarks = models.TextField(max_length=500, blank=True, null=True)  # New remarks field

    def __str__(self):
        return f"{self.operating_unit_project} - {self.property_number}"

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

    def __str__(self):
        return f"{self.partner} ({self.country})"

class PartnershipFiles(models.Model):
    partnership = models.ForeignKey(Partnership, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='partnership_files/')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"File for {self.partnership.partner}: {self.file.name}"