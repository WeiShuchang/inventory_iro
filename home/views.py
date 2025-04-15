from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib import messages
from administrator.models import ItemType, Item, Partnership
from room_reservation.models import Room, Reservation
from .forms import ReservationForm
import json
from django.core.serializers.json import DjangoJSONEncoder



# Create your views here.
def landing_page_view(request):
    return render(request, "home/landing_page.html")


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use 'username' instead of 'email'
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect('administrator_dashboard')  # Adjust 'home:index' to your dashboard/home page
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'home/login_page.html')

def item_types_list(request):
    """View to display all item types."""
    item_types = ItemType.objects.all().order_by("name")
    return render(request, 'home/list_of_item_types.html', {'item_types': item_types})


def item_type_detail(request, pk):
    item_type = get_object_or_404(ItemType, pk=pk)
    items = Item.objects.filter(item_type=item_type, is_archived=False)
    items_with_images = []
    for item in items:
        # Select one image or None if no images are found
        image = item.images.first()
        items_with_images.append({
            'item': item,
            'image_url': image.image.url if image else None,
        })
    context = {
        'item_type': item_type,
        'items_with_images': items_with_images,
    }
    return render(request, 'home/item_detail.html', context)

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {
        'item': item,
        'images': item.images.all()  # Fetch related images using the related_name
    }
    return render(request, 'home/item_information.html', context)


def partnership_list(request):
    # Fetch all partnerships that are not removed from the list
    partnerships = Partnership.objects.filter(is_removed_from_list=False).order_by("continent", "country")

    # Filter active partnerships for marquee
    active_partnerships = partnerships.filter(status="Active").exclude(logo="")

    # Organize partnerships by continent
    continents = {}
    for partnership in partnerships:
        if partnership.continent not in continents:
            continents[partnership.continent] = []
        continents[partnership.continent].append(partnership)

    # Pass the grouped partnerships and active partnerships to the template
    return render(
        request, 
        "home/international_partners_list.html", 
        {'continents': continents, 'active_partnerships': active_partnerships}
    )

def book_room(request):
    form = ReservationForm()
    rooms = Room.objects.all()

    # Get all reservations for each room
    room_reservations = {}
    for room in rooms:
        reservations = Reservation.objects.filter(
            room=room,
            status__in=["Confirmed"]
        ).values_list('arrival_date', 'departure_date')

        # Convert dates to ISO format strings for JSON serialization
        room_reservations[room.id] = [
            [arrival.isoformat(), departure.isoformat()]
            for arrival, departure in reservations
        ]

    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = form.save()

                # Email details
                subject_admin = "New Room Reservation Submitted"
                subject_guest = "Your Room Reservation Was Received"
                from_email = settings.DEFAULT_FROM_EMAIL
                admin_email = settings.EMAIL_HOST_USER
                guest_email = reservation.email

                # Render email templates
                admin_html = render_to_string("emails/reservation_notification.html", {
                    "reservation": reservation
                })
                guest_html = render_to_string("emails/guest_confirmation.html", {
                    "reservation": reservation
                })

                # Plain text fallback
                text_content = f"Reservation by {reservation.first_name} {reservation.last_name} for room {reservation.room}"

                # Send email to admin
                admin_msg = EmailMultiAlternatives(subject_admin, text_content, from_email, [admin_email])
                admin_msg.attach_alternative(admin_html, "text/html")
                admin_msg.send()

                # Send email to guest
                guest_msg = EmailMultiAlternatives(subject_guest, text_content, from_email, [guest_email])
                guest_msg.attach_alternative(guest_html, "text/html")
                guest_msg.send()

                messages.success(request, "Your room reservation was successful! Please wait for the administrator to view your reservation! Thank you!")
                return redirect("book_room")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "home/reservation/book_room.html", {
        "form": form,
        "rooms": rooms,
        "room_reservations": json.dumps(room_reservations, cls=DjangoJSONEncoder),
    })