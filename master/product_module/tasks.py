from celery import shared_task
from product_module.models import ProductVisit, Like, DisLike


@shared_task(queue="tasks")
def product_visited(product_id, user_ip, user_id):
    try:
        ProductVisit.objects.create(product_id=product_id, ip=user_ip, user_id=user_id)
        return {"ProductVisit": False}
    except Exception as e:
        return {"ProductVisit": False, "error": str(e)}


@shared_task(queue="tasks")
def comment_created(comment_id):
    Like.objects.create(comment_id=comment_id)
    DisLike.objects.create(comment_id=comment_id)
    return {"CommentCreated": True}