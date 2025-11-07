from django.contrib.auth.models import AbstractUser
from django.db import models

from decimal import Decimal


class User(AbstractUser):
    wishlist = models.ManyToManyField('Listing', blank=True, related_name="wishlisted_by")

class Listing(models.Model) :
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    image_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    winner = models.ForeignKey(User,on_delete=models.SET_NULL, blank=True, null=True, related_name="auctions_won")
    category = models.CharField (max_length=100, blank=True, null=True)
    is_active = models.BooleanField (default=True)

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField (max_length=1000)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']