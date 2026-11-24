# Refactoring history

This page records the changes made during the exercise and their intent.

- Renamed the generic view test file to `test_process_order_view.py` and added endpoint scenarios for normal, seasonal, expirable, and mixed orders.
- Expanded `test_product_service_unit.py` to cover seasonal and expirable service branches as well as delay notifications.
- Added `orders/models.py` as Django's conventional model import point while preserving protected model definitions in `orders/entities/`.
- Moved the route to `orders/urls.py`, the view to `orders/views.py`, and order orchestration into `OrderProcessingService`.
- Flattened the services package by moving service modules out of the redundant `implementations/` subfolder.
- Replaced module-level repository and service singletons with constructor injection. Added `services/factory.py` as the explicit dependency-wiring point, and updated tests to supply mocks directly.
- Captured the processing date once per order and passed it into seasonal and expiry product rules.
- Centralized NORMAL, SEASONAL, and EXPIRABLE decisions in `ProductService`. `OrderProcessingService` loads the order and delegates each product using the same captured date.
- Preserved the original seasonal and expiry date-boundary behavior in tests. The brief does not define those boundaries, so no new business rule is assumed. See [Business rules](business-rules.md).
- Kept the route path and name unchanged. No serializer package was added because the endpoint returns a small JSON response and the project does not use Django REST Framework.
- The latest full test run found 26 passing tests. Django reported no model migration changes.
