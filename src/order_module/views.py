from rest_framework.views import APIView
from rest_framework.response import Response

from discount_module.models import NumberDiscount
from order_module.models import OrderDetail, Order
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from order_module.serializers import OrderDetailSerializer
from utils.Responses import ErrorResponses
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from utils.utils import payment_gateway, rest_of_percentage


# todo: need test !
class MakeOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """ Add or Lower the product has been in basket """

    def get(self, request):
        """ give orders in baskets """
        order_details = OrderDetail.objects.filter(order__user=request.user, order__is_paid=False)
        serializer = OrderDetailSerializer(instance=order_details, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, deside=None, order_detail_id=None):
        """ increase or decrease Product to basket with order_detail pk """

        if order_detail_id is None:
            return Response(data=ErrorResponses.BAD_FORMAT, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_detail = OrderDetail.objects.get(pk=order_detail_id, order__is_paid=False)
        except OrderDetail.DoesNotExist:
            return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        if deside == "increase":
            order_detail.count += 1
        elif deside == "decrease":
            order_detail.count -= 1
            if order_detail.count >= 0:
                order_detail.delete()
        else:
            return Response(data=ErrorResponses.BAD_FORMAT, status=status.HTTP_400_BAD_REQUEST)
        order_detail.order.calculate_final_price()
        order_detail.order.calculate_total_price()
        order_detail.save()
        order_details = OrderDetail.objects.filter(order_id=order_detail_id, order__is_paid=False)
        serializer = OrderDetailSerializer(instance=order_details, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, deside=None, product_id=None):
        """ increase or decrease or create Product to basket with product id """

        try:
            order = Order.objects.get(user=request.user, is_paid=False)
        except Order.DoesNotExist:
            return Response(ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        order_detail, created = OrderDetail.objects.get_or_create(product_id=product_id, order=order)
        if deside == "increase":
            order_detail.count += 1
        elif deside == "increase":
            order_detail.count -= 1
            if order_detail.count == 0:
                order_detail.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data=ErrorResponses.BAD_FORMAT, status=status.HTTP_400_BAD_REQUEST)
        order_detail.order.calculate_final_price()
        order_detail.order.calculate_total_price()
        order_detail.save()
        if created:
            serializer = OrderDetailSerializer(order_detail)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        order_details = OrderDetail.objects.filter(order=order)
        serializer = OrderDetailSerializer(instance=order_details, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

# todo: discount number need test !
@api_view(["POST"])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def payment(request, discount_number):
    """ According to your payment gateway edit payment_gateway function to do your payment """
    order_details = OrderDetail.objects.filter(order__user=request.user, order__is_paid=False)
    if not order_details.exists():
        return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
    try:
        order = Order.objects.get(user=request.user, is_paid=False)
    except Order.DoesNotExist:
        return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
    except Order.MultipleObjectsReturned:
        return Response(data=ErrorResponses.SOMETHING_WENT_WRONG, status=status.HTTP_300_MULTIPLE_CHOICES)

    discount = NumberDiscount.objects.filter(number=discount_number).first()
    if discount:
        order.total_price = rest_of_percentage(order.total_price, discount)

    if payment_gateway(order.total_price) == status.HTTP_200_OK:
        order.is_paid = True
        order.save()
        Order.objects.create(user=request.user)
        return Response(data={"detail": "Payment went successful."}, status=status.HTTP_200_OK)
    return Response(data={"detail": "Payment wasn't successful"}, status=status.HTTP_406_NOT_ACCEPTABLE)
