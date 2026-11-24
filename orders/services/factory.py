from ..repositories.order_repository import OrderRepository
from ..repositories.product_repository import ProductRepository
from .notification_service import NotificationService
from .order_processing_service import OrderProcessingService
from .product_service import ProductService


def build_order_processing_service():
    product_repository = ProductRepository()
    product_service = ProductService(
        product_repository=product_repository,
        notification_service=NotificationService(),
    )
    return OrderProcessingService(
        order_repository=OrderRepository(),
        product_service=product_service,
    )
