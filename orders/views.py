from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .dto.product import ProcessOrderResponse
from .services.factory import build_order_processing_service


@csrf_exempt
@require_POST
def process_order(request, order_id):
    service = build_order_processing_service()
    processed_order_id = service.process(order_id)
    response = ProcessOrderResponse(processed_order_id)
    return JsonResponse({"id": response.id}, status=200)
