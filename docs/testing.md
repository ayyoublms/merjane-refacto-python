# Tests and coverage

## Test suite

Run all tests from the repository root:

```bash
python manage.py test
```

`orders/tests/test_process_order_view.py` exercises the endpoint with products stored in the test database. It checks stock changes, response JSON, mixed orders, and notification calls across product types and date cases.

`orders/tests/test_product_service_unit.py` calls `ProductService` directly and mocks the repository and notification service. It checks product saves, availability changes, and notification calls for seasonal and expirable branches, as well as delay notifications.

The tests use a fixed date for seasonal and expiry scenarios, so results do not depend on the day they run. Some assertions intentionally capture current behavior where the brief is ambiguous. Revisit those assertions if the intended rules are clarified; see [Business rules](business-rules.md).

## Coverage report

Install the project dependencies first, then run:

```bash
coverage run --branch --source=orders --omit='orders/tests/*,orders/migrations/*' manage.py test
coverage report -m
coverage html
```

Open `htmlcov/index.html` to browse the detailed report. Coverage indicates which code was executed; assertions are still needed to verify outcomes.
