from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
import datetime

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "first_name", "last_name", "college_office_institution",
            "email", "phone_number", "room",
            "arrival_date", "arrival_time", "departure_date", "departure_time",
            "details", "special_request"
        ]
        widgets = {
            "arrival_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "arrival_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "departure_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "departure_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        arrival_date = cleaned_data.get("arrival_date")
        arrival_time = cleaned_data.get("arrival_time")
        departure_date = cleaned_data.get("departure_date")
        departure_time = cleaned_data.get("departure_time")

        if arrival_date and departure_date:
            if arrival_date > departure_date:
                raise ValidationError("Departure date must be after arrival date.")
            elif arrival_date == departure_date and arrival_time and departure_time:
                if arrival_time >= departure_time:
                    raise ValidationError("Departure time must be after arrival time.")

        return cleaned_data

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        return phone
