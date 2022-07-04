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
from django.db.models import Q
import ast
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from user_management.encryption_util import *
from django.contrib.auth.decorators import user_passes_test
import xlrd
from course_management.course_operations import co_po_pso_average

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

@login_required
@group_required('PCMC')
def index(request):
    programs = ProgramUserMapping.objects.filter(Q(to_user_id=request.user.id) , Q(is_active=1),Q(to_user_group_id=4)).values('program__name',
                                                                                                        'program_status_level__title',
                                                                                                        'program__program_type__type',
                                                                                                        'program_id').order_by('-created')
    program = []
    program_id = []
    for i in programs:
        if not i['program_id'] in program_id:
            i['encrypt_id'] = encrypt(i['program_id'])
            program.append(i)
        program_id.append(i['program_id'])
    return render(request, 'pcmc/programs.html', {'programs': program})


@login_required
@group_required('PCMC')
def pcmc_program_detail(request,p_id):
    p_id = decrypt(p_id)
    program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id).values('user_id','is_edit','program_status_level_id','program__name')
    if program_assign_details:
        program_assign_details=program_assign_details.last()
        program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id')

        courses = Course.objects.filter(program_id=p_id).values('course_name','course_category__category','course_type__name','id',
                                                                'level_of_course__level','L','T','P','J','S','C','level_of_course_id','course_header_id').order_by('-created')
        assign_courses = CourseUserMapping.objects.filter(course__program_id=p_id).values('course_status_level__title','course_id')
        program_timeline = []
        program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created','to_user_id','user__first_name','user_id',
                                                                                             'program_status_level__title','to_user__first_name',
                                                                                             'user__image','comment','to_user_group__description',
                                                                                             'user_group__description').order_by('-id')

        pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id,is_edit=1).values('created', 'to_user_id',
                                                                                               'program_status_level__title',
                                                                                               'to_user__first_name',
                                                                                               'to_user__image', 'comment','to_user_group__description',
                                                                                               'user_group__description').last()
        program_timeline.append(pending_timeline)
        program_timeline.extend(program_timeline_actions)
        
        program_structures =[]
        for i in program_level:
            c=[]
            c_ids = []
            for j in courses:
                if not j['course_header_id'] in c_ids:
                    if j['level_of_course_id']==i['level_id']:
                        for k in assign_courses:
                            if j['id'] == k['course_id']:
                                j['course_status'] = k['course_status_level__title']
                                j['encrypt_id'] = encrypt(j['id'])
                        c.append(j)
                c_ids.append(j['course_header_id'])
            i['course_structures']= c
            if len(c)>0:
                program_structures.append(i)
        return render(request, 'pcmc/program_detail.html', {'levels': program_level,'p_id':p_id,'program_structures':program_structures,
                                                        'program_assign_details':program_assign_details,'program_timeline':program_timeline})
    else:
        return redirect('/')


@login_required
@group_required('PCMC')
def course_preview(request,course_id):
    course_id = decrypt(course_id)
    if Course.objects.filter(id=course_id).exists():
        dept = DepartmentInstituteCodes.objects.values('id', 'dept_inst')
        course_type = CourseType.objects.values('id', 'name')
        level_of_course = LevelOfCourse.objects.values('id', 'level')
        course_category = CourseCategory.objects.values('id', 'category')
        course_details = Course.objects.get(id=course_id)
        course_syllabus = get_syllabus(request, course_id, )
        course_book_details = get_course_book_details(request, course_id)
        references_details = get_ref_details(request, course_id)
        journal_details = get_journal_details(request, course_id)
        website_details = get_website_details(request, course_id)
        course = Course.objects.filter(id=course_id).values()
        course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
        pso = ProgramSpecificOutcome.objects.filter(course_id=course_id).values('id', 'pso')
        pedagogy_tools = PedagogyTools.objects.values('id', 'name')
        co_po_pso = CourseCoPoPso.objects.filter(course_id=course_id).values()
        practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values('topic','syllabus_type__name')
        course_owner=CourseUserMapping.objects.filter(is_active=1,to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()
        co_po_psos = []
        count = 0
        if co_po_pso:
            for co in course_outcome:
                co['po'] = co_po_pso[count]
                co_po_psos.append(co)
                count = count + 1
        course_timeline = []
        course_timeline_actions = CourseUserMapping.objects.filter(course_id=course_id).values('created','to_user_id','user__first_name','user_id',
                                   'course_status_level__title','to_user__first_name','user__image', 'to_user_group__description','user_group__description',
                                    'comment').order_by('-id')

        pending_timeline = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                             'course_status_level__title','to_user__first_name','to_user_group__description',
                            'user_group__description','to_user__image', 'comment').last()
        course_view_access=None
        if course_timeline_actions.filter(course_status_level_id=4,to_user_id=request.user.id,is_active=1).exists():
            course_view_access=1                    
        course_timeline.append(pending_timeline)
        course_timeline.extend(course_timeline_actions)
        copo_average = co_po_pso_average(request, co_po_pso, course_id)
        context = {'course_id': encrypt(course_details.id), 'dept': dept,'practical_syllabus':practical_syllabus,
                   'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
                   'course_details': course_details, 'active_step': course_details.active_step,'course_owner':course_owner,
                   'course_syllabus': course_syllabus, 'p_id': encrypt(course_details.program_id),
                   'course_book_details': course_book_details, 'references_details': references_details, 'course': course,
                   'course_outcome': course_outcome,'copo_average':copo_average,
                   'pso': pso, 'co_po_pso': co_po_psos, 'course_timeline': course_timeline,'course_view_access':course_view_access,
                   'pedagogy_tools': pedagogy_tools,'journal_details':journal_details,'website_details':website_details}
        return render(request, 'pcmc/preview.html',context)
    else:
        return redirect('/')


def get_syllabus(request,course_id):
    a = CourseUnits.objects.filter(course_id=course_id).values('id','unit_no')
    b = CourseSyllabus.objects.filter(course_id=course_id).values()
    syllabus = []
    for i in a:
        for j in b:
            if i['id'] == j['course_unit_id']:
                syllabus.append(j)
    return b

def get_course_book_details(request,course_id):
    course_details = ''
    if CourseBooks.objects.filter(course_id=course_id).exists():
        course_details =CourseBooks.objects.filter(course_id=course_id).values()
    return course_details

def get_ref_details(request,course_id):
    references_details = ''
    if References.objects.filter(course_id=course_id).exists():
        references_details =References.objects.filter(course_id=course_id).values()
    return references_details

def get_journal_details(request,course_id):
    journal_details = ''
    print(course_id)
    if JournalBooks.objects.filter(course_id=course_id).exists():
        journal_details =JournalBooks.objects.filter(course_id=course_id).values()
    return journal_details

def get_website_details(request,course_id):
    website_details = ''
    if Websites.objects.filter(course_id=course_id).exists():
        website_details =Websites.objects.filter(course_id=course_id).values()
    return website_details