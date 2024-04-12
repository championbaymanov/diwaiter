from django import forms
from django.contrib import admin
from django.db.models import Count

from .models import UserModel, JwtModel, WaiterModel
from django.core.exceptions import ValidationError


class WaiterForm(forms.ModelForm):
    username = forms.CharField(max_length=255)
    email = forms.EmailField(required=False)
    password = forms.CharField(max_length=255, required=False)

    class Meta:
        model = WaiterModel
        fields = ('username', 'restaurant', 'email', 'password')

    def save(self, commit=True):
        user = UserModel(username=self.cleaned_data['username'], email=self.cleaned_data['email'])
        user.set_password(self.cleaned_data['password'])
        user.save()
        self.instance.user = user

        return super(WaiterForm, self).save(commit=commit)


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username',)  # 'username',
    list_display_links = ('email', )
    list_filter = ('is_active', )
    search_fields = ('username', 'email', 'status')
    exclude = ('is_active', )


admin.site.register((JwtModel,))


@admin.register(WaiterModel)
class WaiterAdmin(admin.ModelAdmin):
    def get_closed_orders(self):
        closed_orders = WaiterModel.objects.filter(restaurant__is_end=True).annotate(
            closed_orders=Count('restaurant__id'))

        return closed_orders

    list_display = ['id', 'user', 'restaurant', 'average_rating']
    list_display_links = ("user", 'id')
    fieldsets = (
        ("Create Fields", {"fields": ("username", "restaurant", "email", "password")}),
    )
    form = WaiterForm

    def get_fieldsets(self, request, obj=None) -> tuple:
        if obj is None:
            return super(WaiterAdmin, self).get_fieldsets(request=request, obj=obj)
        return (
            ("Fields", {"fields": ('user', 'restaurant', 'average_rating')}),
        )

    def get_object(self, request, object_id, from_field=None):
        try:
            waiter = (
                WaiterModel.objects.all()
                .select_related("user")
                .only("id", "user__username", "user__email")
                .get(id=object_id)
            )
            waiter.username = waiter.user.username
            waiter.email = waiter.user.email
            return waiter
        except (WaiterModel.DoesNotExist, ValidationError, ValueError):
            return None

    def save_model(self, request, obj, form, change):
        if obj.id is None:
            return super(WaiterAdmin, self).save_model(request, obj, form, change)
        else:
            changed_fields = form.changed_data
            data = form.cleaned_data
            for key, value in data.items():
                if hasattr(obj, key) and key in changed_fields:
                    setattr(obj, key, value)



# admin.site.register(WaiterAdmin, WaiterModel)
