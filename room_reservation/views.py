from django.shortcuts import render, redirect
from .forms import ReservationForm
from django.contrib import messages
from .models import Room, Reservation

def book_room(request):
    form = ReservationForm()
    rooms = Room.objects.all()  # Fetch all rooms

    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Your room reservation was successful! Please wait for the admnistrator to view your reservation! Thank you!")
                return redirect("book_room")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "home/reservation/book_room.html", {"form": form, "rooms": rooms})


def pending_reservations(request):
    pending_requests = Reservation.objects.filter(status="Pending").order_by("-created_at")
    return render(request, "administrator/reservation/pending_requests.html", {"pending_requests": pending_requests})