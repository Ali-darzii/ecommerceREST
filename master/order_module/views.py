from rest_framework.views import APIView
from rest_framework.response import Response
from order_module.models import OrderDetail
from rest_framework.permissions import IsAuthenticated

from order_module.serializers import OrderDetailSerializer
from utils.Responses import ErrorResponses
from rest_framework import status


class MakeOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """ Add or Lower the product has been in basket """

    def post(self, request):
        """ increase or decrease Product to basket with order_detail pk """
        order_detail_id = request.GET.get("order_detail")
        deside = request.GET.get("deside")

        try:
            order_detail = OrderDetail.objects.get(pk=order_detail_id)
        except OrderDetail.DoesNotExist:
            return Response(data=ErrorResponses.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
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
        order_details = OrderDetail.objects.filter(order_id=order_detail_id)
        serializer = OrderDetailSerializer(order_details)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """ increase or decrease or create Product to basket with product """

