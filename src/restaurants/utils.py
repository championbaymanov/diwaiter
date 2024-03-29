from django.db import models

from rest_framework.exceptions import ValidationError


def update(user, obj, payload, update_fields):
    return _update(user, obj, payload, update_fields)


def _update(user, obj, payload, update_fields):
    for attr, new_value in payload.items():
        obj_attrs: list = get_list_model_attrs_name(obj)
        if hasattr(obj, attr) and not isinstance(new_value, dict) and (attr not in update_fields):
            raise ValidationError(code=400, detail="permission denied")
        if hasattr(obj, attr) and (not isinstance(new_value, (dict, list)) or (attr in obj_attrs)):
            print(obj, attr, new_value)
            setattr(obj, attr, new_value)
        elif hasattr(obj, attr) and isinstance(new_value, (dict, list)) and (attr not in obj_attrs):
            _update(user, getattr(obj, attr), new_value, update_fields)
    _update_fields = get_list_dict_keys(payload, obj)
    obj.save(update_fields=_update_fields, is_updated=True)
    return obj


def get_list_model_attrs_name(cls) -> list:
    if isinstance(cls, models.Model):
        return [field.name for field in cls._meta.fields]
    return []


def get_list_dict_keys(payload: dict, obj) -> list:
    return [attr for attr in list(payload.keys()) if not isinstance(getattr(obj, attr), models.Model)]
