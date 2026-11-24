from datetime import date, timedelta
from unittest import TestCase, main
from unittest.mock import Mock

from orders.models import Product
from orders.services.product_service import ProductService


class ProductServiceTests(TestCase):
    today = date(2025, 6, 15)

    def create_service(self):
        repository = Mock()
        notifications = Mock()
        service = ProductService(
            product_repository=repository,
            notification_service=notifications,
        )
        return service, repository, notifications

    def test_notify_delay_saves_product_and_sends_notification(self):
        product = Product(
            name="RJ45 Cable",
            type="NORMAL",
            available=0,
            lead_time=15,
        )
        service, repository, notifications = self.create_service()
        service.notify_delay(product.lead_time, product)

        self.assertEqual(product.available, 0)
        self.assertEqual(product.lead_time, 15)
        repository.save.assert_called_once_with(product)
        notifications.send_delay_notification.assert_called_once_with(
            15, "RJ45 Cable"
        )

    def test_process_normal_product_with_stock_decrements_and_saves(self):
        product = Product(
            name="RJ45 Cable",
            type="NORMAL",
            available=2,
            lead_time=15,
        )
        service, repository, notifications = self.create_service()

        service.process_product(product, self.today)

        self.assertEqual(product.available, 1)
        repository.save.assert_called_once_with(product)
        notifications.send_delay_notification.assert_not_called()

    def test_process_out_of_stock_normal_product_notifies_delay(self):
        product = Product(
            name="RJ45 Cable",
            type="NORMAL",
            available=0,
            lead_time=15,
        )
        service, repository, notifications = self.create_service()

        service.process_product(product, self.today)

        self.assertEqual(product.available, 0)
        repository.save.assert_called_once_with(product)
        notifications.send_delay_notification.assert_called_once_with(
            15, "RJ45 Cable"
        )

    def test_late_seasonal_arrival_is_zeroed_and_notified(self):
        product = Product(
            name="Watermelon",
            type="SEASONAL",
            available=0,
            lead_time=11,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today + timedelta(days=10),
        )
        service, repository, notifications = self.create_service()
        service.process_product(product, self.today)

        self.assertEqual(product.available, 0)
        repository.save.assert_called_once_with(product)
        notifications.send_out_of_stock_notification.assert_called_once_with(
            "Watermelon"
        )
        notifications.send_delay_notification.assert_not_called()

    def test_seasonal_product_before_season_stays_in_stock(self):
        product = Product(
            name="Grapes",
            type="SEASONAL",
            available=3,
            lead_time=2,
            season_start_date=self.today + timedelta(days=5),
            season_end_date=self.today + timedelta(days=10),
        )
        service, repository, notifications = self.create_service()
        service.process_product(product, self.today)

        self.assertEqual(product.available, 3)
        repository.save.assert_called_once_with(product)
        notifications.send_out_of_stock_notification.assert_called_once_with(
            "Grapes"
        )
        notifications.send_delay_notification.assert_not_called()

    def test_seasonal_arrival_on_end_date_notifies_delay(self):
        product = Product(
            name="Watermelon",
            type="SEASONAL",
            available=0,
            lead_time=10,
            season_start_date=self.today - timedelta(days=10),
            season_end_date=self.today + timedelta(days=10),
        )
        service, repository, notifications = self.create_service()
        service.process_product(product, self.today)

        self.assertEqual(product.available, 0)
        repository.save.assert_called_once_with(product)
        notifications.send_delay_notification.assert_called_once_with(
            10, "Watermelon"
        )
        notifications.send_out_of_stock_notification.assert_not_called()

    def test_unexpired_product_with_stock_is_decremented(self):
        product = Product(
            name="Butter",
            type="EXPIRABLE",
            available=2,
            expiry_date=self.today + timedelta(days=1),
        )
        service, repository, notifications = self.create_service()
        service.process_product(product, self.today)

        self.assertEqual(product.available, 1)
        repository.save.assert_called_once_with(product)
        notifications.send_expiry_notification.assert_not_called()

    def test_expired_product_is_zeroed_and_notified(self):
        product = Product(
            name="Butter",
            type="EXPIRABLE",
            available=2,
            expiry_date=self.today - timedelta(days=1),
        )
        service, repository, notifications = self.create_service()
        service.process_product(product, self.today)

        self.assertEqual(product.available, 0)
        repository.save.assert_called_once_with(product)
        notifications.send_expiry_notification.assert_called_once_with(
            "Butter"
        )

    def test_unexpired_stockout_uses_existing_behavior(self):
        product = Product(
            name="Butter",
            type="EXPIRABLE",
            available=0,
            expiry_date=self.today + timedelta(days=365),
        )
        service, repository, notifications = self.create_service()
        service.process_product(product, self.today)

        self.assertEqual(product.available, 0)
        repository.save.assert_called_once_with(product)
        notifications.send_expiry_notification.assert_called_once_with(
            "Butter"
        )


if __name__ == "__main__":
    main()
