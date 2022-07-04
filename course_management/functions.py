from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from user_management.models import *
from programs.models import *
from course_management.models import *
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.models import  Group
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime, timedelta
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q,Count,Sum
import ast
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from user_management.encryption_util import *
from course_management.course_operations import co_po_pso_average
from django.contrib.auth.decorators import user_passes_test
import xlrd
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from user_management.utils import *

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipaddress = x_forwarded_for.split(',')[-1].strip()
    else:
        ipaddress = request.META.get('REMOTE_ADDR')
    return ipaddress

def not_found(request):
    return HttpResponse('Page not found')

def group_required(*group_names):
   """Requires user membership in at least one of the groups passed in."""

   def in_groups(user):
       if user.is_authenticated:
           if bool(user.groups.filter(name__in=group_names)) | user.is_superuser:
               return True
           else:
               HttpResponse('https://login.gitam.edu/Login.aspx')
       return False
   return user_passes_test(in_groups)


def get_course_data(course_id_list):
    courses = Course.objects.filter(id__in=course_id_list).values('L', 'T', 'P', 'J', 'S', 'C', 'course_name','level_of_course__level','pass_fail',
                                                                       'course_type_id', 'id', 'course_type__name','course_code',
                                                                       'program_type__type').order_by('-level_of_course__level')
    courses_users = CourseUserMapping.objects.filter(course_id__in=course_id_list).values('to_user_id__username',
                                                                                               'course_id',
                                                                                               'course__course_name',
                                                                                               'to_user_id',
                                                                                               'to_user_group_id',
                                                                                               'to_user_id__first_name',
                                                                                               'to_user__email')
    campus_detail = CourseCampusMapping.objects.values('campus__name', 'course_id')
    depart_detail = CourseDepartmentMapping.objects.values('department', 'course_id')
    inst_detail = CourseInstituteMapping.objects.values('institute', 'course_id')
    l = []
    for i in courses:
        i['encrypt_id'] = encrypt(i['id'])
        i['campus_detail'] = [c['campus__name'] for c in campus_detail if c['course_id'] == i['id']]
        i['depart_detail'] = [c['department'] for c in depart_detail if c['course_id'] == i['id']]
        i['inst_detail'] = [c['institute'] for c in inst_detail if c['course_id'] == i['id']]
        course_status = CourseUserMapping.objects.filter(course_id=i['id']).values('course_id','course_status_level_id', 'course_status_level__title').last()
        i['course_status']='-'
        if course_status:
            i['course_status'] = course_status['course_status_level__title']

        for j in courses_users:
            if i['id'] == j['course_id']:
                if j['to_user_group_id'] == 2:
                    i['csmm_name'] = j['to_user_id__first_name']

                if j['to_user_group_id'] == 3:
                    i['csmi_name'] = j['to_user_id__first_name']

        l.append(i)
    return l


def get_program_course_data(course_id,p_id,c_id):
    courses = Course.objects.filter(id=course_id).values('L', 'T', 'P', 'J', 'S', 'C', 'course_name','pass_fail',
                      'course_type_id', 'id', 'course_type__name','level_of_course__level',
                        'program_type__type','course_code','dept_code__dept_code').order_by('-level_of_course__level')
    courses_users = CourseUserMapping.objects.filter(course_id=course_id).values('to_user_id__username',
                                              'course_id','course__course_name', 'to_user_id','to_user_group_id',
                                              'to_user_id__first_name', 'to_user__email')
    campus_detail = CourseCampusMapping.objects.values('campus__name', 'course_id')
    depart_detail = CourseDepartmentMapping.objects.values('department', 'course_id')
    inst_detail = CourseInstituteMapping.objects.values('institute', 'course_id')

    for i in courses:
        i['encrypt_id'] = encrypt(i['id'])
        i['campus_detail'] = [c['campus__name'] for c in campus_detail if c['course_id'] == i['id']]
        i['depart_detail'] = [c['department'] for c in depart_detail if c['course_id'] == i['id']]
        i['inst_detail'] = [c['institute'] for c in inst_detail if c['course_id'] == i['id']]
        course_status = CourseUserMapping.objects.filter(course_id=i['id']).values('course_id',
                                                                                   'course_status_level_id',
                                                                                   'course_status_level__title').last()
        i['course_status'] = '-'
        if course_status:
            i['course_status'] = course_status['course_status_level__title']
        p=ProgramCourseMapping.objects.filter(program_id=p_id,course_id=i['id'],course_category_id=c_id).values('course_category_id','course_category__category')
        if p:
            i['course_category_id']=p[0]['course_category_id']
        for j in courses_users:
            if i['id'] == j['course_id']:
                if j['to_user_group_id'] == 2:
                    i['csmm_name'] = j['to_user_id__first_name']

                if j['to_user_group_id'] == 3:
                    i['csmi_name'] = j['to_user_id__first_name']

        return i


def get_program_course_category_basket_data(request,p_id,c_id):
    program_courses = ProgramCourseMapping.objects.filter(program_id=p_id,course_category_id=c_id).values()
    s_basket = PrimaryBasketSubBasketMapping.objects.values('sub_basket_id__basket_name',
                                                            'primary_basket_id__basket_name', 'sub_basket_id',
                                                            'primary_basket_id', 'id',
                                                            'sub_basket_id__course_count',
                                                            'sub_basket_id__credit_count',
                                                            'sub_basket_id__choice_count')
    program_baskets = program_courses.filter(basket_id__isnull=False).exclude(basket_id__in=s_basket.values_list('sub_basket_id')).values('basket_id','basket__basket_name','basket__course_count','basket__credit_count').distinct()


    data=[]
    for i in program_baskets:
        basket_course_list = []
        for j in program_courses:
            if i['basket_id'] == j['basket_id']:
                basket_course_list.append(get_program_course_data(j['course_id'], p_id, c_id))
        i['basket_course_list']=basket_course_list

        sub_basket_data = []
        for s in s_basket.filter(primary_basket_id=i['basket_id']):
            l=[]
            for j in program_courses:
                if s['sub_basket_id'] == j['basket_id']:
                    l.append(get_program_course_data(j['course_id'], p_id, c_id))
            s['sub_course_data']=l
            if len(l)>0:
                sub_basket_data.append(s)
        i['sub_basket_data']=sub_basket_data
        data.append(i)
    return data

def get_minor_program_course_basket_data(request,p_id):
    s_basket = PrimaryBasketSubBasketMapping.objects.values('sub_basket_id__basket_name',
                                                            'primary_basket_id__basket_name', 'sub_basket_id',
                                                            'primary_basket_id', 'id',
                                                            'sub_basket_id__course_count',
                                                            'sub_basket_id__credit_count',
                                                            'sub_basket_id__choice_count')
    program_courses = ProgramCourseMapping.objects.filter(program_id=p_id).values()
    program_baskets = program_courses.filter(basket_id__isnull=False).exclude(basket_id__in=s_basket.values_list('sub_basket_id')).values('basket_id','basket__basket_name','basket__course_count','basket__credit_count').distinct()
    data=[]
    for i in program_baskets:
        basket_course_list = []
        for j in program_courses:
            if i['basket_id'] == j['basket_id']:
                basket_course_list.append(get_program_course_data(j['course_id'], p_id,0))
        i['basket_course_list']=basket_course_list
        sub_basket_data = []
        for s in s_basket.filter(primary_basket_id=i['basket_id']):
            l = []
            for j in program_courses:
                if s['sub_basket_id'] == j['basket_id']:
                    l.append(get_program_course_data(j['course_id'], p_id, 0))
            s['sub_course_data'] = l
            if len(l) > 0:
                sub_basket_data.append(s)
        i['sub_basket_data'] = sub_basket_data
        data.append(i)
    return data
    




def get_syllabus(request, course_id):
    a = CourseUnits.objects.filter(course_id=course_id).values('id', 'unit_no')
    b = CourseSyllabus.objects.filter(course_id=course_id).values()
    syllabus = []
    for i in a:
        for j in b:
            if i['id'] == j['course_unit_id']:
                syllabus.append(j)
    return b


def get_course_book_details(request, course_id):
    course_details = ''
    if CourseBooks.objects.filter(course_id=course_id).exists():
        course_details = CourseBooks.objects.filter(course_id=course_id).values()
    return course_details


def get_ref_details(request, course_id):
    references_details = ''
    if References.objects.filter(course_id=course_id).exists():
        references_details = References.objects.filter(course_id=course_id).values()
    return references_details


def get_journal_details(request, course_id):
    journal_details = ''
    if JournalBooks.objects.filter(course_id=course_id).exists():
        journal_details = JournalBooks.objects.filter(course_id=course_id).values()
    return journal_details


def get_website_details(request, course_id):
    website_details = ''
    if Websites.objects.filter(course_id=course_id).exists():
        website_details = Websites.objects.filter(course_id=course_id).values()
    return website_details    