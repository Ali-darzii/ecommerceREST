from celery import shared_task
from product_module.models import ProductVisit


@shared_task(queue="tasks")
def product_visited(product_id, user_ip, user_id):
    try:
        ProductVisit.objects.create(product_id=product_id, ip=user_ip, user_id=user_id)
        return {"ProductVisit": False}
    except Exception as e:
        return {"ProductVisit": False, "error": str(e)}
