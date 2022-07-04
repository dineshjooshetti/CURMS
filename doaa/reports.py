from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from programs.models import *
from datetime import datetime, timedelta
from datetime import date
from django.contrib import messages
from django.contrib.auth.models import  Group
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from user_management.encryption_util import *
from course_management.models import *
from user_management.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.template.loader import render_to_string
from user_management.utils import *
from course_management.course_operations import co_po_pso_average
from django.db.models import Count
import xlwt



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
def curriculum_status(request):
    user_di = User.objects.values('dept_code__dept_code').order_by('dept_code__dept_code').distinct()
    department = sorted(list(set([j['dept_code__dept_code'] for j in user_di if j['dept_code__dept_code'] != None])))
    dept_details_list = None
    l=''
    if request.method == 'GET':
        try:
            dept = request.GET.get('department')
            dept_list=Programs.objects.filter(user__dept_code__dept_code=dept).values('name','id','program_type__type')
            l=[]
            for i in dept_list:
                p=ProgramUserMapping.objects.filter(program_id=i['id']).values_list('program_status_level__title',flat=True).last()
                i['program_status']=p
                i['encrypt_id']=encrypt(i['id'])
                l.append(i)
            return render(request, 'doaa/curriculum_status.html', {'dept_list': l, 'department': department,'dept_id':dept})
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return render(request, 'doaa/curriculum_status.html', {'dept_list': l, 'department': department})
    return render(request,'doaa/curriculum_status.html',{'dept_list':l,'department':department})


@login_required
@group_required('DOAA','ADMIN','DOAAAD')
def curriculum_status_program_details(request,program_id):
    p_id = decrypt(program_id)
    program = Programs.objects.filter(id=p_id).values()
    e=[]
    for ed in program:
        ed['encrypt_id']=encrypt(ed['id'])
    if program:
        program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')

        courses = Course.objects.filter(program_id=p_id).values('course_name', 'course_category__category',
                                                                'course_type__name', 'id', 'course_type_id',
                                                                'level_of_course__level', 'L', 'T', 'P', 'J', 'S', 'C',
                                                                'level_of_course_id', 'course_header_id','active_step')
        assign_courses = CourseUserMapping.objects.filter(course__program_id=p_id).values('course_status_level__title','course_id','course_status_level_id')
        campus_detail = CourseCampusMapping.objects.filter(course__program_id=p_id).values('campus__name', 'course_id')

        depart_detail = CourseDepartmentMapping.objects.filter(course__program_id=p_id).values('department',
                                                                                               'course_id')
        inst_detail = CourseInstituteMapping.objects.filter(course__program_id=p_id).values('institute', 'course_id')

        program_timeline = []
        program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created', 'to_user_id',
                                                                                             'user__first_name',
                                                                                             'user_id',
                                                                                             'program_status_level__title',
                                                                                             'to_user__first_name',
                                                                                             'user__image', 'comment',
                                                                                             'to_user_group__description',
                                                                                             'user_group__description').order_by('-id')

        pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id, is_edit=1).values('created', 'to_user_id',
                                                                                                'program_status_level__title',
                                                                                                'to_user__first_name',
                                                                                                'to_user__image',
                                                                                                'comment',
                                                                                                'to_user_group__description',
                                                                                                'user_group__description').last()
        program_timeline.append(pending_timeline)
        program_timeline.extend(program_timeline_actions)
        program_structures = []

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

                        c.append(j)
                c_ids.append(j['course_header_id'])
            i['course_structures'] = c
            if len(c) > 0:
                program_structures.append(i)

        context={'campus_detail':campus_detail,'depart_detail':depart_detail,'inst_detail':inst_detail,'program_structures':program_structures,'program':program,'program_timeline':program_timeline}

    return render(request,'doaa/curriculum_status_program_details.html',context)



def curriculum_status_download(request,program_id):
    p_id=decrypt(program_id)
    program=Programs.objects.filter(id=p_id).values('name')
    #print(program)
    response = HttpResponse(content_type ='application/ms-excel')
    response['Content-Disposition'] =  'attachment; filename='+ program[0]['name'] +" "+(datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M'))+'.xls'
    wb = xlwt.Workbook()
    row_num=0
    font_style = xlwt.XFStyle()
    font_style.font.bold =True
    columns = ['Course Title','Course Status','Course Type','Category','Campus','Institute','Department','L','T','P','J','S','C','Syllabus Status']

    program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')

    courses = Course.objects.filter(program_id=p_id).values('course_name',
                                                            'course_type__name','course_category__category',
                                                             'level_of_course__level','level_of_course_id','course_type_id',
                                                             'course_header_id','id','L', 'T', 'P', 'J', 'S', 'C','active_step')
    assign_courses = CourseUserMapping.objects.filter(course__program_id=p_id).values('course_status_level__title',
                                                                                      'course_id',
                                                                                      'course_status_level_id')
    campus_detail = CourseCampusMapping.objects.filter(course__program_id=p_id).values('campus__name', 'course_id')


    depart_detail = CourseDepartmentMapping.objects.filter(course__program_id=p_id).values('department',
                                                                                           'course_id')
    inst_detail = CourseInstituteMapping.objects.filter(course__program_id=p_id).values('institute', 'course_id')
    depins_course = []
    dept_course = depart_detail.values_list('course_id', flat=True)
    inst_course = inst_detail.values_list('course_id', flat=True)
    program_structures = []
    ltpjs_course = []
    
    for i in program_level:
        c = []
        c_ids = []
        final_l = []
        for j in courses:
            new_l = []
            new_l.append(j['course_name'])
            if not j['course_header_id'] in c_ids:
                if j['level_of_course_id'] == i['level_id']:
                    l = []
                    for k in assign_courses:
                        if j['id'] == k['course_id']:
                            j['course_status'] = k['course_status_level__title']
                            l.append(str(k['course_status_level__title']))
                        
                    if len(l)>0:
                        new_l.append(l[-1])
                    else:
                        new_l.append("Course structure uploaded")
                    new_l.append(j['course_type__name'])
                    new_l.append(j['course_category__category'])
                    j['cp_dtls'] = [cc['campus__name'] for cc in campus_detail if j['id']==cc['course_id']]
                    j['ins_dtls'] = [di['institute'] for di in inst_detail if j['id']==di['course_id']]
                    j['dep_dtls'] = [ci['department'] for ci in depart_detail if j['id']==ci['course_id']]
                    new_l.append(j['cp_dtls'])
                    new_l.append(j['ins_dtls'])
                    new_l.append(j['dep_dtls'])
                   
                    new_l.append(j['L'])
                    new_l.append(j['T'])
                    new_l.append(j['P'])
                    new_l.append(j['J'])
                    new_l.append(j['S'])
                    new_l.append(j['C'])
                    if j['active_step']:
                        if j['active_step']== 1:
                            j['active_stp']= 'Personal details'
                        elif j['active_step']== 2:
                            j['active_stp'] = 'Course code details'
                        elif j['active_step']== 3:
                            j['active_stp'] = 'About the course'
                        elif j['active_step']== 4:
                            j['active_stp'] = 'Syllabus'
                        elif j['active_step']== 5:
                            j['active_stp'] = ' Bibliography'
                        elif j['active_step']== 6 :
                            j['active_stp'] = 'CO-PO-PSO'
                    else:
                        j['active_stp'] = 'Not Created'
                    new_l.append(j['active_stp'])
                    c.append(j)
                    final_l.append(new_l)
           
        i['Course_Structure'] = final_l
        if len(c) > 0:
            program_structures.append(i)

    for row in program_structures :
        ws = wb.add_sheet("Level"+row['level__level'])
        #ws.col(0).width = 550
        for col_num in range(len(columns)):
            ws.col(col_num).width = 2550
            ws.write(row_num, col_num, columns[col_num], font_style)
        
        for i in range(len(row['Course_Structure'])):
            col_num=-1
            for j in row['Course_Structure'][i]:
                col_num = col_num + 1
                if type(j) is list:
                    ws.write(i+1,col_num,','.join(j))
                else:
                    ws.write(i+1,col_num,j)
    wb.save(response)
    return  response

