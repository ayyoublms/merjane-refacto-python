"""Expose the app's models through Django's conventional models module."""

from .entities.order import Order
from .entities.product import Product

__all__ = ["Order", "Product"]
