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
@group_required('DOAA','ADMIN','DOAAAD')
def index(request):
    programs = ProgramUserMapping.objects.filter(Q(to_user_id=request.user.id)).values(
        'id', 'program__name', 'program_status_level__title',
        'program__program_type__type',
        'program_id').order_by('-created')
    program = []
    program_id = []
    for i in programs:
        if not i['program_id'] in program_id:
            i['encrypt_id'] = encrypt(i['program_id'])
            program.append(i)
        program_id.append(i['program_id'])
    return render(request,'doaa/index.html',{'programs':program})


@login_required
@group_required('DOAA','ADMIN','DOAAAD')
def doaa_program_detail(request,p_id):
    p_id = decrypt(p_id)
    program = Programs.objects.filter(id=p_id).values()
    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                                   to_user_group_id=8, is_active=1). \
            values('user_id', 'is_edit', 'program_status_level_id').last()
        if program_assign_details:
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level',
                                                                                       'level_id').order_by(
                'level__level')

            courses = Course.objects.filter(program_id=p_id).values('course_name', 'course_category__category',
                                                                    'course_type__name', 'id', 'course_type_id',
                                                                    'level_of_course__level', 'L', 'T', 'P', 'J', 'S',
                                                                    'C', 'level_of_course_id', 'course_header_id')
            assign_courses = CourseUserMapping.objects.filter(course__program_id=p_id).values(
                'course_status_level__title', 'course_id', 'course_status_level_id')
            program_timeline = []
            program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created',
                                                                                                 'to_user_id',
                                                                                                 'user__first_name',
                                                                                                 'user_id',
                                                                                                 'program_status_level__title',
                                                                                                 'to_user__first_name',
                                                                                                 'user__image',
                                                                                                 'comment',
                                                                                                 'to_user_group__description',
                                                                                                 'user_group__description').order_by(
                '-id')

            pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id, is_edit=1).values('created',
                                                                                                    'to_user_id',
                                                                                                    'program_status_level__title',
                                                                                                    'to_user__first_name',
                                                                                                    'to_user__image',
                                                                                                    'comment',
                                                                                                    'to_user_group__description',
                                                                                                    'user_group__description').last()

            campus_detail = CourseCampusMapping.objects.filter(course__program_id=p_id).values('campus__name',
                                                                                               'course_id')
            depart_detail = CourseDepartmentMapping.objects.filter(course__program_id=p_id).values('department',
                                                                                                   'course_id')
            inst_detail = CourseInstituteMapping.objects.filter(course__program_id=p_id).values('institute',
                                                                                                'course_id')

            program_timeline.append(pending_timeline)
            program_timeline.extend(program_timeline_actions)

            depins_course = []
            dept_course = depart_detail.values_list('course_id', flat=True)
            inst_course = inst_detail.values_list('course_id', flat=True)

            program_structures = []
            ltpjs_course = []
            for i in program_level:
                c = []
                c_ids = []
                for j in courses:
                    if not j['course_header_id'] in c_ids:
                        if j['level_of_course_id'] == i['level_id']:
                            for k in assign_courses:
                                if j['id'] == k['course_id']:
                                    j['course_status'] = k['course_status_level__title']
                            j['encrypt_id'] = encrypt(j['id'])
                            if j['course_type_id'] == 1:
                                if j['P'] != '0' or j['J'] != '0' or j['S'] != '0':
                                    ltpjs_course.append(j['course_name'])
                            elif j['course_type_id'] == 2:
                                if j['L'] != '0' or j['T'] != '0' or j['J'] != '0' or j['S'] != '0':
                                    ltpjs_course.append(j['course_name'])
                            elif j['course_type_id'] == 3:
                                if j['J'] != '0' or j['S'] != '0':
                                    ltpjs_course.append(j['course_name'])
                            elif j['course_type_id'] == 4:
                                if j['L'] != '0' or j['T'] != '0' or j['P'] != '0' or j['S'] != '0':
                                    ltpjs_course.append(j['course_name'])
                            elif j['course_type_id'] == 5:
                                if j['L'] != '0' or j['T'] != '0' or j['P'] != '0' or j['J'] != '0':
                                    ltpjs_course.append(j['course_name'])
                            if not j['id'] in dept_course:
                                depins_course.append(j['course_name'])
                            if not j['id'] in inst_course:
                                depins_course.append(j['course_name'])

                            c.append(j)
                    c_ids.append(j['course_header_id'])
                i['course_structures'] = c
                if len(c) > 0:
                    program_structures.append(i)
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1).exists():
                program_user_mapping = ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                                         is_edit=1).values().last()
            else:
                program_user_mapping = None
            dept_inst_course = list(set(depins_course))
            level_mapped = ProgramLevelMapping.objects.filter(program_id=p_id).values('level',
                                                                                      'level__level').distinct()
            count_courses = set([i['course_id'] for i in assign_courses if i['course_status_level_id'] == 1])
            complete_courses = set([i['course_id'] for i in assign_courses if i['course_status_level_id'] == 5])
            lv = set(
                [j['level__level'] for i in courses for j in level_mapped if j['level'] != i['level_of_course_id']])
            context = {'levels': program_level, 'p_id': p_id, 'program_structures': program_structures,
                       'program_assign_details': program_assign_details, 'program_timeline': program_timeline,
                       'program_id': encrypt(p_id), 'program_user_mapping': program_user_mapping,
                       'level_mapped': len(level_mapped), 'program_st': len(program_structures), 'level': lv,
                       'count_courses': len(courses), 'complete_courses': len(complete_courses),
                       'campus_detail': campus_detail, 'depart_detail': depart_detail, 'inst_detail': inst_detail,
                       'ltpjs_course': ltpjs_course, 'dept_inst_course': dept_inst_course, 'program': program.last()}
            return render(request, 'doaa/program_detail.html', context)
        else:
            return redirect('/')
    else:
        return redirect('/')
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
@login_required
@group_required('DOAA','ADMIN','DOAAAD')
def program_course_preview(request, p_id,c_id):
    course_id = decrypt(c_id)
    program_id = decrypt(p_id)
    program = Programs.objects.get(id=program_id)

    course_details = Course.objects.get(id=course_id)
    course_syllabus = get_syllabus(request, course_id, )
    course_book_details = get_course_book_details(request, course_id)
    references_details = get_ref_details(request, course_id)
    journal_details = get_journal_details(request, course_id)
    website_details = get_website_details(request, course_id)
    course_outcomes = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    pedagogy_tools = PedagogyTools.objects.values('id', 'name')
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values('topic',
                                                                                            'syllabus_type__name')
    course_owner = CourseUserMapping.objects.filter(is_active=1, to_user_group_id=2, course_id=course_id).values(
                                                'to_user__first_name', 'to_user__username', 'to_user__dept_code_id', 'to_user__designation',
                                                'to_user__dept_code__dept_inst').last()
    course_pre_requisite = CoursePrerequestiesMapping.objects.filter(course_id=course_id).values('id',
                                                                                                 'prerequesti__course_name')

    program_course_outcome = ProgramCourseOutcome.objects.filter(course_id=course_id, program_id=program_id).values('id', 'po')
    program_specific_outcome = ProgramSpecificOutcome.objects.filter(course_id=course_id, program_id=program_id).values('id', 'pso')
    co_po_map = ProgramCourseCOPOMapping.objects.filter(course_id=course_id, program_id=program_id,
                                                        ).values()
    co_pso_map = ProgramCourseCOPSOMapping.objects.filter(course_id=course_id, program_id=program_id,
                                                          ).values()

    po_co_average = []
    for i in program_course_outcome:
        s = 0
        for j in co_po_map:
            if i['id'] == j['po_id']:
                s = s + j['po_points']
        po_co_average.append(int(s / len(program_course_outcome)))

    pso_co_average = []
    for i in program_specific_outcome:
        s = 0
        for j in co_pso_map:
            if i['id'] == j['pso_id']:
                s = s + j['pso_points']
        pso_co_average.append(int(s / len(program_course_outcome)))

    context = {'course_id': encrypt(course_details.id), 'po_co_average': po_co_average,
               'pso_co_average': pso_co_average, 'c_id': course_id, 'p_id': p_id,
               'course_details': course_details, 'active_step': course_details.active_step,
               'practical_syllabus': practical_syllabus,
               'course_syllabus': course_syllabus, 'program': program,
               'course_book_details': course_book_details, 'references_details': references_details,
               'course_outcomes': course_outcomes, 'pedagogy_tools': pedagogy_tools, 'course_owner': course_owner,
               'course_pre_requisite': course_pre_requisite,
               'journal_details': journal_details, 'website_details': website_details,
               'program_specific_outcome': program_specific_outcome,
               'program_course_outcome': program_course_outcome, 'co_po_map': co_po_map, 'co_pso_map': co_pso_map}
    return render(request, 'doaa/program_course_preview.html', context)


@login_required
@group_required('DOAA','ADMIN','DOAAAD')
def course_preview_doaa(request,course_id):
    course_id = decrypt(course_id)
    dept = DepartmentInstituteCodes.objects.values('id', 'dept_inst')
    course_type = CourseType.objects.values('id', 'name')
    level_of_course = LevelOfCourse.objects.values('id', 'level')
    course_category = CourseCategory.objects.values('id', 'category')
    course_details = Course.objects.get(id=course_id)
    course_syllabus = get_syllabus(request, course_id,)
    course_book_details = get_course_book_details(request, course_id)
    references_details = get_ref_details(request, course_id)
    course = Course.objects.filter(id=course_id).values()
    course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    pso = ProgramSpecificOutcome.objects.filter(course_id=course_id).values('id', 'pso')
    pedagogy_tools = PedagogyTools.objects.values('id', 'name')
    co_po_pso = CourseCoPoPso.objects.filter(course_id=course_id).values()
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
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=6,is_edit=1,to_user_id=request.user.id).exists():
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
               'pso': pso,  'co_po_pso': co_po_psos,'course_timeline':course_timeline,
               'pedagogy_tools': pedagogy_tools}
    return render(request, 'doaa/preview.html',context)

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

@login_required
@group_required('DOAA','ADMIN','DOAAAD')
def program_structure_need_more_doaa(request,p_id):
    p_id = decrypt(p_id)
    if request.method == 'POST':
        try:
            if ProgramUserMapping.objects.filter(program_id=p_id,user_id=int(request.POST.get('bos_user_id')),
                                                 program_status_level_id__in=[12],to_user_group_id=8).exists():

                ProgramUserMapping.objects.create(program_id=p_id, to_user_id=int(request.POST.get('bos_user_id')),
                                                      user_id=None, program_status_level_id=20,
                                                      is_edit=1,comment=request.POST.get('bos_message'),
                                                      to_user_group_id=7,user_group_id=8)
                ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=None,to_user_group_id=8,
                                                  program_status_level_id__in=[12]).update(is_edit=0)
                messages.success(request, "Submitted Successfully..")
                return redirect(request.POST['path'])
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect(request.POST['path'])
    return redirect('doaa_program_detail', encrypt(p_id))
@login_required
@group_required('DOAA','ADMIN','DOAAAD')
def update_course_code(request,p_id):
    p_id = decrypt(p_id)
    if request.method == 'POST':
        try:
            if Course.objects.filter(id=request.POST['course_id']).exists():

                Course.objects.filter(id=request.POST['course_id']).update(course_code=request.POST['course_id'])
                messages.success(request, "Submitted Updated..")
                return redirect(request.POST['path'])
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect(request.POST['path'])
    return redirect('curriculum_status_program_details', encrypt(p_id))

@login_required
@group_required('DOAA','ADMIN')
def doaa_approve(request,p_id):
    p_id = decrypt(p_id)
    if request.method == 'POST':
        try:
            if ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=None,program_status_level_id__in=[12],to_user_group_id=8).exists():

                ProgramUserMapping.objects.create(program_id=p_id, to_user_id=None,
                                                      user_id=None, program_status_level_id=21,
                                                      is_edit=0,comment=None,
                                                      to_user_group_id=8,user_group_id=8)
                ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=None,to_user_group_id=8,
                                                  program_status_level_id__in=[12]).update(is_edit=0)
                messages.success(request, "Approved Successfully..")
                return redirect(request.POST['path'])
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect(request.POST['path'])
    return redirect('doaa_program_detail', encrypt(p_id))

@login_required
@group_required('DOAA','ADMIN')
def forward_program_to_pre_ac_by_doaa(request,p_id):
    p_id=decrypt(p_id)
    if request.method == "POST":
        try:
            ProgramUserMapping.objects.create(created=datetime.now(),is_edit=1,program_id=p_id,program_status_level_id=17,
                                              to_user_id=request.user.id,user_id=request.user.id,to_user_group_id=8,
                                              user_group_id=8)
            ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,is_edit=1,program_status_level_id=12).update(is_edit=0)
            messages.success(request, 'Forwarded Successfully..')
            return redirect('doaa_program_detail',encrypt(p_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('doaa_program_detail' , encrypt(p_id))
    else:
        return redirect('doaa_program_detail' , encrypt(p_id))

@login_required
@group_required('DOAA','ADMIN')
def program_publish_by_doaa(request,p_id):
    p_id=decrypt(p_id)
    if request.method == "POST":
        try:
            ProgramUserMapping.objects.create(created=datetime.now(),is_edit=1,program_id=p_id,program_status_level_id=18,
                                              to_user_id=request.user.id,user_id=request.user.id,to_user_group_id=8,
                                              user_group_id=8)
            ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,is_edit=1,program_status_level_id=17).update(is_edit=0)
            messages.success(request, 'Published Successfully..')
            return redirect('doaa_program_detail',encrypt(p_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('doaa_program_detail' , encrypt(p_id))
    else:
        return redirect('doaa_program_detail' , encrypt(p_id))



@login_required
@group_required('DOAA','ADMIN')
def dept_index(request):
    user_di = User.objects.values('dept_code__dept_code').order_by('dept_code__dept_code').distinct()
    department = sorted(list(set([j['dept_code__dept_code'] for j in user_di if j['dept_code__dept_code'] != None])))
    programs=''
    if request.method == 'GET':
        try:
            dept = request.GET.get('department')
            programs = ProgramUserMapping.objects.filter(program_id__user_id__dept_code__dept_code=request.GET.get('department'),program_status_level_id=12).values('program__program_type__type','program_id',
                                                                                                                    'program_status_level__title','program__name').distinct()
            for j in programs:
                j['encrypt_id'] = encrypt(j['program_id'])
            return render(request, 'doaa/dept_index.html', {'department': department, 'programs': programs,'dept_id':dept})
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return render(request, 'doaa/dept_index.html', {'department': department, 'programs': programs})
    else:
        return render(request,'doaa/dept_index.html',{'department':department,'programs':programs})


