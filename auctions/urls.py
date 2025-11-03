from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create-listing"),
    path("listing/<int:listing_id>/", views.listing_view, name="listing"),
    path("wishlist", views.wishlist, name="wishlist"),
    path("wishlist/<int:listing_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("listing/<int:listing_id>/bid/", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/comment/", views.add_comment, name="add_comment"),
    path("category-list", views.category_list, name="category-list"),
    path("categories/<str:category_name>/", views.category_view, name="category"),
]   
