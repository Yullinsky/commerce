from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    wishlist = models.ManyToManyField('Listing', blank=True, related_name="wishlisted_by")

class Listing(models.Model) :
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.CharField (max_length=100, blank=True, null=True)
    is_active = models.BooleanField (default=True)

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    timestamp = models.DateField(auto_now_add=True)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField (max_length=1000)
    listings = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateField(auto_now_add=True)     