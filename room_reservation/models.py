from django.db import models

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, choices=[("Single", "Single"), ("Double", "Double"), ("Suite", "Suite"), ("Hall", "Hall")])
    is_available = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField()  # Number of people it can accommodate
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="rooms/", null=True, blank=True)

    def __str__(self):
        return f"{self.room_type} - {self.room_number}"
class Reservation(models.Model):
    first_name = models.CharField(max_length=255)  # Guest's first name
    last_name = models.CharField(max_length=255)  # Guest's last name
    college_office_institution = models.CharField(max_length=255, blank=True, null=True)  # Institution/Organization
    email = models.EmailField()  # Guest's email
    phone_number = models.CharField(max_length=20)  # Contact number

    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="reservations")
    arrival_date = models.DateField()
    arrival_time = models.TimeField()
    departure_date = models.DateField()
    departure_time = models.TimeField()

    details = models.TextField(blank=True, null=True)  # Additional booking details
    special_request = models.TextField(blank=True, null=True)  # Special requests (e.g., early check-in)
    reason_for_cancelling = models.TextField(blank=True, null=True)  # Reason for cancellation
    cancelled_by = models.CharField(max_length=50, blank=True, null=True)  # Who cancelled (admin/user)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Confirmed", "Confirmed"),
            ("Cancelled", "Cancelled"),
            ("Completed", "Completed"),
        ],
        default="Pending",
    )

    # New timestamp fields
    cancelled_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the reservation was made
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update

    def __str__(self):
        return f"Reservation {self.id} - {self.first_name} {self.last_name} ({self.status})"
