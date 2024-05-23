from django.shortcuts import render
import django_filters
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from .filters import RestaurantFilter
from django.utils import timezone
from django.db.models import Sum, Avg, Count, When
from datetime import timedelta
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
# Create your views here.
from rest_framework import generics, filters, status, viewsets, views
from rest_framework.generics import get_object_or_404, ListAPIView, ListCreateAPIView, CreateAPIView, \
    RetrieveUpdateAPIView, DestroyAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import RestaurantSerializer, DishSerializer, OrderSerializer, FavoriteRestaurantSerializer, \
    OrderSerializerUpdate, CurrentSerializer, WaiterOrderListSerializer, WaiterOrderSerializer, OrderHistorySerializer, \
    OrderCheckSerializer, OrderClosedSerializer, FavoriteRestaurantListSerializer, RestaurantDeleteSerializer, \
    CommentSerializer, RatingSerializer, OrderCommentSerializer, CategorySerializer, OrderUpdateSerializer, \
    OrderCloseSerializer, RestaurantDishSerializer
from .models import RestaurantModel, Order, OrderItem, Dish, FavoriteRestaurant, WaiterComment, WaiterRating, \
    OrderComment, Category
from rest_framework import generics
from django_filters import rest_framework as rest_filters
from src.utils import permissions as auth
# import JSONResponce JSON.dump
# import json
# from django.db.models import Prefetch
from src.base.orm import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist


class RestaurantListApiView(generics.ListCreateAPIView):
    queryset = RestaurantModel.objects.all()
    serializer_class = RestaurantSerializer

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = RestaurantFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.user.id is not None:
            queryset = queryset.annotate(is_favorite=Case(
                When(
                    favorites__user_id=request.user, then=Value(True)), default=Value(False), output_field=BooleanField()
            ))
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"error_code": 0,
                         "message": "OK",
                         "data": serializer.data})


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# class CategoryListByRestaurantView(ListAPIView):
#     serializer_class = CategorySerializer
#
#     def get_queryset(self):
#         """
#         Этот метод переопределяется для фильтрации категорий по restaurant_id, полученному из URL.
#         """
#         restaurant_id = self.kwargs['restaurant_id']
#         return Category.objects.filter(restaurant__id=restaurant_id)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     data = serializer.data
    #     return Response({
    #         "error_code": 0,
    #         "message": "OK",
    #         "data": data
    #     }, status=status.HTTP_200_OK)


class FavoriteRestaurantListView(generics.ListAPIView):
    serializer_class = FavoriteRestaurantListSerializer

    def get_queryset(self):
        user = self.request.user
        return FavoriteRestaurant.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Преобразуем данные в желаемый формат
        data = [item['restaurant'] for item in serializer.data]

        return Response({"error_code": 0,
                         "message": "OK",
                         "data": data}, status=status.HTTP_200_OK)


class FavoriteRestaurantCreateView(generics.CreateAPIView):
    queryset = FavoriteRestaurant.objects.all()
    serializer_class = FavoriteRestaurantSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"error_code": 0,
                         "message": "OK",
                         "data": response.data})



class FavoriteRestaurantDeleteView(generics.DestroyAPIView):

    def get_queryset(self):
        user = self.request.user
        return FavoriteRestaurant.objects.filter(user=user)

    def perform_destroy(self, instance):
        instance.delete()

    def delete(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('pk')
        queryset = self.get_queryset()
        favorite_restaurant = queryset.filter(restaurant_id=restaurant_id).first()

        if favorite_restaurant:
            self.perform_destroy(favorite_restaurant)
            return Response({"error_code": 0,
                            'message': 'Ресторан успешно удален из избранного.',
                            "data": None})
        else:
            return Response({"error_code": 1,
                            'message': 'Ресторан не найден в избранном пользователя.',
                            "data": None}, status=status.HTTP_404_NOT_FOUND)


class OrderCreate(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def get_serializer_context(self):
        context = super(OrderCreate, self).get_serializer_context()
        context['user_id'] = self.request.user.id
        return context


class CurrentOrderList(generics.ListAPIView):
    queryset = Order.objects.prefetch_related(
        # Prefetch("order_items__dish", queryset=)
        "order_items__dish"
    )

    serializer_class = CurrentSerializer

    def get_object(self):
        return self.queryset.get(user_id=self.request.user.id, is_end=False)

    def list(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
        except ObjectDoesNotExist:
            return Response({
                "data": None,
                "error_code": 1,
                "message": "У вас сейчас нет активных заказов",
            })

        serializer = self.get_serializer(obj)

        return Response({
            "data": serializer.data,
            "error_code": 0,
            "message": "OK",
        })


class RestaurantDishesAPIView(ListAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer


class RestaurantDishesAPIView(ListAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        restaurant = get_object_or_404(RestaurantModel, id=kwargs['restaurant_id'])
        self.serializer_class = RestaurantSerializer
        restaurant_serializer = self.get_serializer(restaurant)
        return Response({
            "data": {'restaurant': restaurant_serializer.data, "dishes": serializer.data, },
            "error_code": 0,
            "message": "OK",
        })

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(restaurant_id=kwargs['restaurant_id'])
        return self.list(request, *args, **kwargs)
        # return Response(data=self.list(request, *args, **kwargs))


class OrderUpdate(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializerUpdate

    # def update(self, request, *args, **kwargs):
    #     return super(OrderUpdate, self).update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user, is_accepted=False)

    def get_serializer_context(self):
        context = super(OrderUpdate, self).get_serializer_context()
        context['user'] = self.request.user
        return context
    # def perform_update(self, serializer):
    #     # instance = serializer.save
    #     # send_email_confirmation(user=self.request.user, modified=instance)


class WaitersOrderList(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = WaiterOrderListSerializer

    def get_queryset(self):
        restaurant_id = self.request.user.waiter.restaurant_id
        return self.queryset.filter(restaurant_id=restaurant_id, is_end=False, is_accepted=False)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data,
                         "error_code": 0,
                         "message": "OK",
                         })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant_id = self.request.user.waiter.restaurant_id
        instance = get_object_or_404(Order,
                                     restaurant_id=restaurant_id,
                                     is_end=False,
                                     is_accepted=False,
                                     id=serializer.data['id'])
        instance.is_accepted = True
        instance.waiter_id = request.user.waiter.id
        instance.save()
        serializer = self.get_serializer(instance)

        return Response({"data": serializer.data,
                         "error_code": 0,
                         "message": "OK",
                         })


class MyOrdersList(ListAPIView):
    queryset = Order.objects.filter(is_accepted=True, is_end=False)
    serializer_class = CurrentSerializer

    def get_queryset(self):
        restaurant_id = self.request.user.waiter.restaurant_id
        waiter_id = self.request.user.waiter.id
        return self.queryset.filter(restaurant_id=restaurant_id, waiter_id=waiter_id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data,
                         "error_code": 0,
                         "message": "OK",
                         })


# class RestaurantMenuView(ListAPIView):
#     serializer_class = RestaurantDishSerializer
#     permission_classes = [auth.IsAuthenticated]
#
#     def get_queryset(self):
#         user = self.request.user
#         if hasattr(user, 'waiter') and user.waiter.restaurant:
#             return Dish.objects.filter(restaurant=user.waiter.restaurant, is_active=True)
#         else:
#             return Dish.objects.none()
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         if serializer.data:
#             return Response({
#                 "error_code": 0,
#                 "message": "OK",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 "error_code": 1,
#                 "message": "No active dishes found for this restaurant.",
#                 "data": []
#             }, status=status.HTTP_404_NOT_FOUND)

class RestaurantMenuView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        # Получаем доступ к ресторану официанта
        user = self.request.user
        if hasattr(user, 'waiter') and user.waiter.restaurant:
            # Возвращаем категории для ресторана официанта с предзагруженными блюдами
            return Category.objects.filter(restaurant=user.waiter.restaurant).prefetch_related('dishes')
        else:
            # Возвращаем пустой список, если у пользователя нет ресторана
            return Category.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        if serializer.data:
            return Response({
                "error_code": 0,
                "message": "OK",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error_code": 1,
                "message": "No categories found for this restaurant.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)


class WaiterCreateOrder(ListCreateAPIView):
    serializer_class = WaiterOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(restaurant=self.request.user.waiter.restaurant)

    def create(self, request, *args, **kwargs):
        # Добавляем 'waiter_id' в контекст сериализатора
        context = self.get_serializer_context()
        context['waiter_id'] = request.user.waiter.id

        serializer = self.get_serializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({
                "error_code": 0,
                "message": "Order created successfully",
                "data": serializer.data
            }, status=HTTP_201_CREATED, headers=headers)
        else:
            return Response({
                "error_code": 1,
                "message": "Failed to create the order",
                "data": {}
            }, status=HTTP_400_BAD_REQUEST)


# class WaiterOrderUpdateView(UpdateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderUpdateSerializer
#     permission_classes = [auth.IsAuthenticated]
#
#     def get_queryset(self):
#         # Официанты видят только заказы в своем ресторане
#         return Order.objects.filter(restaurant__waiter__user=self.request.user)
#
#     def get_object(self):
#         # Проверяем, что заказ еще не закрыт и принадлежит текущему официанту
#         obj = super().get_object()
#         if obj.is_end:
#             raise serializers.ValidationError("This order is already closed.")
#         return obj
#
#     def update(self, request, *args, **kwargs):
#         response = super().update(request, *args, **kwargs)
#         if response.status_code == 200:
#             return Response({
#                 "error_code": 0,
#                 "message": "Order updated successfully",
#                 "data": response.data
#             }, status=response.status_code)
#         else:
#             return Response({
#                 "error_code": 1,
#                 "message": "Failed to update the order",
#                 "data": None
#             }, status=response.status_code)

    # def partial_update(self, request, *args, **kwargs):
    #     # Разрешаем частичное обновление заказа
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)


class WaiterOrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer

    def get_object(self):
        # Проверяем, что заказ принадлежит текущему пользователю и не завершен
        obj = super().get_object()
        if obj.user != self.request.user or obj.is_end:
            raise PermissionDenied("You cannot edit this order.")
        return obj


class OrderCloseView(APIView):
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderCloseSerializer(order, data={'is_end': True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"error_code": 0, "message": "Order closed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
        Фильтр для заказов текущего официанта.
        """
        return Order.objects.filter(restaurant__waiter__user=self.request.user)


class WaiterHistory(ListAPIView):
    queryset = Order.objects.filter(is_end=True)
    serializer_class = OrderHistorySerializer

    def get_queryset(self):
        waiter_id = self.request.user.waiter.id
        return self.queryset.filter(waiter_id=waiter_id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data,
                         "error_code": 0,
                         "message": "OK",
                         })


class OrderCheck(CreateAPIView):
    queryset = Order.objects.filter(is_end=False, is_accepted=True)
    serializer_class = OrderCheckSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.queryset.get(id=serializer.data['order_id'])
        instance.is_check = True
        instance.save()
        return Response({"data": serializer.data,
                         "error_code": 0,
                         "message": "OK",
                         })


class OrderClosed(RetrieveUpdateAPIView):
    queryset = Order.objects.filter(is_end=False, is_check=True, is_accepted=True)
    serializer_class = OrderClosedSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance.is_end = True
        instance.save()

        return Response({"data": serializer.data,
                         "error_code": 0,
                         "message": "OK",
                         })


class WaiterRestaurantListApiView(generics.ListCreateAPIView):
    # permission_classes = [IsDispatcher]
    queryset = Dish.objects.all()
    serializer_class = DishSerializer

    # filter_backends = (rest_filters.DjangoFilterBackend, filters.SearchFilter)
    # search_fields = ["title"]

    def get_queryset(self):
        return self.queryset.filter(restaurant_id=self.request.user.waiter.restaurant_id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"error_code": 0,
                         "message": "OK",
                         "data": serializer.data})


class CommentCreateView(generics.CreateAPIView):
    queryset = WaiterComment.objects.all()
    serializer_class = CommentSerializer


class RatingCreateView(generics.CreateAPIView):
    queryset = WaiterRating.objects.all()
    serializer_class = RatingSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        waiter = instance.waiter
        waiter.update_average_rating()
        waiter.save()


class OrderCommentCreateView(generics.CreateAPIView):
    queryset = OrderComment.objects.all()
    serializer_class = OrderCommentSerializer


class WaiterOrderStatisticsView(APIView):

    def get(self, request):
        today = timezone.now()
        start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)

        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Убедимся, что у пользователя есть роль официанта и он привязан к ресторану
        if hasattr(request.user, 'waiter') and request.user.waiter.restaurant_id:
            restaurant_id = request.user.waiter.restaurant_id
        else:
            return Response({"error_code": 1, "message": "User is not a waiter or not assigned to any restaurant."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Фильтруем заказы по ресторану и официанту
        orders = Order.objects.filter(restaurant_id=restaurant_id, waiter_id=request.user.waiter.id, is_end=True)

        daily_orders = orders.filter(created_at__range=[start_of_today, end_of_today])
        monthly_orders = orders.filter(created_at__range=[start_of_month, end_of_today])
        all_time_orders = orders

        daily_stats = {
            "total_orders": daily_orders.count(),
            "total_amount": daily_orders.aggregate(total=Sum('total_amount'))['total'],
            "average_amount": daily_orders.aggregate(average=Avg('total_amount'))['average']
        }

        monthly_stats = {
            "total_orders": monthly_orders.count(),
            "total_amount": monthly_orders.aggregate(total=Sum('total_amount'))['total'],
            "average_amount": monthly_orders.aggregate(average=Avg('total_amount'))['average']
        }

        all_time_stats = {
            "total_orders": all_time_orders.count(),
            "total_amount": all_time_orders.aggregate(total=Sum('total_amount'))['total'],
            "average_amount": all_time_orders.aggregate(average=Avg('total_amount'))['average']
        }

        response_data = {
            "daily_stats": daily_stats,
            "monthly_stats": monthly_stats,
            "all_time_stats": all_time_stats
        }

        return Response({
            "error_code": 0,
            "message": "OK",
            "data": response_data
        }, status=status.HTTP_200_OK)

