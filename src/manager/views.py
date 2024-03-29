from django.views.generic import CreateView, DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from src.restaurants.models import RestaurantModel, Dish, Categories
from .forms import UserManagerLoginForm, DishForm
from src.users.models import UserModel, WaiterModel


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


class DishListView(LoginRequiredMixin, ListView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dishes_list.html'
    queryset = Dish.objects.all()


class DishCrudView(LoginRequiredMixin, DetailView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dish_add_page.html'


class DishCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login_page'
    model = Dish
    template_name = 'manager/dish_add_page.html'
    success_url = reverse_lazy('dishes_list')
    # form_class = DishForm
    fields = ['title', 'image', 'price', 'categories', 'description', 'is_active']  # Определите поля непосредственно

    def get_context_data(self, **kwargs):
        kwargs['categories'] = Categories.get_list_values()
        return super().get_context_data(**kwargs)

    # def form_invalid(self, form):
    #     print("111111111111111111111")
    #     return reverse_lazy('dish_add')

    def form_invalid(self, form):
        # Пример перенаправления пользователя на другую страницу в случае ошибки
        return redirect('some_error_page')

    # def form_valid(self, form):
    #     pass


class WaiterListView(LoginRequiredMixin, ListView):
    login_url = 'login_page'
    model = WaiterModel
    template_name = 'manager/waiters_list.html'
    queryset = Dish.objects.all()

