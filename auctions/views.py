from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import User, Listing, Bid, Comment

from decimal import Decimal, InvalidOperation

def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings":listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def category_list(request):
    category_list = Listing.objects.values_list('category', flat=True).distinct()
    return render (request, "auctions/category-list.html",{
        "category_list": category_list
    })

def category_view(request, category_name):
    listings = Listing.objects.filter(category=category_name, is_active=True)
    return render(request, "auctions/category.html",{
        "category": category_name,
        "listings": listings
    })

def create_listing(request):
    if request.method == "POST":
        # 1. Obtener los datos del formulario
        title = request.POST["listing-name"]
        description = request.POST["listing-description"]
        starting_bid_raw = request.POST ["starting-bid"]
        image_url = request.POST.get("url-imagen", "")
        category = request.POST["category"]

        #Convertir y validar el starting_bid
        try:
            starting_bid = Decimal(starting_bid_raw)
        except (InvalidOperation, ValueError):
            messages.error (request, "Invalid starting bid amount.")
            return render (request, "auctions/create-listing.html")

        # 2. Crear el objeto Listing
        listing = Listing(
            title=title,    
            description = description,
            starting_bid = starting_bid,
            bid_amount = starting_bid,
            image_url = image_url,
            category = category,
            owner = request.user
        )

        # 3. Guardar en la base de datos
        listing.save()

        # 4. Redirigir al index (buena práctica después de un POST)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create-listing.html")

@login_required
def close_auction(request, listing_id):
    if request.method != "POST":
        messages.error(request, "Método no permitido.")
        return redirect("listing", listing_id=listing_id)

    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.user != listing.owner:
        messages.error(request, "No tienes permiso para cerrar esta subasta.")
        return redirect("listing", listing_id=listing_id)

    if not listing.is_active:
        messages.error(request, "Esta subasta ya está cerrada.")
        return redirect("listing", listing_id=listing_id)
    
    highest_bid = listing.bids.order_by('-amount').first()
    listing.is_active = False

    if highest_bid:
        listing.winner = highest_bid.bidder
        listing.bid_amount = highest_bid.amount
        messages.success(request, f"Auction closed! The winner is {listing.winner.username} with a bid of ${listing.bid_amount}")
    else:
        listing.winner = None
        messages.success(request, f"Auction closed! There were no bids")
    
    listing.save()
    return redirect("listing", listing_id=listing_id)

@login_required
def place_bid(request, listing_id):
    if request.method == "POST":

        bid_amount_raw = request.POST.get("bid_amount")
        if not bid_amount_raw:
            messages.error(request, "Bid amount is required.")
            return redirect("listing", listing_id=listing_id) 
        
        # 2.1 Convertir y validar la cantidad de puja
        try:
            bid_amount = Decimal(bid_amount_raw)
        except (InvalidOperation, ValueError):
            messages.error(request, "Invalid bid amount.")
            return redirect("listing", listing_id=listing_id)
        
        listing = get_object_or_404(Listing, pk=listing_id)

        # 3. Validar que la puja sea mayor que la puja actual
        if bid_amount <= listing.bid_amount:
            messages.error(request, "Your bid must be higher than the current bid.")
            return redirect("listing", listing_id=listing_id)

        # Actualizar la puja y el Bidder
        bid = Bid(bidder=request.user, listing=listing, amount=bid_amount)
        bid.save()

        listing.bid_amount = bid_amount
        listing.save()

        messages.success(request, "Your bid was placed successfully!")
        return redirect("listing", listing_id=listing_id)
    return redirect("listing", listing_id=listing_id)

def listing_view(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.all() 
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments
    })

@login_required
def wishlist (request):
    wishlisted_listings = request.user.wishlist.all()
    return render(request, "auctions/wishlist.html",{
        "wishlist":wishlisted_listings
    })

@login_required
def toggle_wishlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if listing in request.user.wishlist.all():
        request.user.wishlist.remove(listing)
    else:
        request.user.wishlist.add(listing)

    return redirect("listing", listing_id=listing.id)

@login_required
def add_comment(request, listing_id):
    if request.method == "POST":
        comment_text = request.POST.get("comment_text", "").strip()
        if not comment_text:
            messages.error(request, "Comment cannot be empty.")
            return redirect("listing", listing_id=listing_id)

        listing = get_object_or_404(Listing, pk=listing_id)

        try:
            comment = Comment(
                user=request.user,
                text=comment_text,
                listing=listing
            )
            comment.save()
            messages.success(request, "Your comment was added successfully!")

        except Exception as e:
            messages.error(request, "An error occurred while adding your comment.")
            print(e)

        return redirect("listing", listing_id=listing_id)
    return redirect("listing", listing_id=listing_id)