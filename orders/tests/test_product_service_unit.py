from unittest import TestCase
from unittest.mock import Mock

from orders.models import Product
from orders.services.product_service import ProductService


class ProductServiceTests(TestCase):
    def test_notify_delay_saves_product_and_sends_notification(self):
        product = Product(
            name="RJ45 Cable",
            type="NORMAL",
            available=0,
            lead_time=15,
        )
        repository = Mock()
        notifications = Mock()
        service = ProductService(repository, notifications)

        service.notify_delay(product.lead_time, product)

        self.assertEqual(product.available, 0)
        repository.save.assert_called_once_with(product)
        notifications.send_delay_notification.assert_called_once_with(
            15, "RJ45 Cable"
        )
