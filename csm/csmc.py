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
@group_required("CSMC")
def index(request):

    course_details = CourseUserMapping.objects.filter(to_user_id=request.user.id,to_user_group_id=2,course_status_level_id__in=[1,13],is_active=1,is_edit__in=[0,1]).values('is_edit','course_id', 'course_header_id','course__version_status','course__course_name',
                                          'course__course_type__name','course_id','user__first_name','user__username','course__course_category__category','user__dept_code__dept_code','course__course_code').order_by('-created')


    course_det = []
    course_header = []
    for i in course_details:
        if not i['course_header_id'] in course_header:
            i['encrypt_id'] = encrypt(i['course_id'])
            course_status= CourseUserMapping.objects.filter(course_id=i['course_id']).values('course_id','course_status_level_id','course_status_level__title').last()
            i['course_status']=course_status['course_status_level__title']
            course_det.append(i)
        course_header.append(i['course_id'])



    return render(request, 'csmc/index.html', {'course_det':course_det})

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
@group_required('CSMC','CSMI','PCMI','BOSC')
def dev_details_save(request):
    if request.method == "POST":
        try:
            #User.objects.filter(id=request.user.id).update(dept_code_id=request.POST['dept_inst'])
            response = {'status': 200, 'project': 'project'}
            return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

@csrf_exempt
@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def course_details_save(request):
    if request.method == "POST":
        try:

            if not request.POST['id'] == '':
                dept = DepartmentInstituteCodes.objects.get(id=request.user.dept_code_id)
                course_types = CourseType.objects.get(id=request.POST['type_of_course'])
                #level_course = LevelOfCourse.objects.get(id=request.POST['level_of_course'])
                #course_cat = CourseCategory.objects.get(id=request.POST['course_category'])
                if Course.objects.filter(id=request.POST['id']).exists():
                    course_code=dept.dept_code + course_types.code + request.POST['id']
                    Course.objects.filter(id=request.POST['id']).update(active_step=3,course_code=course_code)
                    insert = Course.objects.get(id=request.POST['id'])
                    response = {'status': 200, 'enc_id': encrypt(insert.id)}
                    return JsonResponse(response)
            else:
                insert = Course.objects.create(course_name=None, course_type_id=request.POST['type_of_course'],
                                               # level_of_course_id=request.POST['level_of_course'],
                                               # course_category_id=request.POST['course_category'],
                                               created=datetime.now(), active_step=3,dept_code_id=request.POST['dept_inst'])
                response = {'status': 200, 'enc_id': encrypt(insert.id)}
                return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def course_details(request,course_id):
    course_id = decrypt(course_id)
    users = User.objects.filter(Q(is_active=1), ~Q(id=request.user.id)).exclude(groups__name__in=["GUEST", 'Admin', 'HOD', 'HOI']).values()
    user_details = User.objects.get(id=request.user.id)
    dept = DepartmentInstituteCodes.objects.values('id', 'dept_inst')
    course_type = CourseType.objects.values('id', 'name')
    #course_levels = LevelOfCourse.objects.filter(course_type_id=course_details.program_type_id, status=1).values('id', 'level','code')
    course_category = CourseCategory.objects.values('id', 'category')
    course_details = Course.objects.get(id=course_id)
    course_levels = ProgramLevel.objects.filter(program_type_id=course_details.program_type_id, status=1).values('id', 'level')

    course_level = CourseUserMapping.objects.filter(course_status_level_id=1).values_list('course_id')
    pre_requisites_courses=Course.objects.filter(dept_code_id=course_details.dept_code_id,id__in=course_level).exclude(id=course_id).values()
    pre_requisites_courses_ids=CoursePrerequestiesMapping.objects.filter(course_id=course_id).values_list('prerequesti_id',flat=True)
    co_requisites_courses_ids=CourseCorequestiesMapping.objects.filter(course_id=course_id).values_list('corequesti_id',flat=True)

    course_syllabus = get_syllabus(request,course_id)
    total_units = 5
    new_units = len(course_syllabus)
    if new_units == 0:
        new_units=2
    journal_details = get_journal_details(request, course_id)
    website_details = get_website_details(request, course_id)
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values()
    syllabus_type = SyllabusType.objects.values('id','name')
    course_book_details = get_course_book_details(request,course_id)
    references_details = get_ref_details(request,course_id)
    course = Course.objects.filter(id=course_id).values()
    outcome_length=1
    total_outcoms=6
    if course_details.course_outcome:
        outcome_length=len(course_details.course_outcome)+outcome_length
        total_outcoms=total_outcoms-len(course_details.course_outcome)-1
    
    obj_length=1
    total_objectives=6
    if course_details.course_objectives:
        obj_length=len(course_details.course_objectives)+obj_length
        total_objectives=total_objectives-len(course_details.course_objectives)-1
    pedagogy_tools = PedagogyTools.objects.values('id','name')
    course_owner=CourseUserMapping.objects.filter(is_active=1,to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()
    selected_sdg=None
    if course_details.sdg:
        selected_sdg=[int(i) for i in course_details.sdg]
    context = {'users':users,'course_id':encrypt(course_details.id),'dept': dept, 
            'user_details': user_details,'course_type': course_type, 
                'course_category': course_category,
               'course_details': course_details,'active_step':course_details.active_step,
               'course_syllabus':course_syllabus,'new_units':range(1,new_units+1),
               'new_outcomes':range(outcome_length,total_outcoms),'new_objectives':range(obj_length,total_objectives),'unit_length':new_units,
               'course_book_details':course_book_details,'references_details':references_details,
               'course':course,'course_owner':course_owner,'pedagogy_tools':pedagogy_tools,
               'syllabus_type':syllabus_type,'practical_syllabus':practical_syllabus,'journal_details':journal_details,'website_details':website_details,
               'course_levels':course_levels,'pre_requisites_courses':pre_requisites_courses,'sdg':range(1,18),
               'pre_requisites_courses_ids':list(pre_requisites_courses_ids),'selected_sdg':selected_sdg,
               'co_requisites_courses_ids':list(co_requisites_courses_ids)}
    return render(request, 'forms/form_base.html',context)

@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def about_course_save(request):
    if request.method == "POST":
        course_id = request.POST['course_id']
        course_type_id = request.POST['course_type_id']
        try:
            if Course.objects.filter(id=course_id).exists():
                course=Course.objects.get(id=course_id)
                course_level_id=ProgramLevel.objects.get(id=int(request.POST['level_of_course']))
                course_code=course.course_code[0:4] +str(course_level_id.level)+ course.course_code[4+1: ]
                Course.objects.filter(id=course_id).update(alternative_exposure=request.POST['alt_exposure'],
                    course_descrption=request.POST['course_description'],pre_requisites=request.POST['pre_requisites'],
                    level_of_course_id=request.POST['level_of_course'],co_requisites=request.POST['co_requisites'],
                    course_objectives=request.POST.getlist('course_objectives'),sdg=request.POST.getlist('sdg'),
                    sdg_description=request.POST['sdg_description'],course_outcome=request.POST.getlist('course_outcome')
                    ,course_code=course_code
                    )
                
                CoursePrerequestiesMapping.objects.filter(course_id=course_id).delete()
                if request.POST['pre_requisites'] == 'Yes':
                    for i in request.POST.getlist('pre_requisites_courses'):
                        CoursePrerequestiesMapping.objects.create(course_id=course_id, created_by_id=request.user.id, prerequesti_id=i)
                CourseCorequestiesMapping.objects.filter(course_id=course_id).delete()
                if request.POST['co_requisites'] == '1':
                    for i in request.POST.getlist('co_requisites_courses'):
                        CourseCorequestiesMapping.objects.create(course_id=course_id, created_by_id=request.user.id,corequesti_id=i)

            Course.objects.filter(id=course_id).update(active_step=2)
            response = {'status': 200, 'enc_id': encrypt(course_id)}
            return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

import ast
@csrf_exempt
@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
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
            if course.course_type_id == 1 or course.course_type_id == 5 or course.course_type_id==3 or course.course_type_id==6:
                if course.course_type_id == 5 and request.POST.get('form_type') == '2':
                    Course.objects.filter(id=course_id).update(project_topic=request.POST.getlist('project_topic'),form_type=request.POST.get('form_type'))
                    CourseSyllabus.objects.filter(course_id=course_id).delete()
                else:
                    if course.course_type_id == 5 and request.POST.get('form_type') == '1':
                        Course.objects.filter(id=course_id).update(form_type=request.POST.get('form_type'),project_topic=None)
                    dat = [int(i) for i in request.POST.getlist('contact_hours')]
                    if not course.course_type_id==6:
                        if not sum(dat) == int(course.total_no_of_contact_hours):
                            response = {'status': 500, 'error': 'total contact hours '+str(sum(dat))+ ' should be equal to '+ str(course.total_no_of_contact_hours), 'project': 'project'}
                            return JsonResponse(response)
                    CourseSyllabus.objects.filter(course_id=course_id).delete()
                    for i in range(len(unit_name)):
                        p_t = request.POST.getlist('pedagogy_tools_'+str(i+1))
                        pt_l = []
                        for j in range(len(p_t)):
                            pt_d = {}
                            pt_d["p_id"] = [ast.literal_eval(k) for k in request.POST.getlist('pedagogy_tools_'+str(i+1))][j]
                            pt_l.append(pt_d)
                        outcome_4 = None
                        if i < len(request.POST.getlist('learning_outcome_4')):
                            outcome_4 = request.POST.getlist('learning_outcome_4')[i]
                        level_4 = None
                        if i < len(request.POST.getlist('level_4')):
                            level_4 = request.POST.getlist('level_4')[i]
                        outcome_5 = None
                        if i < len(request.POST.getlist('learning_outcome_5')):
                            outcome_5 = request.POST.getlist('learning_outcome_5')[i]
                        level_5 = None
                        if i < len(request.POST.getlist('level_5')):
                            level_5 = request.POST.getlist('level_5')[i]
                        CourseSyllabus.objects.create(course_id=course_id,course_unit_id=None,unit_name=unit_name[i],
                                                      short_title=short_title[i],
                                                      number_of_contact_hours = number_of_contact_hours[i],
                                                      version=1,outcome_1=outcome_1[i],level_1 = level_1[i],
                                                      outcome_2 = outcome_2[i],level_2=level_2[i],
                                                      outcome_3=outcome_3[i],level_3=level_3[i],
                                                      outcome_4=outcome_4,level_4=level_4,
                                                      outcome_5=outcome_5,level_5=level_5,
                                                      pedagogy_tools=pt_l,
                                                      created=datetime.now(),created_by_id=request.user.id)
                    
                if course.course_type_id==3 or course.course_type_id==6:
                    CourseSyllabusPractical.objects.filter(course_id=course_id).delete()
                    for i in range(len(request.POST.getlist('syllabus_topic'))):
                        CourseSyllabusPractical.objects.create(course_id=course_id, syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                                                                   topic=request.POST.getlist('syllabus_topic')[i],
                                                                   created=datetime.now(),
                                                                   user_id=request.user.id, version=1)

            elif course.course_type_id == 2:
                CourseSyllabusPractical.objects.filter(course_id=course_id).delete()
                for i in range(len(request.POST.getlist('syllabus_topic'))):
                    CourseSyllabusPractical.objects.create(course_id=course_id, syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                                                               topic=request.POST.getlist('syllabus_topic')[i],
                                                               created=datetime.now(),
                                                                   user_id=request.user.id, version=1)
                # if CourseSyllabusPractical.objects.filter(course_id=course_id).exists():
                    # for i in range(len(request.POST.getlist('syllabus_topic'))):
                        # if i<len(request.POST.getlist('practical_id')):
                            # CourseSyllabusPractical.objects.filter(course_id=course_id,id=request.POST.getlist('practical_id')[i]).update(
                                # course_id=course_id, syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                                # topic=request.POST.getlist('syllabus_topic')[i])
                        # else:
                            # CourseSyllabusPractical.objects.create(course_id=course_id, syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                                                # topic=request.POST.getlist('syllabus_topic')[i],created=datetime.now(),user_id=request.user.id, version=1)

                # else:
                    # for i in range(len(request.POST.getlist('syllabus_topic'))):
                        # CourseSyllabusPractical.objects.create(course_id=course_id,syllabus_type_id=request.POST.getlist('syllabus_type')[i],
                                                               # topic=request.POST.getlist('syllabus_topic')[i],created=datetime.now(),
                                                               # user_id=request.user.id,version=1)
            

            elif course.course_type_id == 4:
                Course.objects.filter(id=course_id).update(project_topic=request.POST.getlist('project_topic'))
            else:
                pass
            Course.objects.filter(id=course_id).update(active_step=3)
            response = {'status': 200, 'enc_id': encrypt(course_id)}
            return JsonResponse(response)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(response)

@csrf_exempt
@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def course_book_save(request,course_id):
    if request.method == "POST":
        course = Course.objects.get(id=request.POST['cours_id'])
        course_id = request.POST['cours_id']
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
            isbn = request.POST.getlist('isbn')

            if CourseBooks.objects.filter(course_id = request.POST['cours_id']).exists():
                CourseBooks.objects.filter(course_id=request.POST['cours_id']).delete()
            for i in range(len(book_author1)):
                CourseBooks.objects.create( created=datetime.now,title=book_title[i],author=book_author[i],
                                            edition=book_edition[i],place_of_publication=book_publication[i],
                                            publisher=book_publisher[i],year=book_year[i],isbn=isbn[i],unit_mapping=request.POST.getlist('unit_mapping')[i],
                                                course_id = request.POST['cours_id'] , created_by_id=request.user.id)

            if References.objects.filter(course_id = request.POST['cours_id']).exists():
                References.objects.filter(course_id=request.POST['cours_id']).delete()
            for i in range(len(ref_author1)):
                References.objects.create(created=datetime.now, title=ref_title[i], author=ref_author[i],
                                               edition=ref_edition[i], place_of_publication=ref_publication[i],
                                               publisher=ref_publisher[i], year=ref_year[i],isbn=request.POST.getlist('ref_isbn')[i],
                                               unit_mapping=request.POST.getlist('ref_unit_mapping')[i],
                                               course_id=request.POST['cours_id'], created_by_id=request.user.id)

            if JournalBooks.objects.filter(course_id=request.POST['cours_id']).exists():
                JournalBooks.objects.filter(course_id=request.POST['cours_id']).delete()
            for b in range(len(request.POST.getlist('journal_title'))):
                if request.POST.getlist('journal_title')[b]:
                    JournalBooks.objects.create(title=request.POST.getlist('journal_title')[b],author=request.POST.getlist('journal_author')[b],
                                                year=request.POST.getlist('journal_year')[b],doi_url=request.POST.getlist('journal_url')[b],
                                                    pages=request.POST.getlist('journal_pages')[b] or None,unit_mapping=request.POST.getlist('journal_unit_mapping')[b],
                                                    course_id=request.POST['cours_id'],created=datetime.now(),created_by_id=request.user.id)
            if Websites.objects.filter(course_id=request.POST['cours_id']).exists():
                Websites.objects.filter(course_id=request.POST['cours_id']).delete()
            for w in range(len(request.POST.getlist('name_website'))):
                if(request.POST.getlist('name_website')[w]):
                    last_accessed=None
                    if request.POST.getlist('last_accesed')[w]:
                        last_accessed = datetime.strptime(request.POST.getlist('last_accesed')[w], '%d-%m-%Y').strftime('%Y-%m-%d')
                    Websites.objects.create(name_website=request.POST.getlist('name_website')[w],last_accessed=last_accessed[w],
                                            website_url=request.POST.getlist('website_url')[w],unit_mapping=request.POST.getlist('website_unit_mapping')[w],
                                            course_id=request.POST['cours_id'],created=datetime.now(),created_by_id=request.user.id)



            # response = {'status': 200, 'project': 'project','enc_id': request.POST['cours_id']}
            # return JsonResponse(response,safe=False)

            if UserGroups.objects.filter(group_id=2,is_active=1,user_id=request.user.id).exists():
                return redirect('/csmc/course_preview/'+encrypt(course_id))
            elif UserGroups.objects.filter(group_id=3, is_active=1, user_id=request.user.id).exists():
                return redirect('/csmi/course_preview/' + encrypt(course_id))
            elif UserGroups.objects.filter(group_id=5, is_active=1, user_id=request.user.id).exists():
                return redirect('/pcmi/course_preview/' + encrypt(course_id))
            elif UserGroups.objects.filter(group_id=6, is_active=1, user_id=request.user.id).exists():
                return redirect('/bosc/course_preview/' + encrypt(course_id))
            else:
                return redirect('/')
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            #response = {'status': 500, 'error': str(e), 'project': 'project'}
            return redirect('/csmc/course_details/' + encrypt(course_id))

@csrf_exempt
@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def co_po_pso_save(request,course_id):
    course_id = decrypt(course_id)
    if request.method == "POST":
        try:
        #     if CourseCoPoPso.objects.filter(course_id=course_id).exists():
        #
        #         for c in range(len(request.POST.getlist('co'))):
        #             pso1=None
        #             if 'pso1' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso1')):
        #                     if request.POST.getlist('pso1')[c]:
        #                         pso1 = request.POST.getlist('pso1')[c]
        #             pso2=None
        #             if 'pso2' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso2')):
        #                     if request.POST.getlist('pso2')[c]:
        #                         pso2 = request.POST.getlist('pso2')[c]
        #             pso3 = None
        #             if 'pso3' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso3')):
        #                     if request.POST.getlist('pso3')[c]:
        #                         pso3 = request.POST.getlist('pso3')[c]
        #             pso4 = None
        #             if 'pso4' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso4')):
        #                     if request.POST.getlist('pso4')[c]:
        #                         pso4 = request.POST.getlist('pso4')[c]
        #             CourseCoPoPso.objects.filter(id=request.POST.getlist('co_po_pso_id')[c],course_id=course_id).update(co=request.POST.getlist('co')[c],
        #                                      po1=request.POST.getlist('po1')[c] or None,po2=request.POST.getlist('po2')[c] or None,
        #                                      po3=request.POST.getlist('po3')[c] or None,po4=request.POST.getlist('po4')[c] or None,po5=request.POST.getlist('po5')[c] or None,
        #                                      po6=request.POST.getlist('po6')[c] or None,po7=request.POST.getlist('po7')[c] or None,po8=request.POST.getlist('po8')[c] or None,
        #                                      po9=request.POST.getlist('po9')[c] or None,po10=request.POST.getlist('po10')[c] or None,po11=request.POST.getlist('po11')[c] or None,
        #                                      po12=request.POST.getlist('po12')[c] or None,
        #                                      pso1=pso1,pso2=pso2,
        #                                      pso3=pso3,pso4=pso4)
        #
        #     else:
        #         for c in range(len(request.POST.getlist('co'))):
        #             pso1=None
        #             if 'pso1' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso1')):
        #                     if request.POST.getlist('pso1')[c]:
        #                         pso1 = request.POST.getlist('pso1')[c]
        #             pso2=None
        #             if 'pso2' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso2')):
        #                     if request.POST.getlist('pso2')[c]:
        #                         pso2 = request.POST.getlist('pso2')[c]
        #             pso3 = None
        #             if 'pso3' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso3')):
        #                     if request.POST.getlist('pso3')[c]:
        #                         pso3 = request.POST.getlist('pso3')[c]
        #             pso4 = None
        #             if 'pso4' in request.POST.keys():
        #                 if c < len(request.POST.getlist('pso4')):
        #                     if request.POST.getlist('pso4')[c]:
        #                         pso4 = request.POST.getlist('pso4')[c]
        #             CourseCoPoPso.objects.create(co=request.POST.getlist('co')[c],
        #                                          po1=request.POST.getlist('po1')[c] or None,po2=request.POST.getlist('po2')[c] or None,
        #                                          po3=request.POST.getlist('po3')[c] or None,po4=request.POST.getlist('po4')[c] or None,po5=request.POST.getlist('po5')[c] or None,
        #                                          po6=request.POST.getlist('po6')[c] or None,po7=request.POST.getlist('po7')[c] or None,po8=request.POST.getlist('po8')[c] or None,
        #                                          po9=request.POST.getlist('po9')[c] or None,po10=request.POST.getlist('po10')[c] or None,po11=request.POST.getlist('po11')[c] or None,
        #                                          po12=request.POST.getlist('po12')[c] or None,
        #                                          pso1=pso1,pso2=pso2 or None,
        #                                          pso3=pso3 or None,pso4=pso4 or None,
        #                                          course_id=course_id,
        #                                          created=datetime.now(),user_id=request.user.id)

            if UserGroups.objects.filter(group_id=2,is_active=1,user_id=request.user.id).exists():
                return redirect('/csmc/course_preview/'+encrypt(course_id))
            elif UserGroups.objects.filter(group_id=3, is_active=1, user_id=request.user.id).exists():
                return redirect('/csmi/course_details_by_csmi/' + encrypt(course_id))
            elif UserGroups.objects.filter(group_id=5, is_active=1, user_id=request.user.id).exists():
                return redirect('/pcmi/course_preview_pcmi/' + encrypt(course_id))
            elif UserGroups.objects.filter(group_id=6, is_active=1, user_id=request.user.id).exists():
                return redirect('/bosc/course_preview_bosc/' + encrypt(course_id))
            else:
                return redirect('/')
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            return redirect('/csmc/course_details/'+encrypt(course_id))


@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def course_preview(request,course_id):
    course_id = decrypt(course_id)
    user_details = User.objects.get(id=request.user.id)
    course_type = CourseType.objects.values('id', 'name')
    level_of_course = ProgramLevel.objects.filter(status=1).values('id', 'level')
    course_category = CourseCategory.objects.values('id', 'category')
    course_details = Course.objects.get(id=course_id)
    course_syllabus = get_syllabus(request, course_id)
    journal_details = get_journal_details(request, course_id)
    website_details = get_website_details(request, course_id)
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values('id', 'topic', 'version','syllabus_type_id','syllabus_type__name').order_by('id')
    course_book_details = get_course_book_details(request, course_id)
    references_details = get_ref_details(request, course_id)
    course = Course.objects.filter(id=course_id).values()
    course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    pedagogy_tools = PedagogyTools.objects.values('id', 'name')
    course_pre_requisite = CoursePrerequestiesMapping.objects.filter(course_id=course_id).values('id', 'prerequesti__course_name')
    course_co_requisite = CourseCorequestiesMapping.objects.filter(course_id=course_id).values('id', 'corequesti__course_name')
    dept = DepartmentInstituteCodes.objects.get(id=request.user.dept_code_id)
    course_types = CourseType.objects.get(id=course_details.course_type_id)
    course_code = dept.dept_code + course_types.code + 'XX'
    course_timeline=CourseUserMapping.objects.filter(course_id=course_id).values('id','to_user__first_name','to_user__first_name','to_user__image',
                         'user__first_name','user__image','created','comment','to_user_group__description','course_status_level__title','user_group__description')
    course_owner=CourseUserMapping.objects.filter(is_active=1,to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()


    template = ''
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=2,is_edit=1,to_user_id=request.user.id).exists():
        is_edit = 1
    else:
        is_edit = 0
    template = 'csmc/forms/course_preview.html'
    
    context = {'course_id': encrypt(course_details.id), 'dept': dept, 'user_details': user_details,
               'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
               'course_details': course_details, 'active_step': course_details.active_step,
               'course_syllabus': course_syllabus,'practical_syllabus':practical_syllabus,'course_owner':course_owner,
               'course_book_details': course_book_details, 'references_details': references_details, 'course': course,
               'course_outcome': course_outcome,
                'is_edit':is_edit,'journal_details':journal_details,'website_details':website_details,
                'course_timeline':course_timeline,'course_pre_requisite':course_pre_requisite,'course_co_requisite':course_co_requisite,
               'pedagogy_tools': pedagogy_tools,'course_code':course_code}
    return render(request, template, context)

@csrf_exempt
@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def update_file(request,course_id):
    from django.core.files.storage import FileSystemStorage
    course = Course.objects.get(id=course_id)
    if request.method == "POST":
        filename_1 = ''
        filename_2 = ''
        fs = FileSystemStorage(location='media/user/instruction_plan/')
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
                Course.objects.filter(id=course_id).update(instruction_plan=filename_1)
            elif course.course_type_id == 2:
                Course.objects.filter(id=course_id).update(instruction_plan_practical=filename_2)
            elif course.course_type_id == 3 or course.course_type_id == 6:
                if request.FILES.get('instruction_plan'):
                    Course.objects.filter(id=course_id).update(instruction_plan=filename_1)
                if request.FILES.get('instruction_plan_practical'):
                    Course.objects.filter(id=course_id).update(instruction_plan_practical=filename_2)
            elif course.course_type_id == 4:
                Course.objects.filter(id=course_id).update(instruction_plan=filename_1)
            data={'status':'200','message':'File uploaded successfully','name':filename_1}
            return JsonResponse(data,safe=False)
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            response = {'status': 500, 'error': str(e), 'project': 'project'}
            return JsonResponse(e,safe=False)
    return redirect('index')

@csrf_exempt
@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
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
    if JournalBooks.objects.filter(course_id=course_id).exists():
        journal_details =JournalBooks.objects.filter(course_id=course_id).values()
    return journal_details

def get_website_details(request,course_id):
    website_details = ''
    if Websites.objects.filter(course_id=course_id).exists():
        website_details =Websites.objects.filter(course_id=course_id).values()
    return website_details

@login_required
@group_required('CSMC','CSMI','PCMI','BOSC')
def course_preview_submit(request,course_id):
    course_id = decrypt(course_id)
    if request.method == "POST":
        try:
            to_user_id = CourseUserMapping.objects.filter(course_id=course_id,course_status_level_id__in=[1,13],to_user_group_id=3,is_active=1).values('to_user_id','course_header_id').order_by('-id')
            CourseUserMapping.objects.create(created=datetime.now(),is_edit=1,course_id=course_id, course_status_level_id=2,to_user_group_id=3,user_group_id=2,
                                             to_user_id=to_user_id[0]['to_user_id'],user_id=request.user.id,course_header_id=to_user_id[0]['course_header_id'])
            CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=2,to_user_id=request.user.id).update(is_edit=0)
            email = User.objects.filter(id=to_user_id[0]['to_user_id']).values('email', 'id', 'first_name')
            course = Course.objects.get(id=course_id)
            course.status_id=2
            course.save()
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Uploaded the syllabus of "+course.course_name+" and requested to verify and forward to subject experts for suggestions."
            message = render_to_string('csmc/email_templates/csmc_forward_email.html', {
                'email': encrypt(email[0]['email']),
                'domain': current_site.domain,
                'guest_firstname': email[0]['first_name'],
                'course_code':course.course_code,
                'course_name':course.course_name,

            })
            e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            EmailStatus.objects.create(hint='CSMC Course final Submit', message=message, to_user_email=email[0]['email'],to_user_id=email[0]['id'], user_id=request.user.id)
            messages.success(request, "Submitted....")
            return redirect('/csmc/course_preview/' + encrypt(course_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST,user_id=request.user.id)
            return redirect('/csmc/course_preview/' + encrypt(course_id))
    else:
        return redirect('/csmc/course_preview/' + encrypt(course_id))
