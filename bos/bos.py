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
@group_required('BOS')
def index(request):
    depts=BoschairInstituteMapping.objects.filter(bos_chair_id=request.user.id).values_list('dept_code_id')
            
    programs = ProgramUserMapping.objects.filter(user__dept_code_id__in=depts,program_status_level_id=11).values(
        'id', 'program__name', 'program_status_level__title','user__dept_code__dept_code',
        'program__program_type__type','program__department',
        'program_id').order_by('-created')
    program = []
    program_id = []
    for i in programs:
        if not i['program_id'] in program_id:
            i['encrypt_id'] = encrypt(i['program_id'])
            program.append(i)
        program_id.append(i['program_id'])
    inst = BoschairInstituteMapping.objects.filter(bos_chair_id=request.user.id).values_list('institute',flat=True)
    departments = BoschairInstituteMapping.objects.filter(bos_chair_id=request.user.id).values('dept_code__dept_code')
    user_data = {}
    for i in departments:
        i['department']=i['dept_code__dept_code']
        user_data[i['department']] = []
        for j in program:
            if i['department'] == j['user__dept_code__dept_code']:
                j['encrypt_id'] = encrypt(j['program_id'])
                user_data[i['department']].append(j)
    return render(request,'bos/index.html',{'programs':program,'user_data':user_data})


@login_required
@group_required('BOS')
def bos_program_detail(request,p_id):
    p_id = decrypt(p_id)
    program=Programs.objects.filter(id=p_id).values()
    if program:
        program_detail = ProgramUserMapping.objects.exclude(program_status_level_id__in=[1,8,9]).filter(program_id=p_id, to_user_id=request.user.id,
                                                           ).values('user_id', 'is_edit','program_status_level_id','comment')
        program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created','to_user_id','user__first_name','user_id','program_status_level__title',
                                                                'to_user__first_name','user__image','comment','to_user_group__description','user_group__description').order_by('-id')

        campus_detail = CourseCampusMapping.objects.filter(course__program_id=p_id).values('campus__name', 'course_id')
        depart_detail = CourseDepartmentMapping.objects.filter(course__program_id=p_id).values('department',
                                                                                               'course_id')
        inst_detail = CourseInstituteMapping.objects.filter(course__program_id=p_id).values('institute', 'course_id')

        program_structures = []
        program_assign_details=''
        program_level =''
        program_timeline = []
        courses = ''
        if program_detail:
            pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id).values('created', 'to_user_id',
                                                                                         'program_status_level__title',
                                                                                         'to_user__first_name',
                                                                                         'to_user__image', 'comment','to_user_group__description','user_group__description').last()
            program_timeline.append(pending_timeline)
            program_assign_details = program_detail.last()
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id')

            courses = Course.objects.filter(program_id=p_id).values('course_name', 'course_category__category',
                                                                    'course_type__name', 'id',
                                                                    'level_of_course__level', 'L', 'T', 'P', 'J', 'S', 'C',
                                                                    'level_of_course_id', 'course_header_id').order_by('-created')
                                                                    
            
            for i in program_level:
                c = []
                c_ids = []
                for j in courses:
                    if not j['course_header_id'] in c_ids:
                        if j['level_of_course_id']==i['level_id']:
                            j['encrypt_id'] = encrypt(j['id'])
                            c.append(j)
                    c_ids.append(j['course_header_id'])
                i['course_structures'] = c
                if len(c) > 0:
                    program_structures.append(i)
        program_timeline.extend(program_timeline_actions)

        if ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,is_edit=1,program_status_level_id=6).exists():
            is_edit = 1
        else:
            is_edit = 0
        return render(request,'bos/program_detail.html',{'levels': program_level,'p_id':encrypt(p_id),'program_structures':program_structures,
                                                            'program_assign_details':program_assign_details,'program_timeline':program_timeline,
                                                          'is_edit':is_edit,'campus_detail':campus_detail,'depart_detail':depart_detail,'program':program.last(),
                                                         'inst_detail':inst_detail,'courses':courses})
    else:
        return redirect('/')

@login_required
@group_required('BOS')
def course_preview_bos(request,course_id):
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
    course_timeline_actions = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                                                                                         'user__first_name', 'user_id',
                                                                                         'course_status_level__title',
                                                                                         'to_user__first_name',
                                                                                           'to_user_group__description','user_group__description',
                                                                                         'user__image',
                                                                                         'comment').order_by('-id')

    pending_timeline = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                                                                                 'course_status_level__title',
                                                                                 'to_user__first_name',
                                                                                    'to_user_group__description','user_group__description',
                                                                                 'to_user__image', 'comment').last()
    course_timeline.append(pending_timeline)
    course_timeline.extend(course_timeline_actions)
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=7,is_edit=1,to_user_id=request.user.id,course_status_level_id__in=[10,16]).exists():
        is_edit = 1
    else:
        is_edit = 0
    copo_average = co_po_pso_average(request, co_po_pso, course_id)
    context = {'course_id': encrypt(course_details.id), 'dept': dept,'practical_syllabus':practical_syllabus,
               'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
               'course_details': course_details, 'active_step': course_details.active_step,
               'course_syllabus': course_syllabus,'p_id':encrypt(course_details.program_id),
               'course_book_details': course_book_details, 'references_details': references_details, 'course': course,
               'course_outcome': course_outcome,'is_edit':is_edit,'copo_average':copo_average,
               'pso': pso,  'co_po_pso': co_po_psos,'course_timeline':course_timeline,'course_owner':course_owner,
               'pedagogy_tools': pedagogy_tools,'journal_details':journal_details,'website_details':website_details}
    return render(request, 'bos/preview.html',context)

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

@login_required
@group_required("BOS")
def forward_program_to_doaa_by_bos(request,p_id):
    p_id=decrypt(p_id)
    if request.method == "POST":
        try:
            bos_user = Programs.objects.filter(id=p_id).values('user_id')
            user_group = UserGroups.objects.filter(user_id=request.user.id, is_active=1, is_block=0).values('group_id')
            ProgramUserMapping.objects.create(created=datetime.now(),is_edit=1,program_id=p_id,program_status_level_id=12,
                                              to_user_id=None,user_id=request.user.id,to_user_group_id=8,
                                              user_group_id=7)
                                              
            course = CourseUserMapping.objects.filter(course_status_level_id=1, course__program_id=p_id).values(
                'course_id', 'course_header_id').distinct()
            for i in course:
                if not CourseUserMapping.objects.filter(course_status_level_id=17, course_id=i['course_id']).exists():
                    CourseUserMapping.objects.create(course_id=i['course_id'], to_user_id=4220,
                                                     user_id=request.user.id, course_status_level_id=17, is_edit=1,
                                                     course_header_id=i['course_header_id'], to_user_group_id=8,
                                                     user_group_id=7)
            ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,is_edit=1,program_status_level_id=11).update(is_edit=0)
            progm = Programs.objects.get(id=p_id)
            m = [12,progm.user_id]
            for k in range(len(m)):
                email = User.objects.filter(id=m[k]).values('email', 'id', 'first_name')
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Invite to Review Program structure and syllabus"
                if k == 0 :
                    message = render_to_string('bos/email_templates/bos_forward_doaa_email.html', {
                        'email': encrypt(email[0]['email']),
                        'domain': current_site.domain,
                        'guest_firstname': email[0]['first_name'],
                        'program':'Curriculum and syllabus of '+progm.name+' has been prepared and forwarded for necessary action.',
                    })
                else :
                    message = render_to_string('bos/email_templates/bos_forward_doaa_email.html', {
                        'email': encrypt(email[0]['email']),
                        'domain': current_site.domain,
                        'guest_firstname': email[0]['first_name'],
                        'program': 'Curriculum and syllabus of ' + progm.name + ' has been approved and forwarded to the DoAA.',
                    })
                #e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, 'Forwarded Successfully..')
            return redirect('bos_program_detail',encrypt(p_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('bos_program_detail' , encrypt(p_id))
    else:
        return redirect('bos_program_detail' , encrypt(p_id))


@login_required
@group_required('BOS')
def program_structure_need_more_bos(request,p_id):
    p_id = decrypt(p_id)
    pcmis = ProgramUserMapping.objects.filter(program_id=p_id,program_status_level=6,user_group=5)
    if request.method == 'POST':
        to_user = [request.POST.get('bosc_user_id'), pcmis.last().user_id]
        is_edit = [1, 0]
        group_user = [6, 5]
        try:
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                 user_id=int(request.POST.get('bosc_user_id')),
                                                 program_status_level_id__in=[11,14]).exists():
                for i in range(0,1):
                    ProgramUserMapping.objects.create(program_id=p_id, to_user_id=to_user[i],
                                                  user_id=request.user.id, program_status_level_id=13,
                                                  is_edit=is_edit[i],comment=request.POST.get('bos_message'),
                                                  to_user_group_id=group_user[i],user_group_id=7,)
                ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                  program_status_level_id__in=[11, 14]).update(is_edit=0)
                                                  
            email = User.objects.filter(id=request.POST.get('bosc_user_id')).values('email', 'id', 'first_name')
            progm = Programs.objects.get(id=p_id)
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Suggestions regarding the curriculum and syllabus of "+progm.name+". "
            message = render_to_string('bos/email_templates/bos_sugg_bosc_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'program': progm.name,
                })
            e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            
            messages.success(request, "Submitted Successfully..")
            return redirect('bos_program_detail', encrypt(p_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('bos_program_detail', encrypt(p_id))
    return redirect('bos_program_detail', encrypt(p_id))
    
@login_required
@group_required('BOS')
def course_structure_approve(request,c_id):
    c_id=decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id,to_user_id=request.user.id,course_status_level_id__in=[10,16]).exists():
                bosc_user = CourseUserMapping.objects.filter(course_id=c_id).values('course__program__user')
                CourseUserMapping.objects.create(course_id=c_id,to_user_id=4220,user_id=request.user.id,course_status_level_id=17,is_edit=1,
                                                 course_header_id = course.course_header_id,to_user_group_id=8,user_group_id=7)
                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                 course_status_level_id__in=[10,16]).update(is_edit=0)
                # email = User.objects.filter(id=bosc_user[0]['course__program__user']).values('email', 'id', 'first_name')
                # course = Course.objects.get(id=c_id)
                # sender = settings.EMAIL_HOST_USER
                # current_site = get_current_site(request)
                # mail_subject = "Invite to Review Program structure and syllabus"
                # message = render_to_string('pcmi/email_templates/course_structure_approve_email.html', {
                #     'email': encrypt(email[0]['email']),
                #     'domain': current_site.domain,
                #     'guest_firstname': email[0]['first_name'],
                #     'course_code': course.course_code,
                #     'course_name': course.course_name,
                # })
                # e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, "Approved.....")
            return redirect('course_preview_bos', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_bos', encrypt(c_id))
    return redirect('course_preview_bos',encrypt(c_id))


@login_required
@group_required("BOS")
def course_structure_need_more(request,c_id):
    c_id=decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id,to_user_id=request.user.id,course_status_level_id__in=[10,16]).exists():
                csmi_user = CourseUserMapping.objects.filter(course_id=c_id,to_user_id=request.user.id,course_status_level_id__in=[10,16]).values('user_id')
                CourseUserMapping.objects.create(course_id=c_id,to_user_id=csmi_user[0]['user_id'],user_id=request.user.id,course_status_level_id=18,
                                                comment= request.POST.get('bos_message'),is_edit=1,course_header_id=course.course_header_id,
                                                to_user_group_id=6,user_group_id=7
                                                )
                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                 course_status_level_id__in=[10,16]).update(is_edit=0)
                # email = User.objects.filter(id=csmi_user[0]['user_id']).values('email', 'id', 'first_name')
                # course = Course.objects.get(id=c_id)
                # sender = settings.EMAIL_HOST_USER
                # current_site = get_current_site(request)
                # mail_subject = "Invite to Review Program structure and syllabus"
                # message = render_to_string('csmi/email_templates/csmi_forward_staff_email.html', {
                #     'email': encrypt(email[0]['email']),
                #     'domain': current_site.domain,
                #     'guest_firstname': email[0]['first_name'],
                #     'course_code': course.course_code,
                #     'course_name': course.course_name,
                #
                # })
                # e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, 'Forwarded Successfully..')
            return redirect('course_preview_bos', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_bos', encrypt(c_id))
    return redirect('course_preview_bos',encrypt(c_id))