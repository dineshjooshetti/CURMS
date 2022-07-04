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
from django.views.generic import View
from .render import Render


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
@group_required('DOAA','ADMIN')
def doaa_program_detail(request,p_id):
    p_id = decrypt(p_id)
    program = Programs.objects.filter(id=p_id).values()
    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,
                                                                   to_user_group_id__in=[8,10], is_active=1). \
            values('user_id', 'is_edit', 'program_status_level_id').last()
        
        if program_assign_details:
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level',
                                                                                       'level_id').order_by(
                'level__level')

            course_ids=ProgramCourseMapping.objects.filter(program_id=p_id)
            courses = Course.objects.filter(id__in=course_ids.values_list('course_id')).values('course_name', 'course_category__category',
                                                                    'course_type__name', 'id', 'course_type_id',
                                                                    'level_of_course__level', 'L', 'T', 'P', 'J', 'S',
                                                                    'C','level_of_course_id', 'course_header_id',
                                                                    'course_descrption','specific_instruction_objectives',
                                                                    'course_code')
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
            course_outcome = CourseOutcome.objects.filter(course__program_id=p_id).values('course_id', 'course_outcome')
            # dept_inst_name = DepartmentInstituteCodes.objects.filter(dept_code=depart_detail[0]['department']).values('id','dept_inst')
            dept_inst_name=[]
            course_syllabus = CourseSyllabus.objects.filter(course__program_id=p_id).values('course_id','short_title','unit_name','outcome_1','level_1','outcome_2',
                                                                                                    'level_2','outcome_3','level_3',
                                                                                                    'outcome_4','level_4','outcome_5','level_5',
                                                                                                    'number_of_contact_hours')
            course_references = References.objects.filter(course__program_id=p_id).values('course_id','author','title','edition','publisher','year')
            course_books = CourseBooks.objects.filter(course__program_id=p_id).values('course_id','author','title','edition','publisher','year')
            course_websites  = Websites.objects.filter(course__program_id=p_id).values('course_id','name_website','website_url')
            course_syl_practical = CourseSyllabusPractical.objects.filter(course__program_id=p_id).values('course_id','topic')
            program_timeline.append(pending_timeline)
            program_timeline.extend(program_timeline_actions)

            depins_course = []
            dept_course = depart_detail.values_list('course_id', flat=True)
            inst_course = inst_detail.values_list('course_id', flat=True)
            # print(course_syllabus)
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
                            j['course_outcome'] = [co['course_outcome'] for co in course_outcome if j['id']==co['course_id']]
                            j['unit_title_outcome_level'] = [{'short_title':cs['short_title'],'unit_name':cs['unit_name'],'ot1':cs['outcome_1'],'l1':cs['level_1'],'ot2':cs['outcome_2'],'l2':cs['level_2'],'ot3':cs['outcome_3'],'l3':cs['level_3'],'ot4':cs['outcome_4'],'l4':cs['level_4'],'ot5':cs['outcome_5'],'l5':cs['level_5'],'chours':cs['number_of_contact_hours']} for cs in course_syllabus if j['id']==cs['course_id']]
                            j['references'] = [{'author':cr['author'],'title':cr['title'],'edition':cr['edition'],'pub':cr['publisher'],'year':cr['year']}  for cr in course_references if j['id']==cr['course_id']]
                            j['course_books'] = [{'author':cb['author'],'title':cb['title'],'edition':cb['edition'],'pub':cb['publisher'],'year':cb['year']}  for cb in course_books if j['id']==cb['course_id']]
                            j['course_websites'] = [{'cw':cw['name_website'],'wurl':cw['website_url']}  for cw in course_websites if j['id']==cw['course_id']]
                            j['course_syl_practical'] = [cp['topic'] for cp in course_syl_practical if j['id']==cp['course_id']]
                            c.append(j)        
                    c_ids.append(j['course_header_id'])
                i['course_structures'] = c
                if len(c) > 0:
                    program_structures.append(i)
            # print(program_structures)
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

            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1,
                                                 program_status_level_id=12).exists() and CourseUserMapping.objects.filter(course__program_id=p_id,user_id=request.user.id, is_edit=0,course_status_level_id=16).exists():
                is_edit = 1
            else:
                is_edit = 0

            context = {'levels': program_level, 'p_id': p_id, 'program_structures': program_structures,
                       'program_assign_details': program_assign_details, 'program_timeline': program_timeline,
                       'program_id': encrypt(p_id), 'program_user_mapping': program_user_mapping,
                       'level_mapped': len(level_mapped), 'program_st': len(program_structures), 'level': lv,
                       'count_courses': len(courses), 'complete_courses': len(complete_courses),
                       'campus_detail': campus_detail, 'depart_detail': depart_detail, 'inst_detail': inst_detail,
                       'ltpjs_course': ltpjs_course, 'dept_inst_course': dept_inst_course, 'program': program.last(),
                       'is_edit':is_edit,'programs':program,'dept_inst_name':dept_inst_name} 
            return context
    #     else:
    #         return redirect('/')
    # else:
    #     return redirect('/')
@login_required
@group_required('DOAA','ADMIN')
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
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=8,is_edit=1,to_user_id=request.user.id,course_status_level_id=17).exists():
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


class Pdf(View):
    def get(self, request,p_id):
        program_details = doaa_program_detail(request,p_id)
        print(program_details)
        program_name = program_details['program'].name
        #reg_id=finalpreview['user_reg_attr'].reg_id

        # return Render.render('doaa/cover_page.html', program_details)
        context = {}
        pdf= Render.render('doaa/cover_page.html',program_details)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = program_name+'.pdf'
            content = "attachment; filename="+filename
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")