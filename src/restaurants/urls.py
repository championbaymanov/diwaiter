from django.urls import path
from .views import *

from . import views


urlpatterns = [
    path('restaurant/', RestaurantListApiView.as_view()),
    path('restaurant/<int:restaurant_id>/', RestaurantDishesAPIView.as_view(), name='restaurant_dishes_api'),
    path('favorite-restaurants/list/', FavoriteRestaurantListView.as_view(), name='favorite-restaurant-list'),
    path('favorite-restaurants/', FavoriteRestaurantCreateView.as_view(), name='favorite-restaurant-create'),
    path('favorite-restaurants/<int:pk>/', FavoriteRestaurantDeleteView.as_view(), name='favorite-restaurant-detail'),
    path('orders/create/', OrderCreate.as_view(), name='order-create'),
    path('orders/update/<int:pk>/', OrderUpdate.as_view(), name='order-update'),
    path('orders/current/', CurrentOrderList.as_view(), name='current-order'),
    path("orders/list/", WaitersOrderList.as_view(), name='order-list'),
    path("my-orders/list/", MyOrdersList.as_view(), name='my-orders-list'),
    path('waiter/restaurant/menu/', RestaurantMenuView.as_view(), name='restaurant-menu'),
    path('waiter/create/order/', WaiterCreateOrder.as_view(), name='waiter-order-create'),
    path('waiter/orders/history/', WaiterHistory.as_view(), name='waiter-order-history'),
    path('order/check/', OrderCheck.as_view(), name='order-check'),
    path('waiter/order/update/<int:pk>/', WaiterOrderUpdateView.as_view(), name='order-update'),
    path('order/closed/<int:pk>', OrderCloseView.as_view(), name='order-closed'),
    path("waiter/restaurant/", WaiterRestaurantListApiView.as_view(), name='menu-list'),
    path('waiter/comments/', CommentCreateView.as_view(), name='comment-create'),
    path('waiter/ratings/', RatingCreateView.as_view(), name='rating-create'),
    path('order/comments/', OrderCommentCreateView.as_view(), name='order-comment-create'),

    path('restaurant/<int:restaurant_id>/categories/', CategoryListByRestaurantView.as_view(),
         name='restaurant-categories'),
    path('waiters/statistics/', WaiterOrderStatisticsView.as_view(), name='waiter-order-statistics'),

    # Order list заказы попадали сюда и официант мог видеть и брать на себя
    # My orders Мои заказы когда официант взял их на себя, тогда они приходят сюда
    # Profile Профиль официанта
    # History orders история заказов за день с 8:00 до 23:00
    # Waiter Create order Когда официант создает заказ по номеру стола и заполняет заказ и
    # он автоматически is_accepted=True
    # Order closed Фронт запрашивает счет
    # Order Cancelled Пока логика будет такая что пока order is_accepted=False будет возможность отменить
    # User завершает заказ фронт отправляет номер стола, id заказа is_check=True Я возвращаю message data error code
    # Официант завершает заказ is_end=True
]
