import random, math
from django import template
from django.utils import timezone

register = template.Library()

def callmethod(obj, methodname):
    method = getattr(obj, methodname)
    if "__callArg" in obj.__dict__:
        # if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()


def args(obj, arg):
    if not "__callArg" in obj.__dict__:
        # if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []
    obj.__callArg.append(arg)
    return obj
    
def add_class(field):
    # Check if it is a checkbox
    if field.field.widget.input_type == "checkbox":
        if "class" in field.field.widget.attrs:
            field.field.widget.attrs["class"] += " form-check-input"
        else:
            field.field.widget.attrs["class"] = "form-check-input"
    # Check if it is a select
    elif field.field.widget.input_type == "select":
        if "class" in field.field.widget.attrs:
            field.field.widget.attrs["class"] += " form-select"
        else:
            field.field.widget.attrs["class"] = "form-select"
    else:
        if "class" in field.field.widget.attrs:
            field.field.widget.attrs["class"] += " form-control"
        else:
            field.field.widget.attrs["class"] = "form-control"
    return field


def get_photo_user(user):
        if user.socialaccount_set.exists():
            social_account = user.socialaccount_set.first()
            return social_account.get_avatar_url()
        else:
            return None
        
def get_first_name(user):
    if user.first_name == "":
        return user.username
    return user.first_name

def number_to_price(number):
    return str(number).replace(",", ".")

register.filter("call", callmethod)
register.filter("args", args)
register.filter("add_class", add_class)
register.filter("get_photo_user", get_photo_user)
register.filter("get_first_name", get_first_name)
register.filter("number_to_price", number_to_price)