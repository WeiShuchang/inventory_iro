from django.urls import path, include
from . import views

urlpatterns = [
    path('book-a-room/', views.book_room, name="book_room"),
    path("pending-reservations/", views.pending_reservations, name="pending_reservations"),

]