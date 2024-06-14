from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from src.restaurants.models import RestaurantModel, Dish, Categories, Category, Order
from .forms import UserManagerLoginForm, DishForm, WaiterForm, UserRegistrationForm
from src.users.models import UserModel, WaiterModel
from datetime import date
from django.db.models import Sum


class DashboardTemplateView(LoginRequiredMixin, View):
    login_url = 'login_page'
    template_name = 'manager/dashboard.html'

    def get(self, request):
        restaurant = RestaurantModel.objects.get(owner_id=request.user.id)
        return render(request, self.template_name, context={'restaurant': restaurant})


# def create_admin_view(request):
#     if request.method == 'POST':
#         print(request.FILES)
#         form = UserManagerLoginForm(request.POST, request.FILES)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             email = form.cleaned_data['email']
#             title = form.cleaned_data['title']
#             image = form.cleaned_data['image']
#             user = UserModel.objects.create(username=username, email=email, password=password)
#             RestaurantModel.objects.create(title=title, image=image, owner_id=user.id)
#             return render(request, 'manager/dashboard.html', {'user': user})
#         print(form.errors)
#     return


class LoginPageView(View):
    template_name = 'manager/Login_v1/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('restaurant_dashboard')
        else:
            messages.info(request, 'ERROR')
        return render(request, self.template_name)


# class DishListView(LoginRequiredMixin, ListView):
#     login_url = 'login_page'
#     model = Dish
#     template_name = 'manager/dishes_list.html'
#     queryset = Dish.objects.all()


class DishCrudView(LoginRequiredMixin, DetailView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dish_add_page.html'


# class DishCreateView(LoginRequiredMixin, CreateView):
#     login_url = 'login_page'
#     model = Dish
#     template_name = 'manager/dish_add_page.html'
#     success_url = reverse_lazy('dishes_list')
#     # form_class = DishForm
#     fields = ['title', 'image', 'price', 'categories', 'description', 'is_active']  # Определите поля непосредственно
#
#     def get_context_data(self, **kwargs):
#         kwargs['categories'] = Categories.get_list_values()
#         return super().get_context_data(**kwargs)
#
#     # def form_invalid(self, form):
#     #     print("111111111111111111111")
#     #     return reverse_lazy('dish_add')
#
#     def form_invalid(self, form):
#         # Пример перенаправления пользователя на другую страницу в случае ошибки
#         return redirect('some_error_page')
#
#     # def form_valid(self, form):
#     #     pass


class WaiterListView(LoginRequiredMixin, ListView):
    login_url = 'login_page'
    model = WaiterModel
    template_name = 'manager/waiters_list.html'
    # queryset = WaiterModel.objects.select_related('restaurant', 'user').all()

    def get_queryset(self):
        user = self.request.user
        if user.restaurant:
            waiters = WaiterModel.objects.filter(restaurant_id=user.restaurant)
            return waiters
        return WaiterModel.objects.none()
# class WaiterCreateView(LoginRequiredMixin, CreateView):
#     login_url = 'login_page'
#     model = WaiterModel
#     form_class = WaiterForm
#     template_name = 'manager/waiter_add_page.html'
#     success_url = reverse_lazy('waiters_list')


class DishListView(LoginRequiredMixin, ListView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dishes_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.restaurant:
            dishes = Dish.objects.filter(restaurant_id=user.restaurant)
            return dishes
        return Dish.objects.none()

class DishCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dish_add_page.html'
    success_url = reverse_lazy('dishes_list')
    form_class = DishForm

    def form_valid(self, form):
        # Установите restaurant перед сохранением формы
        form.instance.restaurant = RestaurantModel.objects.get(owner=self.request.user)
        return super().form_valid(form)

class DishUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dish_form.html'
    form_class = DishForm
    success_url = reverse_lazy('dishes_list')

    def form_valid(self, form):
        # Установите restaurant перед сохранением формы
        form.instance.restaurant = RestaurantModel.objects.get(owner=self.request.user)
        return super().form_valid(form)


class MainPageView(LoginRequiredMixin, View):
    login_url = 'login_page'
    template_name = 'manager/main_page.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            restaurant = user.owned_restaurant
        except RestaurantModel.DoesNotExist:
            return render(request, self.template_name, {'error': 'No restaurant found for user.'})

        total_daily_sales = self.get_total_daily_sales(restaurant)
        total_monthly_sales = self.get_total_monthly_sales(restaurant)
        total_sales = self.get_total_sales(restaurant)

        context = {
            'restaurant': restaurant,
            'total_daily_sales': total_daily_sales,
            'total_monthly_sales': total_monthly_sales,
            'total_sales': total_sales
        }
        return render(request, self.template_name, context)

    def get_total_daily_sales(self, restaurant):
        total_sales = Order.objects.filter(restaurant=restaurant, created_at__date=date.today()).aggregate(total=Sum('total_amount'))['total']
        return total_sales if total_sales else 0

    def get_total_monthly_sales(self, restaurant):
        total_sales = Order.objects.filter(restaurant=restaurant, created_at__month=date.today().month, created_at__year=date.today().year).aggregate(total=Sum('total_amount'))['total']
        return total_sales if total_sales else 0

    def get_total_sales(self, restaurant):
        total_sales = Order.objects.filter(restaurant=restaurant).aggregate(total=Sum('total_amount'))['total']
        return total_sales if total_sales else 0


class ReviewsView(LoginRequiredMixin, View):
    login_url = 'login_page'
    template_name = 'manager/reviews.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class OrdersView(LoginRequiredMixin, View):
    login_url = 'login_page'
    template_name = 'manager/orders.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


# class CategoriesView(LoginRequiredMixin, View):
#     login_url = 'login_page'
#     template_name = 'manager/categories.html'
#
#     def get(self, request, *args, **kwargs):
#         return render(request, self.template_name)


class CategoriesView(View):
    def get(self, request):
        return render(request, 'manager/categories.html')

class SubcategoriesView(View):
    def get(self, request, category):
        context = {
            'category': category,
            'category_name': category.capitalize(),  # Или заменить на более читабельное название
        }
        return render(request, 'manager/subcategories.html', context)

class EditSubcategoriesView(View):
    def get(self, request, category):
        context = {
            'category': category,
            'category_name': category.capitalize(),  # Или заменить на более читабельное название
        }
        return render(request, 'manager/edit_subcategories.html', context)

    def post(self, request, category):
        # Логика обработки формы для сохранения изменений подкатегорий
        return render(request, 'manager/edit_subcategories.html', {
            'category': category,
            'category_name': category.capitalize(),  # Или заменить на более читабельное название
        })

class ManagerLoginView(View):
    def get(self, request):
        return render(request, 'manager/index.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_page')
        else:
            return render(request, 'manager/index.html', {'error': 'Invalid credentials'})


from django.views.generic.edit import UpdateView, DeleteView


# class DishUpdateView(LoginRequiredMixin, UpdateView):
#     login_url = 'login_page'
#     model = Dish
#     template_name = 'manager/dish_form.html'
#     form_class = DishForm
#     success_url = reverse_lazy('dishes_list')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.all()
#         return context
#
#     def form_valid(self, form):
#         form.instance.restaurant = self.request.user.restaurant
#         return super().form_valid(form)

class DishDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dish_confirm_delete.html'
    success_url = reverse_lazy('dishes_list')

class WaiterCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login_page'
    model = WaiterModel
    form_class = WaiterForm
    template_name = 'manager/waiter_add_page.html'
    success_url = reverse_lazy('waiters_list')

    def form_valid(self, form):
        # Устанавливаем ресторан перед сохранением формы
        form.instance.restaurant = RestaurantModel.objects.get(owner=self.request.user)
        return super().form_valid(form)

class WaiterUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login_page'
    model = WaiterModel
    template_name = 'manager/waiter_form.html'
    form_class = WaiterForm
    success_url = reverse_lazy('waiters_list')

    def form_valid(self, form):
        # Устанавливаем ресторан перед сохранением формы
        form.instance.restaurant = RestaurantModel.objects.get(owner=self.request.user)
        return super().form_valid(form)

class WaiterDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login_page'
    model = WaiterModel
    template_name = 'manager/waiter_confirm_delete.html'
    success_url = reverse_lazy('waiters_list')