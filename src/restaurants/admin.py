from django.contrib import admin
from datetime import date
from django.db.models import Sum
# Register your models here.
from .models import Dish, Order, RestaurantModel, OrderItem, OrderComment, WaiterRating, WaiterComment, Category


class DishAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant__owner=request.user)


admin.site.register(Dish, DishAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant')  # Отображение имени категории и связанного ресторана
    list_filter = ('restaurant',)  # Фильтрация по ресторану


admin.site.register(Order, OrderAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')  # Отображение имени категории и связанного ресторана
    list_filter = ('restaurant',)  # Фильтрация по ресторану
    search_fields = ('name',)  # Поиск по имени категории


admin.site.register(Category, CategoryAdmin)


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'owner', 'service_charge_percentage', 'get_total_daily_sales', 'get_total_monthly_sales',
                    'get_total_sales']
#
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.owner:
            obj.owner.restaurant = obj
            obj.owner.save()


admin.site.register(RestaurantModel, RestaurantAdmin)

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