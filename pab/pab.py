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
from course_management.course_operations import co_po_pso_average
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
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

@login_required
@group_required('PAB')
def index(request):
    programs = ProgramUserMapping.objects.filter(to_user_id=request.user.id).values('program__name','program_status_level__title',
                                                                                    'program__program_type__type',
                                                                                    'program_id').order_by('-created')
    program = []
    program_id =[]
    for i in programs:
        if not i['program_id'] in program_id:
            i['encrypt_id'] = encrypt(i['program_id'])
            program.append(i)
        program_id.append(i['program_id'])
    return render(request, 'pab/programs.html', {'programs': program})

@login_required
def programs(request):
    programs = ProgramUserMapping.objects.filter(to_user_id=request.user.id).values('program__name',
                                                                                    'program__program_type__type','program_id')
    program = []
    for i in programs:
        i['encrypt_id']=encrypt(i['program_id'])
        program.append(i)

    return render(request,'pab/programs.html',{'programs':program})



def handle_uploaded_file(f,temp_file):
    with open('media/'+temp_file+'.xlsx', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
def program_detail(request,p_id):
    p_id = decrypt(p_id)
    program=Programs.objects.filter(id=p_id).values()
    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id).\
                                                                                    values('user_id','is_edit','program_status_level_id').last()

        program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id')

        courses = Course.objects.filter(program_id=p_id).values('course_name','course_category__category','course_type__name','id',
                                                              'level_of_course__level','L','T','P','J','S','C','level_of_course_id','course_header_id').order_by('-created')
        assign_courses = CourseUserMapping.objects.filter(course__program_id=p_id).values('course_status_level__title','course_id')
        program_timeline = []
        program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created','to_user_id','user__first_name','user_id','program_status_level__title','to_user__first_name','user__image','comment',
                                                                                             'to_user_group__description',
                                                                                             'user_group__description').order_by('-id')

        pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id).values('created', 'to_user_id',
                                                                                     'program_status_level__title',
                                                                                     'to_user__first_name',
                                                                                     'to_user__image', 'comment','to_user_group__description','user_group__description').last()
        program_timeline.append(pending_timeline)
        program_timeline.extend(program_timeline_actions)

        program_structures =[]
        for i in program_level:
            c=[]
            c_ids = []
            for j in courses:
                if not j['course_header_id'] in c_ids:
                    if i['level_id'] == j['level_of_course_id']:
                        for k in assign_courses:
                            if j['id'] == k['course_id']:
                                j['course_status'] = k['course_status_level__title']
                                j['encrypt_id'] = encrypt(j['id'])
                        c.append(j)
                c_ids.append(j['course_header_id'])
            i['course_structures']= c
            if len(c)>0:
                program_structures.append(i)
        if ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,is_edit=1).exists():
            is_edit = 1
        else:
            is_edit = 0
        return render(request, 'pab/program_detail.html', {'levels': program_level,'p_id':p_id,'program_structures':program_structures,
                                                            'program_assign_details':program_assign_details,'program_timeline':program_timeline,
                                                            'program_id':encrypt(p_id),'is_edit':is_edit,'program':program.last()})
    else:
        return redirect('/')

@login_required
def program_structure_need_more(request,p_id):
    p_id = decrypt(p_id)
    if request.method == "POST":
        try:
            program = Programs.objects.get(id=p_id)
            to_user_group = UserGroups.objects.filter(user_id=program.user_id, is_active=1, is_block=0).values('group_id')
            user_group = UserGroups.objects.filter(user_id=request.user.id, is_active=1, is_block=0).values('group_id')
            ProgramUserMapping.objects.create(created=datetime.now(),is_edit=0,program_id=p_id,program_status_level_id=9,comment=request.POST['pab_message'],
                                              to_user_id=program.user_id,user_id=request.user.id,to_user_group_id=to_user_group[0]['group_id'],user_group_id=user_group[0]['group_id'])
            ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,program_status_level_id=7).update(is_edit=0)
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Please find the suggestions for the curriculum and syllabi of "+program.name
            message = render_to_string('pab/email_templates/suggestions_email.html', {
                'domain': current_site.domain,
                'guest_firstname': program.user.first_name,
                'program': program.name,
            })
            e = send_html_mail(mail_subject, message, [program.user.email], sender)
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Thank you for accepting our request as a member of the Programme Advisory Board for Programme "+program.name
            message = render_to_string('pab/email_templates/thanks_to_pab.html', {
                'domain': current_site.domain,
                'guest_firstname': request.user.first_name,
                'program': program.name,
            })
            e = send_html_mail(mail_subject, message, [request.user.email], sender)
            messages.success(request, 'Submitted Successfully')
            return redirect('program_detail', encrypt(p_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('program_detail', encrypt(p_id))
    else:
            return redirect('program_detail', encrypt(p_id))


@login_required
def course_preview(request,course_id):
    course_id = decrypt(course_id)
    dept = DepartmentInstituteCodes.objects.values('id', 'dept_inst')
    course_type = CourseType.objects.values('id', 'name')
    level_of_course = LevelOfCourse.objects.values('id', 'level')
    course_category = CourseCategory.objects.values('id', 'category')
    course_details = Course.objects.get(id=course_id)
    course_syllabus = get_syllabus(request, course_id,)
    course_book_details = get_course_book_details(request, course_id)
    references_details = get_ref_details(request, course_id)
    journal_details = get_journal_details(request, course_id)
    website_details = get_website_details(request, course_id)
    course = Course.objects.filter(id=course_id).values()
    course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    pso = ProgramSpecificOutcome.objects.filter(course_id=course_id).values('id', 'pso')
    pedagogy_tools = PedagogyTools.objects.values('id', 'name')
    co_po_pso = CourseCoPoPso.objects.filter(course_id=course_id).values()
    co_po_psos = []
    count = 0
    course_owner=CourseUserMapping.objects.filter(is_active=1,to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()
    
    for co in course_outcome:
        co['po'] = co_po_pso[count]
        co_po_psos.append(co)
        count = count + 1
    course_timeline = []
    course_timeline_actions = CourseUserMapping.objects.filter(course_id=course_id,is_edit=1).values('created', 'to_user_id',
                                                                                         'user__first_name', 'user_id',
                                                                                         'course_status_level__title',
                                                                                         'to_user__first_name',
                                                                                         'user__image',
                                                                                         'comment').order_by('-id')

    pending_timeline = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                                                                                 'course_status_level__title',
                                                                                 'to_user__first_name',
                                                                                 'to_user__image', 'comment').last()
    course_timeline.append(pending_timeline)
    course_timeline.extend(course_timeline_actions)
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=9,is_edit=1,to_user_id=request.user.id).exists():
        is_edit = 1
    else:
        is_edit = 0
    copo_average = co_po_pso_average(request, co_po_pso, course_id)
    context = {'course_id': encrypt(course_details.id), 'dept': dept,
               'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
               'course_details': course_details, 'active_step': course_details.active_step,
               'course_syllabus': course_syllabus,'p_id':encrypt(course_details.program_id),
               'course_book_details': course_book_details, 'references_details': references_details, 'course': course,
               'course_outcome': course_outcome,'is_edit':is_edit,'copo_average':copo_average,
               'pso': pso,  'co_po_pso': co_po_psos,'course_timeline':course_timeline,'course_owner':course_owner,
               'pedagogy_tools': pedagogy_tools,'journal_details':journal_details,'website_details':website_details}
    return render(request, 'pab/preview.html',context)


def get_syllabus(request,course_id):
    a = CourseUnits.objects.filter(course_id=course_id).values('id','unit_no')
    b = CourseSyllabus.objects.filter(course_id=course_id).values()
    syllabus = []
    for i in a:
        for j in b:
            if i['id'] == j['course_unit_id']:
                syllabus.append(j)
    return syllabus

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
    
@login_required
def course_structure_approve(request,c_id):
    c_id=decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id,to_user_id=request.user.id,course_status_level_id=4).exists():
                bosc_user = CourseUserMapping.objects.filter(course_id=c_id).values('course__program__user')
                CourseUserMapping.objects.create(course_id=c_id,to_user_id=bosc_user[0]['course__program__user'],user_id=request.user.id,course_status_level_id=5,is_edit=1,
                                                 course_header_id = course.course_header_id)
                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                 course_status_level_id=4).update(is_edit=0)
            return redirect('course_preview_pcmi', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_pcmi', encrypt(c_id))
    return redirect('course_preview_pcmi',encrypt(c_id))

