from django.contrib import admin
from datetime import date
from django.db.models import Sum
# Register your models here.
from .models import Dish, Order, RestaurantModel, OrderItem, OrderComment, WaiterRating, WaiterComment


class DishAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant__owner=request.user)


admin.site.register(Dish, DishAdmin)


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_total_daily_sales', 'get_total_monthly_sales', 'get_total_sales']

    def get_total_daily_sales(self, obj):
        # Подсчитываем общую сумму заказов для ресторана за текущий день
        total_sales = Order.objects.filter(restaurant=obj, created_at__date=date.today()).aggregate(total=Sum('total_amount'))['total']
        return total_sales if total_sales else 0

    def get_total_monthly_sales(self, obj):
        # Подсчитываем общую сумму заказов для ресторана за текущий месяц
        total_sales = Order.objects.filter(restaurant=obj, created_at__month=date.today().month, created_at__year=date.today().year).aggregate(total=Sum('total_amount'))['total']
        return total_sales if total_sales else 0

    def get_total_sales(self, obj):
        # Подсчитываем общую сумму заказов для ресторана за все время
        total_sales = Order.objects.filter(restaurant=obj).aggregate(total=Sum('total_amount'))['total']
        return total_sales if total_sales else 0


admin.site.register(RestaurantModel, RestaurantAdmin)

admin.site.register(Order)
admin.site.register(OrderItem)



class OrderCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')


admin.site.register(OrderComment, OrderCommentAdmin)


class WaiterRatingAdmin(admin.ModelAdmin):
    list_display = ('waiter_id', 'user_id', 'rating')


admin.site.register(WaiterRating, WaiterRatingAdmin)


class WaiterCommentAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'waiter_id', 'text')


admin.site.register(WaiterComment, WaiterCommentAdmin)