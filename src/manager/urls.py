from django.urls import path
from .views import DashboardTemplateView, LoginPageView, DishListView, DishCrudView, DishCreateView, WaiterListView, \
    WaiterCreateView, ManagerLoginView, DishUpdateView, DishDeleteView, WaiterUpdateView, WaiterDeleteView

from . import views


urlpatterns = [
    path('restaurant/dashboard', DashboardTemplateView.as_view(), name='restaurant_dashboard'),
    # path('create/restaurant', create_admin_view, name='create-admin'),
    path('', ManagerLoginView.as_view(), name='login_page'),
    path('restaurant/dishes/', DishListView.as_view(), name='dishes_list'),
    path('restaurant/dishes/add/', DishCreateView.as_view(), name='dish_add'),
    path('restaurant/dishes/<int:pk>/edit', DishUpdateView.as_view(), name='dish_edit'),
    path('restaurant/dishes/<int:pk>/delete/', DishDeleteView.as_view(), name='dish_delete'),
    path('restaurant/dishes/<int:pk>/', DishCrudView.as_view(), name='dish_detail'),  # Для отображения детали блюда

    # path('restaurant/dishes/<int:dish_id>/edit', DishCrudView.as_view(), name='dish_edit'),
    path('restaurant/waiters/', WaiterListView.as_view(), name='waiters_list'),
    path('restaurant/waiters/add/', WaiterCreateView.as_view(), name='waiter_add'),
    path('restaurant/waiters/<int:pk>/edit/', WaiterUpdateView.as_view(), name='waiter_edit'),
    path('restaurant/waiters/<int:pk>/delete/', WaiterDeleteView.as_view(), name='waiter_delete'),

    # path('restaurant/main', views.main_page, name='main_page'),
    path('restaurant/main/', views.MainPageView.as_view(), name='main_page'),
    path('restaurant/reviews/', views.ReviewsView.as_view(), name='reviews'),
    path('restaurant/orders/', views.OrdersView.as_view(), name='orders'),
    path('restaurant/categories/', views.CategoriesView.as_view(), name='categories'),
    path('restaurant/categories/<str:category>/', views.SubcategoriesView.as_view(), name='subcategories'),
    path('restaurant/categories/<str:category>/edit/', views.EditSubcategoriesView.as_view(), name='edit_subcategories'),


    # path('restaurant/waiters/add', DishCreateView.as_view(), name='waiters_add'),
    # path('restaurant/waiters/<int:dish_id>/edit', DishCrudView.as_view(), name='waiters_edit'),
]
