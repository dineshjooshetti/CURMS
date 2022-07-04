from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from course_management.models import *
from user_management.models import *
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
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.template.loader import render_to_string
from user_management.utils import *
# Create your views here.
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
@group_required('STAFF')
def index(request):
    template=None
    context=''
    course_details = CourseUserMapping.objects.filter(to_user_id=request.user.id,to_user_group=1).values('is_edit','course_id')
    course = Course.objects.filter(id__in=course_details.values_list('course_id')).values('id','version_status',
                                             'course_name','course_type__name','course_code').order_by('-created')
    course_det = []
    for i in course:
        i['encrypt_id'] = encrypt(i['id'])
        course_det.append(i)
    return render(request, 'staff/index.html',{'course_det':course_det})


@login_required
def course_preview_staff(request,course_id):
    course_id = decrypt(course_id)
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups__in=[1],to_user_id=request.user.id).exists():
        user_course_mapping = CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=1,to_user_id=request.user.id).values().last()
        course_details = Course.objects.get(id=course_id)
        course_syllabus = get_syllabus(request, course_id, )
        course_book_details = get_course_book_details(request, course_id)
        references_details = get_ref_details(request, course_id)
        journal_details = get_journal_details(request, course_id)
        website_details = get_website_details(request, course_id)
        course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
        pso = ProgramSpecificOutcome.objects.filter(course_id=course_id).values('id', 'pso')
        co_po_pso = CourseCoPoPso.objects.filter(course_id=course_id).values()
        pedagogy_tools = PedagogyTools.objects.values('id', 'name')
        co_po_psos = []
        count = 0
        course_owner=CourseUserMapping.objects.filter(is_active=1,to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()
        for co in course_outcome:
            co['po'] = co_po_pso[count]
            co_po_psos.append(co)
            count = count + 1
        course_timeline = []
        course_timeline_actions = CourseUserMapping.objects.filter(course_id=course_id, is_edit=1).values('created',
                                                                                                          'to_user_id',
                                                                                                          'user__first_name',
                                                                                                          'user_id',
                                                                                                          'course_status_level__title',
                                                                                                          'to_user__first_name',
                                                                                                          'user__image',
                                                                                                          'comment','to_user_group__description',
                                                                                    'user_group__description').order_by(
            '-id')

        pending_timeline = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                                                                                        'course_status_level__title',
                                                                                        'to_user__first_name',
                                                                                        'to_user__image', 'comment','to_user_group__description',
                                                                                    'user_group__description').last()
        course_timeline.append(pending_timeline)
        course_timeline.extend(course_timeline_actions)
        copo_average = co_po_pso_average(request, co_po_pso, course_id)
        context = {'course_id': encrypt(course_details.id),
                   'course_details': course_details, 'active_step': course_details.active_step,
                   'course_syllabus': course_syllabus, 'p_id': encrypt(course_details.program_id),
                   'course_book_details': course_book_details, 'references_details': references_details,
                   'course_outcome': course_outcome, 'pedagogy_tools': pedagogy_tools,'copo_average':copo_average,'course_owner':course_owner,
        
                   'pso': pso, 'co_po_pso': co_po_psos, 'course_timeline': course_timeline, 'user_course_mapping': user_course_mapping,
                   'journal_details':journal_details,'website_details':website_details}
        return render(request, 'staff/preview.html',context)

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
    if JournalBooks.objects.filter(course_id=course_id).exists():
        journal_details =JournalBooks.objects.filter(course_id=course_id).values()
    return journal_details

def get_website_details(request,course_id):
    website_details = ''
    if Websites.objects.filter(course_id=course_id).exists():
        website_details =Websites.objects.filter(course_id=course_id).values()
    return website_details
    
def get_syllabus(request,course_id):
    a = CourseUnits.objects.filter(course_id=course_id).values('id','unit_no')
    b = CourseSyllabus.objects.filter(course_id=course_id).values()
    syllabus = []
    for i in a:
        for j in b:
            if i['id'] == j['course_unit_id']:
                syllabus.append(j)
    return syllabus


@login_required
def staff_suggestion(request,c_id):
    c_id=decrypt(c_id)
    if request.method == 'POST':
        try:
            to_user_id = CourseUserMapping.objects.filter(course_id=c_id, course_status_level_id=1,
                                                          to_user_group_id=3).values('to_user_id', 'course_header_id')
            CourseUserMapping.objects.create(created=datetime.now(), is_edit=0, course_id=c_id,
                                             course_status_level_id=12, to_user_group_id=3, user_group_id=1,
                                             to_user_id=to_user_id[0]['to_user_id'], user_id=request.user.id,
                                             course_header_id=to_user_id[0]['course_header_id'],comment=request.POST.get('message'),)
            CourseUserMapping.objects.filter(course_id=c_id, to_user_group_id=1,course_status_level_id=3,to_user_id=request.user.id).update(is_edit=0)
            email = User.objects.filter(id=to_user_id[0]['to_user_id']).values('email', 'id', 'first_name')
            course = Course.objects.get(id=c_id)
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Suggestions regarding "+course.course_name
            message = render_to_string('staff/email_templates/staff_forward_csmi_email.html', {
                'email': encrypt(email[0]['email']),
                'domain': current_site.domain,
                'guest_firstname': email[0]['first_name'],
                'course_code': course.course_code,
                'course_name': course.course_name,
            })
            e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, "Submitted....")
            return redirect('course_preview_staff', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_staff', encrypt(c_id))
    return redirect('course_preview_staff',encrypt(c_id))