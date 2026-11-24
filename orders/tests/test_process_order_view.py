from datetime import date, timedelta
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from orders.models import Order, Product
from orders.repositories.order_repository import OrderRepository
from orders.repositories.product_repository import ProductRepository
from orders.services.order_processing_service import OrderProcessingService
from orders.services.product_service import ProductService


class ProcessOrderViewTests(TestCase):
    today = date(2025, 6, 15)

    def build_processing_service(self, notifications):
        product_repository = ProductRepository()
        product_service = ProductService(
            product_repository=product_repository,
            notification_service=notifications,
        )
        return OrderProcessingService(
            order_repository=OrderRepository(),
            product_service=product_service,
            today_provider=lambda: self.today,
        )

    def process_product(self, product):
        order = Order.objects.create()
        order.products.add(product)
        notifications = Mock()
        service = self.build_processing_service(notifications)

        with patch(
            "orders.views.build_order_processing_service", return_value=service
        ):
            response = self.client.post(
                reverse("process_order", args=[order.pk]),
                content_type="application/json",
            )

        product.refresh_from_db()
        return response, product, notifications, order

    def test_normal_product_in_stock_decrements_without_notification(self):
        product = Product.objects.create(
            name="USB Cable", type="NORMAL", available=2, lead_time=5
        )

        response, product, ns, order = self.process_product(product)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": order.pk})
        self.assertEqual(product.available, 1)
        ns.send_delay_notification.assert_not_called()
        ns.send_out_of_stock_notification.assert_not_called()
        ns.send_expiry_notification.assert_not_called()

    def test_normal_out_of_stock_notifies_with_positive_lead_time(self):
        product = Product.objects.create(
            name="USB Cable", type="NORMAL", available=0, lead_time=5
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_delay_notification.assert_called_once_with(5, "USB Cable")

    def test_normal_out_of_stock_with_zero_lead_does_not_notify(self):
        product = Product.objects.create(
            name="USB Cable", type="NORMAL", available=0, lead_time=0
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_delay_notification.assert_not_called()

    def test_mixed_order_processes_products_and_returns_order_id(self):
        normal = Product.objects.create(
            name="USB Cable", type="NORMAL", available=2, lead_time=5
        )
        seasonal = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=0,
            lead_time=11,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today + timedelta(days=10),
        )
        expirable = Product.objects.create(
            name="Butter",
            type="EXPIRABLE",
            available=2,
            expiry_date=self.today - timedelta(days=1),
        )
        order = Order.objects.create()
        order.products.add(normal, seasonal, expirable)
        notifications = Mock()
        service = self.build_processing_service(notifications)

        with patch(
            "orders.views.build_order_processing_service", return_value=service
        ):
            response = self.client.post(
                reverse("process_order", args=[order.pk]),
                content_type="application/json",
            )

        normal.refresh_from_db()
        seasonal.refresh_from_db()
        expirable.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": order.pk})
        self.assertEqual(normal.available, 1)
        self.assertEqual(seasonal.available, 0)
        self.assertEqual(expirable.available, 0)
        notifications.send_out_of_stock_notification.assert_called_once_with(
            "Watermelon"
        )
        notifications.send_expiry_notification.assert_called_once_with(
            "Butter"
        )

    def test_seasonal_product_in_season_with_stock_decrements(self):
        product = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=2,
            lead_time=5,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today + timedelta(days=10),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 1)
        ns.send_delay_notification.assert_not_called()
        ns.send_out_of_stock_notification.assert_not_called()

    def test_seasonal_out_of_stock_before_end_notifies_delay(self):
        product = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=0,
            lead_time=5,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today + timedelta(days=10),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_delay_notification.assert_called_once_with(5, "Watermelon")
        ns.send_out_of_stock_notification.assert_not_called()

    def test_seasonal_out_of_stock_arriving_on_season_end_notifies_delay(self):
        product = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=0,
            lead_time=10,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today + timedelta(days=10),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_delay_notification.assert_called_once_with(10, "Watermelon")
        ns.send_out_of_stock_notification.assert_not_called()

    def test_seasonal_late_arrival_notifies_unavailable(self):
        product = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=0,
            lead_time=11,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today + timedelta(days=10),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_out_of_stock_notification.assert_called_once_with("Watermelon")
        ns.send_delay_notification.assert_not_called()

    def test_seasonal_before_season_notifies_and_keeps_stock(self):
        product = Product.objects.create(
            name="Grapes",
            type="SEASONAL",
            available=2,
            lead_time=5,
            season_start_date=self.today + timedelta(days=3),
            season_end_date=self.today + timedelta(days=10),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 2)
        ns.send_out_of_stock_notification.assert_called_once_with("Grapes")

    def test_seasonal_before_season_with_late_arrival_zeroes_stock(self):
        product = Product.objects.create(
            name="Grapes",
            type="SEASONAL",
            available=2,
            lead_time=11,
            season_start_date=self.today + timedelta(days=3),
            season_end_date=self.today + timedelta(days=10),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_out_of_stock_notification.assert_called_once_with("Grapes")

    def test_seasonal_first_day_uses_existing_behavior(self):
        product = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=2,
            lead_time=5,
            season_start_date=self.today,
            season_end_date=self.today + timedelta(days=10),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 2)
        ns.send_delay_notification.assert_called_once_with(5, "Watermelon")

    def test_seasonal_last_day_uses_existing_behavior(self):
        product = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=2,
            lead_time=5,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today,
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_out_of_stock_notification.assert_called_once_with("Watermelon")

    def test_seasonal_product_after_season_is_marked_unavailable(self):
        product = Product.objects.create(
            name="Watermelon",
            type="SEASONAL",
            available=2,
            lead_time=5,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today - timedelta(days=1),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_out_of_stock_notification.assert_called_once_with("Watermelon")

    def test_expirable_product_in_stock_before_expiry_decrements(self):
        product = Product.objects.create(
            name="Butter",
            type="EXPIRABLE",
            available=2,
            expiry_date=self.today + timedelta(days=1),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 1)
        ns.send_expiry_notification.assert_not_called()

    def test_expirable_product_expiring_today_uses_existing_behavior(self):
        product = Product.objects.create(
            name="Butter",
            type="EXPIRABLE",
            available=2,
            expiry_date=self.today,
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_expiry_notification.assert_called_once_with("Butter")

    def test_expirable_product_expired_yesterday_is_zeroed_and_notifies(self):
        product = Product.objects.create(
            name="Butter",
            type="EXPIRABLE",
            available=2,
            expiry_date=self.today - timedelta(days=1),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_expiry_notification.assert_called_once_with("Butter")

    def test_expirable_stockout_uses_existing_behavior(self):
        product = Product.objects.create(
            name="Butter",
            type="EXPIRABLE",
            available=0,
            expiry_date=self.today + timedelta(days=365),
        )

        _, product, ns, _ = self.process_product(product)

        self.assertEqual(product.available, 0)
        ns.send_expiry_notification.assert_called_once_with("Butter")
