from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .encryption_util import *
from .models import *
from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names):
   """Requires user membership in at least one of the groups passed in."""

   def in_groups(user):
       if user.is_authenticated:
           if bool(UserGroups.objects.filter(group__name__in=group_names,user_id=user.id,user__is_active=1,is_active=1)) | user.is_superuser:
               return True
           else:
               HttpResponse('https://login.gitam.edu/Login.aspx')
       return False
   return user_passes_test(in_groups)

