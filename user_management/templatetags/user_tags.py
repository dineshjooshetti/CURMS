from django import template
import json
register = template.Library()

from user_management.models import *


@register.simple_tag
def get_group_data(user_id):
    user_roles=UserGroups.objects.filter(user_id=user_id).values('group__name','role','is_active','group_id')
    return user_roles

@register.filter(name='has_group')
def has_group(user, group_name):
    return UserGroups.objects.filter(group__name=group_name,is_active=1,user_id=user.id).exists()


@register.filter
def slice_string(string,n):
    n=int(n)
    chunks = [string[i:i + n] for i in range(0, len(string), n)]
    res=' '.join(chunks)
    return res

