from datetime import date


class OrderProcessingService:
    def __init__(
        self,
        order_repository,
        product_service,
        today_provider=date.today,
    ):
        self.order_repository = order_repository
        self.product_service = product_service
        self.today_provider = today_provider

    def process(self, order_id):
        order = self.order_repository.find_by_id(order_id).get()
        today = self.today_provider()

        for product in order.get_items():
            self.product_service.process_product(product, today)

        return order.id
