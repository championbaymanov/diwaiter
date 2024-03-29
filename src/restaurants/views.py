from django.shortcuts import render
import django_filters
from .filters import RestaurantFilter

# Create your views here.
from rest_framework import generics, filters, status, viewsets, views
from rest_framework.generics import get_object_or_404, ListAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import RestaurantSerializer, DishSerializer, OrderSerializer, FavoriteRestaurantSerializer, \
    OrderSerializerUpdate, CurrentSerializer, WaiterOrderListSerializer, WaiterOrderSerializer, OrderHistorySerializer, \
    OrderCheckSerializer, OrderClosedSerializer, FavoriteRestaurantListSerializer, RestaurantDeleteSerializer, CommentSerializer, RatingSerializer, OrderCommentSerializer
from .models import RestaurantModel, Order, OrderItem, Dish, FavoriteRestaurant, WaiterComment, WaiterRating, OrderComment
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
    permission_classes = (auth.IsAnyAuthenticated,)

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



class FavoriteRestaurantListView(generics.ListAPIView):
    serializer_class = FavoriteRestaurantListSerializer
    permission_classes = [auth.IsAuthenticated]

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
    permission_classes = [auth.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"error_code": 0,
                         "message": "OK",
                         "data": response.data})



class FavoriteRestaurantDeleteView(generics.DestroyAPIView):
    permission_classes = [auth.IsAuthenticated]

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
    permission_classes = [auth.IsAuthenticated]
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
    permission_classes = [auth.IsAuthenticated]

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
    permission_classes = [auth.IsAuthenticated]

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
    permission_classes = [auth.IsAuthenticated]

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


class WaiterCreateOrder(ListCreateAPIView):
    permission_classes = [auth.IsAuthenticated]
    serializer_class = WaiterOrderSerializer

    def get_serializer_context(self):
        context = super(WaiterCreateOrder, self).get_serializer_context()
        print(self.request.user)
        context['waiter_id'] = self.request.user.waiter.id
        return context


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
    permission_classes = [auth.IsAuthenticated]


class RatingCreateView(generics.CreateAPIView):
    queryset = WaiterRating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [auth.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        waiter = instance.waiter
        waiter.update_average_rating()
        waiter.save()


class OrderCommentCreateView(generics.CreateAPIView):
    queryset = OrderComment.objects.all()
    serializer_class = OrderCommentSerializer
    permission_classes = [auth.IsAuthenticated]


