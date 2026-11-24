from django.test import TestCase
from django.urls import reverse

from orders.models import Order, Product


class ProcessOrderViewTests(TestCase):
    def test_normal_product_in_stock_decrements_availability(self):
        product = Product.objects.create(
            name="USB Cable", type="NORMAL", available=2, lead_time=5
        )
        order = Order.objects.create()
        order.products.add(product)

        response = self.client.post(
            reverse("process_order", args=[order.pk]),
            content_type="application/json",
        )

        product.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": order.pk})
        self.assertEqual(product.available, 1)
