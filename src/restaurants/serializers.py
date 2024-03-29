from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .models import Dish, RestaurantModel, FavoriteRestaurant, Order, OrderItem, Categories, PAYMENT_METHOD_CHOICES,\
    WaiterRating, WaiterComment, OrderComment
from .utils import update


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'


class OrderItemsSerializer(serializers.Serializer):
    title = serializers.CharField(source="dish.title")
    image = serializers.ImageField(source="dish.image")
    price = serializers.CharField(source="dish.price")
    categories = serializers.CharField(source="dish.categories")
    description = serializers.CharField(source="dish.description")
    restaurant = serializers.IntegerField(source="dish.restaurant_id")
    is_active = serializers.BooleanField(source="dish.is_active")
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class CurrentSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()
    # user_id = serializers.IntegerField()
    table_number = serializers.IntegerField()
    restaurant_id = serializers.IntegerField()
    payment_method = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_accepted = serializers.BooleanField()
    id = serializers.IntegerField()

    order_items = OrderItemsSerializer(many=True)

    def to_representation(self, instance):
        data = super(CurrentSerializer, self).to_representation(instance)
        if hasattr(instance, 'user'):
            waiter = instance.waiter
            if waiter and hasattr(waiter, 'user'):
                data['waiter_username'] = waiter.user.username
            else:
                data['waiter_username'] = None
        return data

    # title = serializers.CharField(max_length=16)
    # image = serializers.ImageField()
    # price = serializers.CharField(max_length=16)
    # categories = serializers.ChoiceField(Categories.get_choice(), default='Main_meal')
    # description = serializers.CharField(max_length=255, required=False)
    # # restaurant = serializers.ForeignKey(RestaurantModel, on_delete=models.CASCADE, related_name='dishes')
    # is_active = serializers.BooleanField(default=True)


class RestaurantSerializer(serializers.ModelSerializer):
    is_favorite = serializers.BooleanField(default=False)

    class Meta:
        model = RestaurantModel
        fields = ['id', 'title', 'image', 'is_favorite']


class FavoriteRestaurantListSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()

    class Meta:
        model = FavoriteRestaurant
        fields = ['restaurant']


class FavoriteRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRestaurant
        fields = ['restaurant']

    def create(self, validated_data):
        user = self.context['request'].user
        restaurant = validated_data['restaurant']

        # Проверяем, существует ли уже запись о ресторане в избранном для данного пользователя
        if FavoriteRestaurant.objects.filter(user=user, restaurant=restaurant).exists():
            raise serializers.ValidationError({"error_code": 0,
                         "message": "Этот ресторан уже добавлен в избранное",
                         "data": "Null"})

        favorite = FavoriteRestaurant(user=user, restaurant=restaurant)
        favorite.save()
        return favorite


class RestaurantDeleteSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    

class OrderItemSerializer(serializers.Serializer):
    dish = serializers.IntegerField(required=True, source="dish_id")
    quantity = serializers.IntegerField(required=True)


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    table_number = serializers.IntegerField(required=True)
    restaurant = serializers.IntegerField(required=True, source="restaurant_id")
    total_amount = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(required=True)
    is_accepted = serializers.BooleanField(read_only=True)
    order_items = OrderItemSerializer(many=True)
    is_end = serializers.BooleanField(default=False)

    # waiter = WaiterSerializer(read_only=True)

    def create(self, validated_data: dict):
        if not (items := validated_data.pop("order_items")):
            raise ValidationError("The field 'items' cannot be empty")
        order = Order.objects.create(user_id=self.context["user_id"], **validated_data)
        for item_data in items:
            OrderItem.objects.create(order=order, **item_data)
        order.calculate_total_amount()
        return order

    def to_representation(self, instance):
        data = super(OrderSerializer, self).to_representation(instance)
        return {"error_code": 0, "message": "OK", "data": data}


class OrderSerializerUpdate(serializers.Serializer):
    order_items = OrderItemSerializer(many=True, write_only=True, required=False)
    payment_method = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        if (pm := validated_data.get('payment_method')) is not None and pm in ['card', 'cash']:
            instance.payment_method = pm
        if (oi := validated_data.get('order_items')) is not None:
            for order in oi:
                try:
                    order_db = OrderItem.objects.get(
                        dish_id=order['dish_id'],
                        order_id=instance.id
                    )
                    order_db.quantity = order['quantity']
                    order_db.save()
                except OrderItem.DoesNotExist:
                    OrderItem.objects.create(dish_id=order['dish_id'], order_id=instance.id, quantity=order['quantity'])

        return instance
        # return update(self.context["request"].user, instance, validated_data, ['order_items', 'payment_method'])


class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_waiter:  # Проверка, является ли пользователь официантом
            return Order.objects.filter(waiter=user.userprofile)
        else:
            return Order.objects.none()  # Пользователь не является официантом, пустой QuerySet


class RestaurantDishesAPIView(ListAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(restaurant_id=kwargs['restaurant_id'])
        return self.list(request, *args, **kwargs)


class WaiterOrderListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    table_number = serializers.IntegerField(read_only=True)
    restaurant = serializers.IntegerField(read_only=True, source="restaurant_id")
    total_amount = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(read_only=True)
    is_accepted = serializers.BooleanField(read_only=True)
    waiter_id = serializers.IntegerField(read_only=True)
    order_items = OrderItemsSerializer(many=True, read_only=True)


class WaiterOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    table_number = serializers.IntegerField(required=True)
    restaurant = serializers.IntegerField(required=True, source="restaurant_id")
    total_amount = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(read_only=True)
    is_accepted = serializers.BooleanField(read_only=True)
    order_items = OrderItemSerializer(many=True)
    is_end = serializers.BooleanField(default=False)

    def create(self, validated_data: dict):
        if not (items := validated_data.pop("order_items")):
            raise ValidationError("The field 'items' cannot be empty")
        order = Order.objects.create(is_accepted=True, waiter_id=self.context['waiter_id'], **validated_data)
        for item_data in items:
            OrderItem.objects.create(order=order, **item_data)
        order.calculate_total_amount()
        return order


class OrderHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    table_number = serializers.IntegerField(read_only=True)
    restaurant = serializers.IntegerField(read_only=True, source="restaurant_id")
    total_amount = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(read_only=True)
    is_accepted = serializers.BooleanField(read_only=True)
    order_items = OrderItemsSerializer(many=True, read_only=True)
    waiter_id = serializers.IntegerField(read_only=True)


class OrderCheckSerializer(serializers.Serializer):
    table_number = serializers.IntegerField()
    is_check = serializers.BooleanField(default=False)
    order_id = serializers.IntegerField()


class OrderClosedSerializer(serializers.Serializer):
    is_end = serializers.BooleanField()
    order_id = serializers.IntegerField(read_only=True)
    order_items = OrderItemsSerializer(many=True, read_only=True)
    total_amount = serializers.IntegerField(read_only=True)
    payment_method = serializers.CharField(read_only=True)
    restaurant = serializers.IntegerField(read_only=True, source="restaurant_id")
    table_number = serializers.IntegerField(read_only=True)
    


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaiterComment
        fields = '__all__'

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        order = get_object_or_404(Order, user_id=user_id, is_end=False, only=('restaurant_id', 'waiter_id', 'id'),
                                  raise_error_text='Нету текущего заказа')
        data = {'user_id': user_id, 'restaurant_id': order.restaurant_id, 'waiter_id': order.waiter_id, 'order_id': order.id}
        validated_data.update(data)
        return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaiterRating
        fields = '__all__'

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        order = get_object_or_404(Order, user_id=user_id, is_end=False, only=('waiter_id', 'id'),
                                  raise_error_text='Нету текущего заказа')
        data = {'user_id': user_id, 'waiter_id': order.waiter_id}
        validated_data.update(data)
        return super().create(validated_data)


class OrderCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderComment
        fields = '__all__'

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        order = get_object_or_404(Order, user_id=user_id, is_end=False, only=('restaurant_id', 'id'),
                                  raise_error_text='Нету текущего заказа')
        data = {'user_id': user_id, 'restaurant_id': order.restaurant_id, 'order_id': order.id}
        validated_data.update(data)
        return super().create(validated_data)

