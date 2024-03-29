import django_filters
from .models import RestaurantModel


class RestaurantFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title', lookup_expr='istartswith',
        help_text='Поиск по названию начиная с первой и второй буквы (регистронезависимый)'
    )

    class Meta:
        model = RestaurantModel
        fields = ['title']
