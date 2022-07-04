from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from programs.models import *
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from user_management.encryption_util import *
from course_management.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.template.loader import render_to_string
from user_management.utils import *
from course_management.course_operations import co_po_pso_average
from .csmc import *
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

@login_required
@group_required('CSMI')
def index(request):
    template=None
    context=''
    course_details = CourseUserMapping.objects.filter(to_user_id=request.user.id,to_user_group_id=3,course_status_level_id__in=[1,13],is_active=1).values('is_edit','course_id', 'course_header_id','course__version_status','course__course_name',
                                          'course__course_code','course__course_type__name','course_id','user__first_name','user__username','course__program__name','course__course_category__category').order_by('-created')
    course = Course.objects.filter(course_header_id__in=course_details.values_list('course_header_id')).values('id', 'course_header_id','version_status', 'course_name',
                            'course_type__name','program__name').order_by('-created')

    course_det = []
    course_header = []
    for i in course_details:
        if not i['course_id'] in course_header:
            i['encrypt_id'] = encrypt(i['course_id'])
            course_status= CourseUserMapping.objects.filter(course_id=i['course_id']).values('course_id','course_status_level_id','course_status_level__title').last()
            i['course_status']=course_status['course_status_level__title']
            course_det.append(i)
        course_header.append(i['course_id'])


    return render(request, 'csmi/index.html', {'course_det':course_det})


@login_required
@group_required('CSMI')
def course_preview(request,course_id):
    course_id = decrypt(course_id)
    course_details = Course.objects.get(id=course_id)
    course_syllabus = get_syllabus(request, course_id, )
    course_book_details = get_course_book_details(request, course_id)
    references_details = get_ref_details(request, course_id)
    journal_details = get_journal_details(request, course_id)
    website_details = get_website_details(request, course_id)
    course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    pedagogy_tools = PedagogyTools.objects.values('id', 'name')
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values('topic','syllabus_type__name')
    course_owner=CourseUserMapping.objects.filter(is_active=1,to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()
    course_pre_requisite = CoursePrerequestiesMapping.objects.filter(course_id=course_id).values('id','prerequesti__course_name')


    course_timeline = []
    course_timeline_actions = CourseUserMapping.objects.filter(course_id=course_id).values('created','to_user_id',
                                                                                                      'user__first_name','user_id',
                                                                                                      'course_status_level__title',
                                                                                                      'to_user__first_name','course_status_level_id',
                                                                                                      'user__image','comment',
                                                                                                      'to_user_group__description',
                                                                                    'user_group__description').order_by('-id')

    pending_timeline = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                                                                                    'course_status_level__title',
                                                                                    'to_user__first_name',
                                                                                    'to_user__image', 'comment',
                                                                                    'to_user_group__description',
                                                                                    'user_group__description').last()
    course_timeline.append(pending_timeline)
    course_timeline.extend(course_timeline_actions)
    course_owner_submit=False
    if course_timeline_actions.filter(course_status_level_id=2).exists():
        course_owner_submit=True
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=3,is_edit=1,to_user_id=request.user.id).exists():
        is_edit = 1
    else:
        is_edit = 0
    context = {'course_id': encrypt(course_details.id),
               'course_details': course_details, 'active_step': course_details.active_step,'practical_syllabus':practical_syllabus,
               'course_syllabus': course_syllabus, 'p_id': encrypt(course_details.program_id),
               'course_book_details': course_book_details, 'references_details': references_details,'course_owner_submit':course_owner_submit,
               'course_outcome': course_outcome,'pedagogy_tools':pedagogy_tools,'course_owner':course_owner,
               'course_pre_requisite':course_pre_requisite,
               'course_timeline': course_timeline,'is_edit':is_edit,'journal_details':journal_details,'website_details':website_details}
    return render(request, 'csmi/course_preview.html',context)

@login_required
@group_required('CSMI')
def course_forward_to_faculty(request,course_id):
    course_id = decrypt(course_id)
    if request.method == "POST":
        try:
            course = Course.objects.get(id=course_id)
            faculyt_ids = request.POST.getlist('faculty')
            for i in range(0, len(faculyt_ids)):
                CourseUserMapping.objects.create(created=datetime.now(),is_edit=1,course_id=course_id,
                                                 course_status_level_id=3,to_user_id=faculyt_ids[i],user_id=request.user.id,course_header_id=course.course_header_id,
                                                 to_user_group_id=1,user_group_id=3)
                email = User.objects.filter(id=faculyt_ids[i]).values('email', 'id', 'first_name')
                course = Course.objects.get(id=course_id)
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Being a subject expert in "+course.course_name+", requested to check the syllabus and suggest modifications (if any)."
                message = render_to_string('csmi/email_templates/csmi_forward_staff_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'course_code': course.course_code,
                    'course_name': course.course_name,

                })
                e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, "Forwaded Sucessfully...")
            return redirect('/csmi/course_details_by_csmi/'+encrypt(course_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            return redirect('/csmi/course_details_by_csmi/' + encrypt(course_id))
    else:
        return redirect('/csmi/course_details_by_csmi/' + encrypt(course_id))

@login_required
@group_required('CSMI')
def course_forward_to_bosc(request,course_id):
    course_id = decrypt(course_id)
    course = Course.objects.get(id=course_id)
    if request.method == "POST":
        try:
            Course.objects.filter(id=course_id).update(version_status=1,status_id=4)
            CourseUserMapping.objects.filter(course_id=course_id,to_user_id=request.user.id).update(is_edit=0)
            CourseUserMapping.objects.create(created=datetime.now(),is_edit=1,course_id=course_id,to_user_group_id=6,user_group_id=3,
                                             course_status_level_id=4,to_user_id=course.created_by_id,user_id=request.user.id)
            email = User.objects.filter(id=course.created_by_id).values('email', 'id', 'first_name')
            course = Course.objects.get(id=course_id)
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Syllabus of "+course.course_name+" has been prepared and submitted for your Approval/Suggestions."
            message = render_to_string('csmi/email_templates/csmi_forward_pcmi.html', {
                'email': encrypt(email[0]['email']),
                'domain': current_site.domain,
                'guest_firstname': email[0]['first_name'],
                'course_code': course.course_code,
                'course_name': course.course_name,

            })
            e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            EmailStatus.objects.create(hint='CSMI forward to BOSC', message=message,to_user_email=email[0]['email'], to_user_id=email[0]['id'],user_id=request.user.id)
            messages.success(request, "Forwaded Sucessfully...")
            return redirect('/csmi/course_preview/'+encrypt(course_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            return redirect('/csmi/course_preview/' + encrypt(course_id))
    else:
        return redirect('/csmi/course_preview/' + encrypt(course_id))

@login_required
def course_new_version_by_csmi(request,course_id):
    course_id = decrypt(course_id)
    if request.method == "POST":
        version = Course.objects.get(id=course_id)
        try:
            Course.objects.filter(id=course_id).update(version_status=0,active_step=1)
            #CourseUserMapping.objects.filter(course_id=course_id,to_user_id=request.user.id,course_status_level_id=6).update(is_edit=0)
            # course = Course.objects.filter(id=course_id).values()
            # course_outcome = CourseOutcome.objects.filter(course_id=course_id).values()
            # program_out_come = ProgramSpecificOutcome.objects.filter(course_id=course_id).values()
            # course_units = CourseUnits.objects.filter(course_id=course_id).values()
            # course_syllabus = CourseSyllabus.objects.filter(course_id=course_id).values()
            # course_syllabus_practical = CourseSyllabusPractical.objects.filter(course_id=course_id).values()
            # course_books = CourseBooks.objects.filter(course_id=course_id).values()
            # course_referance = References.objects.filter(course_id=course_id).values()
            # co_po_pso = CourseCoPoPso.objects.filter(course_id=course_id).values()
            # insert = None
            # unit = None
            # if course:
                # for c in course:
                    # a_dict = c
                    # a_dict.pop('id')
                    # insert = Course.objects.create(**a_dict)
                    # Course.objects.filter(id=insert.id).update(created=datetime.now(),created_by_id=request.user.id,version=float(version.version)+float(0.1),version_status=0)
            # if course_outcome:
                # for c in course_outcome:
                    # CourseOutcome.objects.create(course_outcome=c['course_outcome'],course_id=insert.id,user_id=request.user.id,
                                                  # created=datetime.now())
            # if program_out_come:
                # for po in program_out_come:
                    # ProgramSpecificOutcome.objects.create(pso=po['pso'],created=datetime.now(),course_id=insert.id,user_id=request.user.id)
            # if course_units:
                # for u in course_units:
                    # unit = CourseUnits.objects.create(unit_no=u['unit_no'],course_id=insert.id)
            # if course_syllabus:
                # for cs in course_syllabus:
                    # CourseSyllabus.objects.create(unit_name=cs['unit_name'],short_title=cs['short_title'],number_of_contact_hours=cs['number_of_contact_hours'],
                                                  # version=float(version.version)+float(0.1),created=datetime.now(),course_id=insert.id,created_by_id=request.user.id,pedagogy_tool_1_id=cs['pedagogy_tool_1_id'],
                                                  # pedagogy_tool_2_id=cs['pedagogy_tool_2_id'],level_1=cs['level_1'],level_2=cs['level_2'],level_3=cs['level_3'],
                                                  # level_4=cs['level_4'],level_5=cs['level_5'],outcome_1=cs['outcome_1'],outcome_2=cs['outcome_2'],outcome_3=cs['outcome_3'],
                                                  # outcome_4=cs['outcome_4'],outcome_5=cs['outcome_5'],course_unit_id=unit.id)
            # if course_syllabus_practical:
                # for sp in course_syllabus_practical:
                    # CourseSyllabusPractical.objects.create(topic=sp['topic'],version=float(version.version)+float(0.1),created=datetime.now(),course_id=insert.id,syllabus_type_id=sp['syllabus_type_id'],
                                                           # user_id=request.user.id)
            # if course_books:
                # for cb in course_books:
                    # CourseBooks.objects.create(title=cb['title'],author=cb['author'],publisher=cb['publisher'],place_of_publication=cb['place_of_publication'],
                                               # year=cb['year'],edition=cb['edition'],created=datetime.now(),created_by_id=request.user.id,course_id=insert.id)
            # if course_referance:
                # for cr in course_referance:
                    # References.objects.create(title=cr['title'],author=cr['author'],publisher=cr['publisher'],place_of_publication=cr['place_of_publication'],
                                              # year=cr['year'],edition=cr['edition'],created=datetime.now(),created_by_id=request.user.id,course_id=insert.id)
            # if co_po_pso:
                # for copo in co_po_pso:
                    # CourseCoPoPso.objects.create(co=copo['co'],po1=copo['po1'],po2=copo['po2'],po3=copo['po3'],po4=copo['po4'],po5=copo['po5'],po6=copo['po6'],
                                                 # po7=copo['po7'],po8=copo['po8'],po9=copo['po9'],po10=copo['po10'],po11=copo['po11'],po12=copo['po12'],
                                                 # pso1=copo['pso1'],pso2=copo['pso2'],pso3=copo['pso3'],pso4=copo['pso4'],created=datetime.now(),
                                                 # user_id=request.user.id,course_id=insert.id)
            # CourseUserMapping.objects.create(created=datetime.now(),is_edit=1,to_user_id=request.user.id,user_id=request.user.id,
                                             # course_status_level_id=7,course_id=insert.id,course_header_id=insert.course_header_id)
            return redirect('/csmi/course_details/'+encrypt(course_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            return redirect('/csmi/course_details_by_csmi/' + encrypt(course_id))
    else:
        return redirect('/csmi/course_details_by_csmi/' + encrypt(course_id))

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