from datetime import timedelta


class ProductService:
    def __init__(
        self,
        product_repository,
        notification_service,
    ):
        self.product_repository = product_repository
        self.notification_service = notification_service

    def notify_delay(self, lead_time, p):
        p.lead_time = lead_time
        self.product_repository.save(p)
        self.notification_service.send_delay_notification(lead_time, p.name)

    def process_product(self, product, today):
        if product.type == "NORMAL":
            self._process_normal_product(product)
        elif product.type == "SEASONAL":
            self._process_seasonal_product(product, today)
        elif product.type == "EXPIRABLE":
            self._process_expirable_product(product, today)

    def _process_normal_product(self, product):
        if product.available > 0:
            product.available -= 1
            self.product_repository.save(product)
        elif product.lead_time > 0:
            self.notify_delay(product.lead_time, product)

    def _process_seasonal_product(self, product, today):
        if (
            today > product.season_start_date
            and today < product.season_end_date
            and product.available > 0
        ):
            product.available -= 1
            self.product_repository.save(product)
        else:
            self.handle_seasonal_product(product, today)

    def handle_seasonal_product(self, p, today):
        if today + timedelta(days=p.lead_time) > p.season_end_date:
            self.notification_service.send_out_of_stock_notification(p.name)
            p.available = 0
            self.product_repository.save(p)
        elif p.season_start_date > today:
            self.notification_service.send_out_of_stock_notification(p.name)
            self.product_repository.save(p)
        else:
            self.notify_delay(p.lead_time, p)

    def _process_expirable_product(self, product, today):
        self.handle_expired_product(product, today)

    def handle_expired_product(self, p, today):
        if p.available > 0 and p.expiry_date > today:
            p.available -= 1
            self.product_repository.save(p)
        else:
            p.available = 0
            self.product_repository.save(p)
            self.notification_service.send_expiry_notification(p.name)
