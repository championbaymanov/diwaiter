from django.urls import path
from .views import DashboardTemplateView, LoginPageView, DishListView, DishCrudView, DishCreateView, WaiterListView

from . import views


urlpatterns = [
    path('restaurant/dashboard', DashboardTemplateView.as_view(), name='restaurant_dashboard'),
    # path('create/restaurant', create_admin_view, name='create-admin'),
    path('restaurant/login', LoginPageView.as_view(), name='login_page'),
    path('restaurant/dishes', DishListView.as_view(), name='dishes_list'),
    path('restaurant/dishes/add', DishCreateView.as_view(), name='dish_add'),
    path('restaurant/dishes/<int:dish_id>/edit', DishCrudView.as_view(), name='dish_edit'),
    path('restaurant/waiters', WaiterListView.as_view(), name='waiters_list'),
    # path('restaurant/waiters/add', DishCreateView.as_view(), name='waiters_add'),
    # path('restaurant/waiters/<int:dish_id>/edit', DishCrudView.as_view(), name='waiters_edit'),
]
