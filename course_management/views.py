from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from .models import *
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
def create_course(request):
    users=User.objects.filter(Q(is_active=1),~Q(id=request.user.id)).exclude(groups__name__in=["GUEST",'Admin','HOD','HOI']).values()
    user_details = User.objects.get(id=request.user.id)
    dept = DepartmentInstituteCodes.objects.values('id','dept_inst')
    course_type = CourseType.objects.values('id','name')
    level_of_course = LevelOfCourse.objects.values('id','level')
    course_category = CourseCategory.objects.values('id','category')
    context = {'users':users,'months':range(1,13),'dept':dept,'user_details':user_details,'course_type':course_type,'level_of_course':level_of_course,
               'course_category':course_category}
    return render(request,'forms/form_base.html',context)


@csrf_exempt
@login_required
@group_required('STAFF')
def dev_details_save(request):
    if request.method == "POST":
        try:
            User.objects.filter(id=request.user.id).update(dept_code_id=request.POST['dept_inst'])
            response = {'status': 200, 'project': 'project'}
            return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

@csrf_exempt
@login_required
@group_required('STAFF')
def course_details_save(request):
    if request.method == "POST":
        try:
            if not request.POST['id'] == '':
                if Course.objects.filter(id=request.POST['id']).exists():
                    Course.objects.filter(id=request.POST['id']).update(course_type_id= request.POST['type_of_course'],level_of_course_id = request.POST['level_of_course'],
                                                                        course_category_id = request.POST['course_category'],
                                                                        created = datetime.now(),created_by_id = request.user.id,active_step=3)
                    insert = Course.objects.get(id=request.POST['id'])
                    response = {'status': 200, 'enc_id': encrypt(insert.id)}
                    return JsonResponse(response)
            else:
                insert = Course.objects.create(course_name=None, course_type_id=request.POST['type_of_course'],
                                               level_of_course_id=request.POST['level_of_course'],
                                               course_category_id=request.POST['course_category'],
                                               created=datetime.now(), created_by_id=request.user.id, active_step=3)
                response = {'status': 200, 'enc_id': encrypt(insert.id)}
                return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

@login_required
@group_required('STAFF')
def course_details(request,course_id):
    course_id = decrypt(course_id)
    pre_requisites = []
    co_requisites = []
    users = User.objects.filter(Q(is_active=1), ~Q(id=request.user.id)).exclude(groups__name__in=["GUEST", 'Admin', 'HOD', 'HOI']).values()
    user_details = User.objects.get(id=request.user.id)
    dept = DepartmentInstituteCodes.objects.values('id', 'dept_inst')
    course_type = CourseType.objects.values('id', 'name')
    level_of_course = LevelOfCourse.objects.values('id', 'level')
    course_category = CourseCategory.objects.values('id', 'category')
    course_details = Course.objects.get(id=course_id)
    course_syllabus = get_syllabus(request,course_id)
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values()
    syllabus_type = SyllabusType.objects.values('id','name')
    course_book_details = get_course_book_details(request,course_id)
    references_details = get_ref_details(request,course_id)
    course = Course.objects.filter(id=course_id, created_by_id=request.user.id).values()
    course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id','course_outcome')
    pso = ProgramSpecificOutcome.objects.filter(course_id=course_id).values('id','pso')
    pedagogy_tools = PedagogyTools.objects.values('id','name')
    co_po_pso = CourseCoPoPso.objects.filter(course_id=course_id).values()
    for c in course:
        if c['co_requisite1'] != None:
            co_requisites.append(c['co_requisite1'])
        if c['co_requisite2'] != None:
            co_requisites.append(c['co_requisite2'])
        if c['co_requisite3'] != None:
            co_requisites.append(c['co_requisite3'])
        if c['co_requisite4'] != None:
            pre_requisites.append(c['co_requisite4'])
        if c['co_requisite5'] != None:
            co_requisites.append(c['co_requisite5'])
        if c['pre_requisites_yes1'] != None:
            pre_requisites.append(c['pre_requisites_yes1'])
        if c['pre_requisites_yes2'] != None:
            pre_requisites.append(c['pre_requisites_yes2'])
        if c['pre_requisites_yes3'] != None:
            pre_requisites.append(c['pre_requisites_yes3'])
        if c['pre_requisites_yes4'] != None:
            pre_requisites.append(c['pre_requisites_yes4'])
        if c['pre_requisites_yes5'] != None:
            pre_requisites.append(c['pre_requisites_yes5'])
    context = {'users':users,'course_id':encrypt(course_details.id),'dept': dept, 'user_details': user_details,'course_type': course_type, 'level_of_course': level_of_course,'course_category': course_category,
               'course_details': course_details,'active_step':course_details.active_step,'course_syllabus':course_syllabus,
               'course_book_details':course_book_details,'references_details':references_details,'course':course,'course_outcome':course_outcome,
               'pso':pso,'co_po_pso':co_po_pso,'pedagogy_tools':pedagogy_tools,'pre_requisites':pre_requisites,'co_requisites':co_requisites,
               'syllabus_type':syllabus_type,'practical_syllabus':practical_syllabus}
    return render(request, 'forms/form_base.html',context)

@group_required('STAFF')
def about_course_save(request):
    if request.method == "POST":
        print(request.POST)
        course_id = request.POST['course_id']
        course_type_id = request.POST['course_type_id']
        try:
            co_requisites = request.POST.getlist('co_requisites')
            try:
                co_requisite1 = co_requisites[0]
            except:
                co_requisite1 = None
            try:
                co_requisite2 = co_requisites[1]
            except:
                co_requisite2 = None
            try:
                co_requisite3 = co_requisites[2]
            except:
                co_requisite3 = None
            try:
                co_requisite4 = co_requisites[3]
            except:
                co_requisite4 = None
            try:
                co_requisite5 = co_requisites[4]
            except:
                co_requisite5 = None
            pre_requisites_yes1= ''
            pre_requisites_yes2 = ''
            pre_requisites_yes3 = ''
            pre_requisites_yes4 = ''
            pre_requisites_yes5 = ''
            if not request.POST.getlist('pre_requisites_yes') == ['']:
                pre_requisites_yes =  request.POST.getlist('pre_requisites_yes')
                try:
                    pre_requisites_yes1 = pre_requisites_yes[0]
                except:
                    pre_requisites_yes1 = None
                try:
                    pre_requisites_yes2 = pre_requisites_yes[1]
                except:
                    pre_requisites_yes2 = None
                try:
                    pre_requisites_yes3 = pre_requisites_yes[2]
                except:
                    pre_requisites_yes3 = None
                try:
                    pre_requisites_yes4 = pre_requisites_yes[3]
                except:
                    pre_requisites_yes4 = None
                try:
                    pre_requisites_yes5 = pre_requisites_yes[4]
                except:
                    pre_requisites_yes5 = None
            if Course.objects.filter(id=course_id).exists():
                Course.objects.filter(id=course_id).update(course_name=request.POST['course_title'],L=request.POST['L'],T=request.POST['T'],P=request.POST['P'],S=request.POST['S'],
                                        J=request.POST['J'],C=request.POST['C'],total_no_of_contact_hours=request.POST['total_hours'],
                                        alternative_exposure=request.POST['alt_exposure'],course_descrption=request.POST['course_description'],
                                        specific_instruction_objectives=request.POST['self_objectives'],pre_requisites=request.POST['pre_requisites'],
                                        co_requisite1 = co_requisite1,co_requisite2=co_requisite2,co_requisite3=co_requisite3,
                                        co_requisite4 = co_requisite4,co_requisite5=co_requisite5,
                                        pre_requisites_yes1 = pre_requisites_yes1,pre_requisites_yes2=pre_requisites_yes2,pre_requisites_yes3=pre_requisites_yes3,
                                        pre_requisites_yes4 = pre_requisites_yes4,pre_requisites_yes5 = pre_requisites_yes5,
                                        created=datetime.now(),created_by_id=request.user.id)
                if CourseOutcome.objects.filter(course_id=course_id,user_id=request.user.id).exists():
                    for i in range(len(request.POST.getlist('course_outcome_id'))):
                        CourseOutcome.objects.filter(id=request.POST.getlist('course_outcome_id')[i],course_id=course_id,
                                                     user_id=request.user.id).update(course_id=course_id,
                                                     course_outcome=request.POST.getlist('course_outcome')[i],
                                                     created=datetime.now(),user_id=request.user.id)
                else:
                    for i in range(len(request.POST.getlist('course_outcome'))):
                        CourseOutcome.objects.create(course_id=course_id,course_outcome=request.POST.getlist('course_outcome')[i],
                                                     created=datetime.now(),user_id=request.user.id)
                if ProgramSpecificOutcome.objects.filter(course_id=course_id, user_id=request.user.id).exists():
                    for i in range(len(request.POST.getlist('pso_id'))):
                        ProgramSpecificOutcome.objects.filter(id=request.POST.getlist('pso_id')[i],course_id=course_id,
                                                              user_id=request.user.id).update(course_id=course_id,
                                                              pso=request.POST.getlist('pso')[i],
                                                              created=datetime.now(),user_id=request.user.id)
                else:
                    for i in range(len(request.POST.getlist('pso'))):
                        ProgramSpecificOutcome.objects.create(course_id=course_id,pso=request.POST.getlist('pso')[i],
                                                              created=datetime.now(),user_id=request.user.id)

            Course.objects.filter(id=course_id).update(active_step=4)
            response = {'status': 200, 'enc_id': encrypt(course_id)}
            return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

@csrf_exempt
@login_required
@group_required('STAFF')
def syllabus_save(request):
    if request.method == "POST":
        course_id = request.POST['cour_id']
        course = Course.objects.get(id=course_id)
        try:
            unit_name = request.POST.getlist('unit_name')
            short_title = request.POST.getlist('short_title')
            number_of_contact_hours = request.POST.getlist('contact_hours')
            outcome_1 = request.POST.getlist('learning_outcome_1')
            level_1 = request.POST.getlist('level_1')
            outcome_2 = request.POST.getlist('learning_outcome_2')
            level_2 = request.POST.getlist('level_2')
            outcome_3 = request.POST.getlist('learning_outcome_3')
            level_3 = request.POST.getlist('level_3')
            pedagogy_tools1 = request.POST.getlist('pedagogy_tool_1')
            pedagogy_tools2 = request.POST.getlist('pedagogy_tool_2')

            if course.course_type_id == 1 or course.course_type_id == 5:
                c_t = Course.objects.filter(id=course_id).values()
                dat = [int(i) for i in request.POST.getlist('contact_hours')]
                if sum(dat) > int(c_t[0]['total_no_of_contact_hours']):
                    response = {'status': 500, 'error': 'total contact hours should be equal to'+ ' ' + c_t[0]['total_no_of_contact_hours'], 'project': 'project'}
                    return JsonResponse(response)
                elif sum(dat) < int(c_t[0]['total_no_of_contact_hours']):
                    response = {'status': 500, 'error': 'total contact hours should be equal to' + ' ' + c_t[0]['total_no_of_contact_hours'], 'project': 'project'}
                    return JsonResponse(response)
                insert = None
                for i in request.POST.getlist('unit_no'):
                    if CourseUnits.objects.filter(unit_no=i,course_id=course_id).exists():
                        CourseUnits.objects.filter(unit_no=i,course_id=course_id).update(course_id=course_id,unit_no=i)
                        insert = CourseUnits.objects.get(unit_no=i,course_id=course_id)
                    else:
                        insert = CourseUnits.objects.create(course_id=course_id,unit_no=i)

                if CourseSyllabus.objects.filter(course_id=course_id,course_unit_id=insert.id).exists():
                    for i in range(len(unit_name)):
                        outcome_4 = None
                        if request.POST.getlist('learning_outcome_4'):
                            outcome_4 = request.POST.getlist('learning_outcome_4')[i]
                        level_4 = None
                        if request.POST.getlist('level_4'):
                            level_4 = request.POST.getlist('level_4')['']
                        outcome_5 = None
                        if request.POST.getlist('learning_outcome_5'):
                            outcome_5 = request.POST.getlist('learning_outcome_5')[i]
                        level_5 = None
                        if request.POST.getlist('level_5'):
                            level_5 = request.POST.getlist('level_5')[i]
                        CourseSyllabus.objects.filter(course_id=course_id,course_unit_id=insert.id).update(course_id=course_id, course_unit_id=insert.id, unit_name=unit_name[i],
                                                      short_title=short_title[i],
                                                      number_of_contact_hours=number_of_contact_hours[i],
                                                      version=1, outcome_1=outcome_1[i], level_1=level_1[i],
                                                      outcome_2=outcome_2[i], level_2=level_2[i],
                                                      outcome_3=outcome_3[i], level_3=level_3[i],
                                                      outcome_4=outcome_4,level_4=level_4,
                                                      outcome_5=outcome_5,level_5=level_5,
                                                      pedagogy_tool_1_id=pedagogy_tools1[i],pedagogy_tool_2_id=pedagogy_tools2[i],
                                                      created=datetime.now(),created_by_id=request.user.id)
                else:
                    for i in range(len(unit_name)):
                        outcome_4 = None
                        if request.POST.getlist('learning_outcome_4'):
                            outcome_4 = request.POST.getlist('learning_outcome_4')[i]
                        level_4 = None
                        if request.POST.getlist('level_4'):
                            level_4 = request.POST.getlist('level_4')['']
                        outcome_5 = None
                        if request.POST.getlist('learning_outcome_5'):
                            outcome_5 = request.POST.getlist('learning_outcome_5')[i]
                        level_5 = None
                        if request.POST.getlist('level_5'):
                            level_5 = request.POST.getlist('level_5')[i]
                        CourseSyllabus.objects.create(course_id=course_id,course_unit_id=insert.id,unit_name=unit_name[i],
                                                      short_title=short_title[i],
                                                      number_of_contact_hours = number_of_contact_hours[i],
                                                      version=1,outcome_1=outcome_1[i],level_1 = level_1[i],
                                                      outcome_2 = outcome_2[i],level_2=level_2[i],
                                                      outcome_3=outcome_3[i],level_3=level_3[i],
                                                      outcome_4=outcome_4,level_4=level_4,
                                                      outcome_5=outcome_5,level_5=level_5,
                                                      pedagogy_tool_1_id=pedagogy_tools1[i],pedagogy_tool_2_id=pedagogy_tools2[i],
                                                      created=datetime.now(),created_by_id=request.user.id)
            elif course.course_type_id == 2:
                if CourseSyllabusPractical.objects.filter(course_id=course_id).exists():
                    for i in range(len(request.POST.getlist('practical_id'))):
                        CourseSyllabusPractical.objects.filter(course_id=course_id,id=request.POST.getlist('practical_id')[i]).update(
                            course_id=course_id, syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                            topic=request.POST.getlist('syllabus_topic')[i])
                else:
                    for i in range(len(request.POST.getlist('syllabus_topic'))):
                        CourseSyllabusPractical.objects.create(course_id=course_id,syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                                                               topic=request.POST.getlist('syllabus_topic')[i],created=datetime.now(),
                                                               user_id=request.user.id,version=1)

            elif course.course_type_id == 3:
                c_t = Course.objects.filter(id=course_id).values()
                total_hours = (int(c_t[0]['L']) + int(c_t[0]['T'])) * (15)
                dat = [int(i) for i in request.POST.getlist('contact_hours')]
                if sum(dat) > int(total_hours):
                    response = {'status': 500, 'error': 'total contact hours should be equal to' + ' ' + str(total_hours), 'project': 'project'}
                    return JsonResponse(response)
                elif sum(dat) < int(total_hours):
                    response = {'status': 500, 'error': 'total contact hours should be equal to' + ' ' + str(total_hours), 'project': 'project'}
                    return JsonResponse(response)
                insert = None
                for i in request.POST.getlist('unit_no'):
                    if CourseUnits.objects.filter(unit_no=i, course_id=course_id).exists():
                        CourseUnits.objects.filter(unit_no=i, course_id=course_id).update(course_id=course_id,
                                                                                          unit_no=i)
                        insert = CourseUnits.objects.get(unit_no=i, course_id=course_id)
                    else:
                        insert = CourseUnits.objects.create(course_id=course_id, unit_no=i)

                if CourseSyllabus.objects.filter(course_id=course_id, course_unit_id=insert.id).exists():
                    for i in range(len(unit_name)):
                        outcome_4 = None
                        if request.POST.getlist('learning_outcome_4'):
                            outcome_4 = request.POST.getlist('learning_outcome_4')[i]
                        level_4 = None
                        if request.POST.getlist('level_4'):
                            level_4 = request.POST.getlist('level_4')['']
                        outcome_5 = None
                        if request.POST.getlist('learning_outcome_5'):
                            outcome_5 = request.POST.getlist('learning_outcome_5')[i]
                        level_5 = None
                        if request.POST.getlist('level_5'):
                            level_5 = request.POST.getlist('level_5')[i]
                        CourseSyllabus.objects.filter(course_id=course_id, course_unit_id=insert.id).update(
                            course_id=course_id, course_unit_id=insert.id, unit_name=unit_name[i],
                            short_title=short_title[i],
                            number_of_contact_hours=number_of_contact_hours[i],
                            version=1, outcome_1=outcome_1[i], level_1=level_1[i],
                            outcome_2=outcome_2[i], level_2=level_2[i],
                            outcome_3=outcome_3[i], level_3=level_3[i],
                            outcome_4=outcome_4, level_4=level_4,
                            outcome_5=outcome_5, level_5=level_5,
                            pedagogy_tool_1_id=pedagogy_tools1[i], pedagogy_tool_2_id=pedagogy_tools2[i],
                            created=datetime.now(), created_by_id=request.user.id)
                else:
                    for i in range(len(unit_name)):
                        outcome_4 = None
                        if request.POST.getlist('learning_outcome_4'):
                            outcome_4 = request.POST.getlist('learning_outcome_4')[i]
                        level_4 = None
                        if request.POST.getlist('level_4'):
                            level_4 = request.POST.getlist('level_4')['']
                        outcome_5 = None
                        if request.POST.getlist('learning_outcome_5'):
                            outcome_5 = request.POST.getlist('learning_outcome_5')[i]
                        level_5 = None
                        if request.POST.getlist('level_5'):
                            level_5 = request.POST.getlist('level_5')[i]
                        CourseSyllabus.objects.create(course_id=course_id, course_unit_id=insert.id,
                                                      unit_name=unit_name[i],
                                                      short_title=short_title[i],
                                                      number_of_contact_hours=number_of_contact_hours[i],
                                                      version=1, outcome_1=outcome_1[i], level_1=level_1[i],
                                                      outcome_2=outcome_2[i], level_2=level_2[i],
                                                      outcome_3=outcome_3[i], level_3=level_3[i],
                                                      outcome_4=outcome_4, level_4=level_4,
                                                      outcome_5=outcome_5, level_5=level_5,
                                                      pedagogy_tool_1_id=pedagogy_tools1[i],
                                                      pedagogy_tool_2_id=pedagogy_tools2[i],
                                                      created=datetime.now(), created_by_id=request.user.id)
                if CourseSyllabusPractical.objects.filter(course_id=course_id).exists():
                    for i in range(len(request.POST.getlist('practical_id'))):
                        CourseSyllabusPractical.objects.filter(course_id=course_id,id=request.POST.getlist('practical_id')[i]).update(
                            course_id=course_id, syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                            topic=request.POST.getlist('syllabus_topic')[i])
                else:
                    for i in range(len(request.POST.getlist('syllabus_topic'))):
                        CourseSyllabusPractical.objects.create(course_id=course_id,syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                                                               topic=request.POST.getlist('syllabus_topic')[i],created=datetime.now(),
                                                               user_id=request.user.id,version=1)
            elif course.course_type_id == 4:
                project_topic_l = []
                for i in range(len(request.POST.getlist('project_topic'))):
                    project_topic = {}
                    project_topic['project_topic'] = request.POST.getlist('project_topic')[i]
                    project_topic_l.append(project_topic)
                Course.objects.filter(id=course_id).update(project_topic=project_topic_l)
            else:
                pass
            Course.objects.filter(id=course_id).update(active_step=5)
            response = {'status': 200, 'enc_id': encrypt(course_id)}
            return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

@csrf_exempt
@login_required
@group_required('STAFF')
def course_book_save(request):
    if request.method == "POST":
        course = Course.objects.get(id=request.POST['cours_id'])
        try:
            book_author = request.POST.getlist('book_author')
            book_author1 = request.POST.getlist('book_author')
            book_year = request.POST.getlist('book_year')
            book_title = request.POST.getlist('book_title')
            book_edition = request.POST.getlist('book_edition')
            book_publisher = request.POST.getlist('book_publisher')
            book_publication = request.POST.getlist('book_publication')
            book_id = request.POST.getlist('book_id')
            ref_author = request.POST.getlist('ref_author')
            ref_author1 = [i for i in ref_author if i!='']
            ref_year = request.POST.getlist('ref_year')
            ref_title = request.POST.getlist('ref_title')
            ref_edition = request.POST.getlist('ref_edition')
            ref_publisher = request.POST.getlist('ref_publisher')
            ref_publication = request.POST.getlist('ref_publication')
            ref_id = request.POST.getlist('ref_id')
            if course.course_type_id == 1 or course.course_type_id == 5:
                if CourseBooks.objects.filter(created_by_id=request.user.id,course_id = request.POST['cours_id']).exists():
                    for i in range(len(book_id)):
                        CourseBooks.objects.filter(course_id=request.POST['cours_id'],id=book_id[i],created_by_id=request.user.id).update(title=book_title[i],author=book_author[i],
                                                                                                                   edition=book_edition[i],place_of_publication=book_publication[i],
                                                                                                                   publisher=book_publisher[i],year=book_year[i]
                                                                                                                   )

                else:
                    for i in range(len(book_author1)):
                        CourseBooks.objects.create( created=datetime.now,title=book_title[i],author=book_author[i],
                                                    edition=book_edition[i],place_of_publication=book_publication[i],
                                                    publisher=book_publisher[i],year=book_year[i],
                                                        course_id = request.POST['cours_id'] , created_by_id=request.user.id)
                if References.objects.filter(created_by_id=request.user.id,course_id = request.POST['cours_id']).exists():
                    for i in range(len(ref_id)):
                        References.objects.filter(course_id=request.POST['cours_id'], id=ref_id[i], created_by_id=request.user.id).update(
                            title=ref_title[i], author=ref_author[i],edition=ref_edition[i], place_of_publication=ref_publication[i],
                            publisher=ref_publisher[i], year=ref_year[i])

                else:
                    for i in range(len(ref_author1)):
                        References.objects.create(created=datetime.now, title=ref_title[i], author=ref_author[i],
                                                       edition=ref_edition[i], place_of_publication=ref_publication[i],
                                                       publisher=ref_publisher[i], year=ref_year[i],
                                                       course_id=request.POST['cours_id'], created_by_id=request.user.id)
            elif course.course_type_id == 2:
                practical_referance_l = []
                pratical_topic_mapping_l = []
                for i in range(len(request.POST.getlist('practical_referance'))):
                    practical_referance = {}
                    practical_referance['referacne'] = request.POST.getlist('practical_referance')[i]
                    practical_referance_l.append(practical_referance)
                for j in range(len(request.POST.getlist('prctical_topic_mapping'))):
                    pratical_topic_mapping = {}
                    pratical_topic_mapping['topic_mapping'] = request.POST.getlist('prctical_topic_mapping')[j]
                    pratical_topic_mapping_l.append(pratical_topic_mapping)
                Course.objects.filter(id=request.POST['cours_id']).update(practical_referance=practical_referance_l,
                                                                          practical_topic_mapping=pratical_topic_mapping_l)
            elif course.course_type_id == 3:
                if CourseBooks.objects.filter(created_by_id=request.user.id,course_id = request.POST['cours_id']).exists():
                    for i in range(len(book_id)):
                        CourseBooks.objects.filter(course_id=request.POST['cours_id'],id=book_id[i],created_by_id=request.user.id).update(title=book_title[i],author=book_author[i],
                                                                                                                   edition=book_edition[i],place_of_publication=book_publication[i],
                                                                                                                   publisher=book_publisher[i],year=book_year[i]
                                                                                                                   )

                else:
                    for i in range(len(book_author1)):
                        CourseBooks.objects.create( created=datetime.now,title=book_title[i],author=book_author[i],
                                                    edition=book_edition[i],place_of_publication=book_publication[i],
                                                    publisher=book_publisher[i],year=book_year[i],
                                                        course_id = request.POST['cours_id'] , created_by_id=request.user.id)
                if References.objects.filter(created_by_id=request.user.id,course_id = request.POST['cours_id']).exists():
                    for i in range(len(ref_id)):
                        References.objects.filter(course_id=request.POST['cours_id'], id=ref_id[i], created_by_id=request.user.id).update(
                            title=ref_title[i], author=ref_author[i],edition=ref_edition[i], place_of_publication=ref_publication[i],
                            publisher=ref_publisher[i], year=ref_year[i])

                else:
                    for i in range(len(ref_author1)):
                        References.objects.create(created=datetime.now, title=ref_title[i], author=ref_author[i],
                                                       edition=ref_edition[i], place_of_publication=ref_publication[i],
                                                       publisher=ref_publisher[i], year=ref_year[i],
                                                       course_id=request.POST['cours_id'], created_by_id=request.user.id)
                practical_referance_l = []
                pratical_topic_mapping_l = []
                for i in range(len(request.POST.getlist('practical_referance'))):
                    practical_referance = {}
                    practical_referance['referacne'] = request.POST.getlist('practical_referance')[i]
                    practical_referance_l.append(practical_referance)
                for j in range(len(request.POST.getlist('prctical_topic_mapping'))):
                    pratical_topic_mapping = {}
                    pratical_topic_mapping['topic_mapping'] = request.POST.getlist('prctical_topic_mapping')[j]
                    pratical_topic_mapping_l.append(pratical_topic_mapping)
                Course.objects.filter(id=request.POST['cours_id']).update(practical_referance=practical_referance_l,
                                                                          practical_topic_mapping=pratical_topic_mapping_l)
            elif course.course_type_id == 4:
                if References.objects.filter(created_by_id=request.user.id,course_id = request.POST['cours_id']).exists():
                    for i in range(len(ref_id)):
                        References.objects.filter(course_id=request.POST['cours_id'], id=ref_id[i], created_by_id=request.user.id).update(
                            title=ref_title[i], author=ref_author[i],edition=ref_edition[i], place_of_publication=ref_publication[i],
                            publisher=ref_publisher[i], year=ref_year[i])

                else:
                    for i in range(len(ref_author1)):
                        References.objects.create(created=datetime.now, title=ref_title[i], author=ref_author[i],
                                                       edition=ref_edition[i], place_of_publication=ref_publication[i],
                                                       publisher=ref_publisher[i], year=ref_year[i],
                                                       course_id=request.POST['cours_id'], created_by_id=request.user.id)

                online_resources_l = []
                for i in range(len(request.POST.getlist('online_resources'))):
                    online_resources = {}
                    online_resources['online_resouces'] = request.POST.getlist('online_resources')[i]
                    online_resources_l.append(online_resources)
                Course.objects.filter(id=request.POST['cours_id']).update(online_resources=online_resources_l)
            else:
                pass
            Course.objects.filter(id=request.POST['cours_id']).update(active_step=6)
            response = {'status': 200, 'project': 'project'}
            return JsonResponse(response,safe=False)
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(e,safe=False)

@csrf_exempt
@login_required
@group_required('STAFF')
def co_po_pso_save(request,course_id):
    course_id = decrypt(course_id)
    if request.method == "POST":
        print(request.POST)
        try:
            if CourseCoPoPso.objects.filter(course_id=course_id,user_id=request.user.id).exists():
                for c in range(len(request.POST.getlist('co'))):
                    pso4 = None
                    if request.POST.getlist('pso4'):
                        pso4 = request.POST.getlist('pso4')[c]
                    CourseCoPoPso.objects.filter(id=request.POST.getlist('co_po_pso_id')[c],course_id=course_id, user_id=request.user.id).update(co=request.POST.getlist('co')[c],
                                             po1=request.POST.getlist('po1')[c] or None,po2=request.POST.getlist('po2')[c] or None,
                                             po3=request.POST.getlist('po3')[c] or None,po4=request.POST.getlist('po4')[c] or None,po5=request.POST.getlist('po5')[c] or None,
                                             po6=request.POST.getlist('po6')[c] or None,po7=request.POST.getlist('po7')[c] or None,po8=request.POST.getlist('po8')[c] or None,
                                             po9=request.POST.getlist('po9')[c] or None,po10=request.POST.getlist('po10')[c] or None,po11=request.POST.getlist('po11')[c] or None,
                                             po12=request.POST.getlist('po12')[c] or None,
                                             pso1=request.POST.getlist('pso1')[c] or None,pso2=request.POST.getlist('pso2')[c] or None,
                                             pso3=request.POST.getlist('pso3')[c] or None,pso4=pso4,
                                             course_id=course_id)

            else:
                for c in range(len(request.POST.getlist('co'))):
                    pso4 = None
                    if request.POST.getlist('pso4'):
                        pso4 = request.POST.getlist('pso4')[c]
                    CourseCoPoPso.objects.create(co=request.POST.getlist('co')[c],
                                                 po1=request.POST.getlist('po1')[c] or None,po2=request.POST.getlist('po2')[c] or None,
                                                 po3=request.POST.getlist('po3')[c] or None,po4=request.POST.getlist('po4')[c] or None,po5=request.POST.getlist('po5')[c] or None,
                                                 po6=request.POST.getlist('po6')[c] or None,po7=request.POST.getlist('po7')[c] or None,po8=request.POST.getlist('po8')[c] or None,
                                                 po9=request.POST.getlist('po9')[c] or None,po10=request.POST.getlist('po10')[c] or None,po11=request.POST.getlist('po11')[c] or None,
                                                 po12=request.POST.getlist('po12')[c] or None,
                                                 pso1=request.POST.getlist('pso1')[c] or None,pso2=request.POST.getlist('pso2')[c] or None,
                                                 pso3=request.POST.getlist('pso3')[c] or None,pso4=pso4,
                                                 course_id=course_id,
                                                 created=datetime.now(),user_id=request.user.id)
            messages.success(request, 'Submitted Sucessfully...')
            return redirect('/course/course_preview/'+encrypt(course_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            print(str(e))
            return redirect('/course/course_details/'+encrypt(course_id))

@login_required
@group_required('STAFF')
def course_preview(request,course_id):
    course_id = decrypt(course_id)
    users = User.objects.filter(Q(is_active=1), ~Q(id=request.user.id)).exclude(groups__name__in=["GUEST", 'Admin', 'HOD', 'HOI']).values()
    user_details = User.objects.get(id=request.user.id)
    dept = DepartmentInstituteCodes.objects.values('id', 'dept_inst')
    course_type = CourseType.objects.values('id', 'name')
    level_of_course = LevelOfCourse.objects.values('id', 'level')
    course_category = CourseCategory.objects.values('id', 'category')
    course_details = Course.objects.get(id=course_id)
    # course_theory = CourseTheory.objects.filter(course_id=course_id, created_by_id=request.user.id).values()
    course_syllabus = get_syllabus(request, course_id)
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values()
    course_book_details = get_course_book_details(request, course_id)
    references_details = get_ref_details(request, course_id)
    course = Course.objects.filter(id=course_id, created_by_id=request.user.id).values()
    course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    # co_requisites = CourseCoRequisites.objects.filter(course_id=course_id).values('id', 'co_requisites')
    pso = ProgramSpecificOutcome.objects.filter(course_id=course_id).values('id', 'pso')
    # pre_requisites = CoursePreRequisites.objects.filter(course_id=course_id).values('id', 'pre_requisites')
    pedagogy_tools = PedagogyTools.objects.values('id', 'name')
    co_po_pso = CourseCoPoPso.objects.filter(course_id=course_id).values()
    dept = DepartmentInstituteCodes.objects.get(id=request.user.dept_code_id)
    course_types = CourseType.objects.get(id=course_details.course_type_id)
    level_course = LevelOfCourse.objects.get(id=course_details.level_of_course_id)
    course_cat = CourseCategory.objects.get(id=course_details.course_category_id)
    course_code = dept.dept_code + course_types.code + level_course.code + course_cat.code + 'XX'
    co_po_psos = []
    count = 0
    for co in course_outcome:
        co['po'] = co_po_pso[count]
        co_po_psos.append(co)
        count = count + 1
    template = ''
    if course_details.course_type_id == 1 or course_details.course_type_id == 5:
        template = 'forms/theorypreview.html'
    elif course_details.course_type_id == 2:
        template = 'forms/practicalpreview.html'
    elif course_details.course_type_id == 3:
        template = 'forms/theory_practical_preview.html'
    elif course_details.course_type_id == 4:
        template = 'forms/projectpreview.html'
    else:
        template = ''
    context = {'users': users, 'course_id': encrypt(course_details.id), 'dept': dept, 'user_details': user_details,
               'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
               'course_details': course_details, 'active_step': course_details.active_step,
               'course_syllabus': course_syllabus,'practical_syllabus':practical_syllabus,
               'course_book_details': course_book_details, 'references_details': references_details, 'course': course,
               'course_outcome': course_outcome,
               'pso': pso,  'co_po_pso': co_po_psos,
               'pedagogy_tools': pedagogy_tools,'course_code':course_code}
    return render(request, template, context)

@csrf_exempt
@login_required
@group_required('STAFF')
def update_file(request,course_id):
    from django.core.files.storage import FileSystemStorage
    course = Course.objects.get(id=course_id)
    if request.method == "POST":
        filename_1 = ''
        filename_2 = ''
        fs = FileSystemStorage(location='media/user/'+str(request.user.id)+'/')
        if request.FILES.get('instruction_plan'):
            resume = request.FILES.get('instruction_plan')
            filename_1 = fs.save(resume.name, resume)
            uploaded_file_url = fs.url(filename_1)
        if request.FILES.get('instruction_plan_practical'):
            resume = request.FILES.get('instruction_plan_practical')
            filename_2 = fs.save(resume.name, resume)
            uploaded_file_url = fs.url(filename_2)
        try:
            if course.course_type_id == 1 or course.course_type_id == 5:
                Course.objects.filter(id=course_id, created_by_id=request.user.id).update(instruction_plan=filename_1)
            elif course.course_type_id == 2:
                Course.objects.filter(id=course_id, created_by_id=request.user.id).update(instruction_plan_practical=filename_2)
            elif course.course_type_id == 3:
                Course.objects.filter(id=course_id, created_by_id=request.user.id).update(instruction_plan=filename_1,instruction_plan_practical=filename_2)
            elif course.course_type_id == 4:
                Course.objects.filter(id=course_id, created_by_id=request.user.id).update(instruction_plan=filename_1)
            data={'status':'200','message':'File uploaded successfully','name':filename_1}
            return JsonResponse(data,safe=False)
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(e,safe=False)
    return redirect('index')

@csrf_exempt
@login_required
@group_required('STAFF')
def previous_step(request):
    response = {'status': 200, 'project': 'project'}
    return JsonResponse(response)

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
    if CourseBooks.objects.filter(course_id=course_id,created_by_id=request.user.id).exists():
        course_details =CourseBooks.objects.filter(course_id=course_id,created_by_id=request.user.id).values()
    return course_details

def get_ref_details(request,course_id):
    references_details = ''
    if References.objects.filter(course_id=course_id,created_by_id=request.user.id).exists():
        references_details =References.objects.filter(course_id=course_id,created_by_id=request.user.id).values()
    return references_details