# Architecture

## Project map

```text
.
├── README.md
├── docs/                              # project documentation
├── manage.py                          # Django management entry point
├── merjane/                           # Django project configuration
│   ├── settings.py                    # apps, middleware, database, templates
│   ├── urls.py                        # admin and order-processing routes
│   ├── asgi.py                        # ASGI server entry point
│   └── wsgi.py                        # WSGI server entry point
├── orders/                            # order-processing Django app
│   ├── admin.py                       # admin registrations (currently empty)
│   ├── apps.py                        # app configuration
│   ├── models.py                      # conventional Django model exports
│   ├── urls.py                        # app-level order route
│   ├── views.py                       # HTTP request and response handling
│   ├── dto/product.py                 # process-order response object
│   ├── entities/order.py              # Order model definition
│   ├── entities/product.py            # Product model definition
│   ├── repositories/                  # Django ORM access
│   ├── services/                      # order and product use cases
│   ├── migrations/                    # database schema migrations
│   └── tests/                         # endpoint and service tests
└── requirements.txt                   # Python dependencies
```

`__init__.py` files mark Python packages. Django imports models from `orders/models.py`. That module exports the existing model definitions from `orders/entities/`, so imports remain compatible and the protected Order class definition stays unchanged. The Order, response DTO, and notification service files include exercise constraints marked with `WARN` comments. Preserve those protected class definitions during the exercise.

## Request flow

```text
POST /orders/<id>/processOrder
        ↓
merjane/urls.py → orders/urls.py
        ↓
orders/views.py:process_order
        ↓
services/factory.py builds the service dependencies
        ↓
OrderProcessingService loads the order and coordinates processing
        ↓
ProductService applies product-specific rules
        ├── repositories read and save Django models
        └── NotificationService receives notification calls
        ↓
JSON response containing the order ID
```

## Layer responsibilities

- **URLs and views:** map the HTTP route, handle the request, invoke the order use case, and return the response.
- **Services:** coordinate order processing and own product availability decisions.
- **Repositories:** isolate Django ORM reads and writes.
- **Entities and models:** represent persisted Order and Product data.
- **DTO:** represents the process-order response data.
- **Factory:** constructs the production services and injects their repositories and collaborators.

Services receive repositories and notification services through constructors. `OrderProcessingService` captures the date once at the start of each order and passes it into product rules. Tests can therefore supply mocks and a fixed date without patching dependencies inside service modules.

The notification methods currently have empty bodies, so tests mock them to verify when a notification would be requested. The endpoint uses Django's `JsonResponse` and the existing `ProcessOrderResponse` DTO. Django REST Framework is not a dependency, so there is no separate serializer layer.
