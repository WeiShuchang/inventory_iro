from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from administrator.models import ItemType, Item

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