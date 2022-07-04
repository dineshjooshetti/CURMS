from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from .models import *
from user_management.models import *
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
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
@group_required('PCMI','BOSC')
def course_edit(request,course_id):
    course_id = decrypt(course_id)
    if Course.objects.filter(created_by=request.user.id).exists():
        course_details = Course.objects.get(id=course_id)
        pid=course_details.program_id
        enc_pid=encrypt(pid)
        course_type = CourseType.objects.filter(status=1).values('id', 'name')
        level_of_course = ProgramLevelMapping.objects.filter(program=course_details.program_id).values('level__level','level')
        course_category = CourseCategory.objects.values('id', 'category')
        csmi = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=3, is_active=1,course_status_level_id__in=[1, 13]).values('to_user_id','to_user__username',
                                                                                             'to_user__first_name','to_user__email').last()
        csmc = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=2, is_active=1).values('to_user_id', 'to_user__username', 'to_user__first_name',
                                                                                                             'to_user__email')
        course = Course.objects.get(id=course_id)
        user_di = User.objects.values('dept_code__dept_code', 'institution').distinct()
        campus = CourseCampusMapping.objects.filter(course_id=course_id).values('campus_id')
        
        dept = list(set([j['dept_code__dept_code'] for j in user_di if j['dept_code__dept_code'] != None]))
        inst = list(set([j['institution'] for j in user_di if j['institution'] != None]))
        dept_det = CourseDepartmentMapping.objects.filter(course_id=course_id).values('department')
        inst_det = CourseInstituteMapping.objects.filter(course_id=course_id).values('institute')
        campus_det = Campus.objects.values('id', 'name')
        if request.method == 'POST':
            try:
                L = 0
                T = 0
                P = 0
                S = 0
                J = 0
                C = 0
                if request.POST['type_of_course'] == '1':
                    L = int(request.POST['L'])
                    T = int(request.POST['T'])
                    C = int(L)+int(T)
                elif request.POST['type_of_course'] == '2':
                    P = int(request.POST['P'])
                    C=int(P)*0.5
                elif request.POST['type_of_course'] == '3':
                    L = int(request.POST['L'])
                    T = int(request.POST['T'])
                    P = int(request.POST['P'])
                    C=int(L)+int(T)+(int(P)*0.5)
                elif request.POST['type_of_course'] == '4':
                    J = int(request.POST['J'])
                    C=int(request.POST['C'])
                elif request.POST['type_of_course'] == '5':
                    S = int(request.POST['S'])
                    C=S
                elif request.POST['type_of_course'] == '6':
                    L = int(request.POST['L'])
                    T = int(request.POST['T'])
                    P = int(request.POST['P'])
                    J = int(request.POST['J'])
                    S = int(request.POST['S'])
                    C=0   
                campus_get = request.POST.getlist('campus')
                dept_get = request.POST.getlist('dept')
                inst_get = request.POST.getlist('inst')
                if Course.objects.filter(id=course_id).exists():
                    Course.objects.filter(id=course_id).update(course_name=request.POST['course_title'],
                                                               course_type_id=request.POST['type_of_course'],
                                                               level_of_course_id=request.POST['level_of_course'],
                                                               course_category_id=request.POST['course_category'],
                                                               L=L, T=T,P=P, S=S,J=J, C=int(C),total_no_of_contact_hours=int(C)*15,
                                                               modified=datetime.now(), modified_by_id=request.user.id
                                                               )
                                                               
                    if CourseDepartmentMapping.objects.filter(course_id=course_id).exists():
                        CourseDepartmentMapping.objects.filter(course_id=course_id).delete()
                    for i in range(len(dept_get)):
                        CourseDepartmentMapping.objects.create(department=dept_get[i], course_id=course_id,
                                                                   created=datetime.now(), user_id=request.user.id)

                    if CourseInstituteMapping.objects.filter(course_id=course_id).exists():
                        CourseInstituteMapping.objects.filter(course_id=course_id).delete()
                    for k in range(len(inst_get)):
                        CourseInstituteMapping.objects.create(institute=inst_get[k], course_id=course_id,
                                                              created=datetime.now(), user_id=request.user.id)

                    if CourseCampusMapping.objects.filter(course_id=course_id).exists():
                        CourseCampusMapping.objects.filter(course_id=course_id).delete()
                    for j in range(len(campus_get)):
                        CourseCampusMapping.objects.create(campus_id=campus_get[j], course_id=course_id,
                                                           created=datetime.now(), user_id=request.user.id)
                    csmi_id = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=3, is_active=1,to_user_id=request.POST.get('csmi_old')).values('course_status_level_id','to_user_id')
                    if csmi_id:
                        csmi_id=csmi_id.last()
                        if not  csmi_id['to_user_id'] ==  int(request.POST.get('csmi')):
                            CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=3, is_active=1,to_user_id=csmi_id['to_user_id']).update(is_active=0,is_edit=0)
                            CourseUserMapping.objects.create(created=datetime.now, is_edit=0,
                                                         course_id=course_id, course_status_level_id=13,
                                                         to_user_id=request.POST.get('csmi'), user_id=request.user.id,
                                                         to_user_group_id=3, user_group_id=5,
                                                         course_header_id=course.course_header_id)
                            if not UserGroups.objects.filter(user_id=request.POST.get('csmi'), group_id=3).exists():
                                UserGroups.objects.create(user_id=request.POST.get('csmi'), group_id=3, is_active=0, is_block=0,is_default=0, role='CSMI')
                             
                                                         
                    try:                                     
                        csmc_id = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=2, is_active=1,to_user_id=request.POST.get('csmc_old')).values('course_status_level_id','to_user_id')
                    except Exception as e:
                        csmc_id=None
                    if csmc_id:
                        csmc_id=csmc_id.last()
                        if not  csmc_id['to_user_id'] ==  int(request.POST.get('csmc')):
                            CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=2,to_user_id=csmc_id['to_user_id'],is_active=1).update(is_active=0, is_edit=0)
                            CourseUserMapping.objects.create(created=datetime.now, is_edit=1,
                                                         course_id=course_id, course_status_level_id=13,
                                                         to_user_id=request.POST.get('csmc'), user_id=request.user.id,
                                                         to_user_group_id=2, user_group_id=5,
                                                         course_header_id=course.course_header_id)
                        if not UserGroups.objects.filter(user_id=request.POST.get('csmc'), group_id=2).exists():
                            UserGroups.objects.create(user_id=request.POST.get('csmc'), group_id=2, is_active=0, is_block=0,
                                                      is_default=0, role='CSMM')
                    else:
                        CourseUserMapping.objects.create(created=datetime.now, is_edit=1,
                                                         course_id=course_id, course_status_level_id=13,
                                                         to_user_id=request.POST.get('csmc'), user_id=request.user.id,
                                                         to_user_group_id=2, user_group_id=5,
                                                         course_header_id=course.course_header_id)
                        if not UserGroups.objects.filter(user_id=request.POST.get('csmc'), group_id=2).exists():
                            UserGroups.objects.create(user_id=request.POST.get('csmc'), group_id=2, is_active=0, is_block=0,
                                                      is_default=0, role='CSMM')
                        
                    messages.success(request,'Updated successful')
                    if UserGroups.objects.filter(group_id=5,is_active=1,user_id=request.user.id).exists():
                        return redirect('/pcmi/pcmi_program_detail/'+ encrypt(pid))
                    elif UserGroups.objects.filter(group_id=6, is_active=1, user_id=request.user.id).exists():
                        return redirect('/bosc/bosc_program_detail/' + encrypt(pid))
            except Exception as e:
                messages.error(request, str(e))
                ErrorLogs.objects.create(log=str(e)+'--Course Edit', info=request.POST,user_id=request.user.id)
                response = {'status': 500, 'error': str(e), 'project': 'project'}
                return render(request,'course_management/course_edit.html',{'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
                   'course_details': course_details,'p_id':encrypt(course_details.program_id),'course_id':encrypt(course_id),'enc_pid':enc_pid,
                   'campus': campus,'dept_det':dept_det,'inst_det':inst_det,'campus_det':campus_det,'dept':dept,'inst':inst}
                   )
        context = {'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,'course_details': course_details,'p_id':encrypt(course_details.program_id),
                   'course_id':encrypt(course_id),'csmi':csmi,'csmc':csmc,'enc_pid':enc_pid,'pre_url':request.META.get('HTTP_REFERER'),
                   'campus': campus,'dept_det':dept_det,'inst_det':inst_det,'campus_det':campus_det,'dept':dept,'inst':inst}
        return render(request, 'course_management/course_edit.html',context)
    else:
        ErrorLogs.objects.create(log='Not Authorised Access --Course Edit',user_id=request.user.id)
        return redirect('/')

@login_required
@group_required('PCMI','BOSC')
def course_del(request):
    if request.method == "POST":
        try:
            if CourseBooks.objects.filter(course_id=request.POST['course_del']).exists():
                CourseBooks.objects.filter(course_id=request.POST['course_del']).delete()
            if References.objects.filter(course_id=request.POST['course_del']).exists():
                References.objects.filter(course_id=request.POST['course_del']).delete()
            if CourseSyllabus.objects.filter(course_id=request.POST['course_del']).exists():
                CourseSyllabus.objects.filter(course_id=request.POST['course_del']).delete()
            if CourseUnits.objects.filter(course_id=request.POST['course_del']).exists():
                CourseUnits.objects.filter(course_id=request.POST['course_del']).delete()
            if CourseSyllabusPractical.objects.filter(course_id=request.POST['course_del']).exists():
                CourseSyllabusPractical.objects.filter(course_id=request.POST['course_del']).delete()
            if CourseUserMapping.objects.filter(course_id=request.POST['course_del']).exists():
                CourseUserMapping.objects.filter(course_id=request.POST['course_del']).delete()
            CourseOutcome.objects.filter(course_id=request.POST['course_del']).delete()
            ProgramSpecificOutcome.objects.filter(course_id=request.POST['course_del']).delete()
            CourseCoPoPso.objects.filter(course_id=request.POST['course_del']).delete()
            Course.objects.filter(id=request.POST['course_del']).delete()
            messages.success(request, "Deleted Successfully..")
            return redirect('pcmi_program_detail', encrypt(request.POST['p_id']))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e),info=request.POST)
            return redirect('pcmi_program_detail', encrypt(request.POST['p_id']))
    else:
        return redirect('/')

def co_po_pso_average(request,co_po_pso,course_id):
    pso = ProgramSpecificOutcome.objects.filter(course_id=course_id).values('id', 'pso')
    po1 = []
    po2 = []
    po3 = []
    po4 = []
    po5 = []
    po6 = []
    po7 = []
    po8 = []
    po9 = []
    po10 = []
    po11 = []
    po12 = []
    pso1 = []
    pso2 = []
    pso3 = []
    pso4 = []
    for i in co_po_pso:
        if i['po1'] != None:
            po1.append(i['po1'])
        if i['po2'] != None:
            po2.append(i['po2'])
        if i['po3'] != None:
            po3.append(i['po3'])
        if i['po4'] != None:
            po4.append(i['po4'])
        if i['po5'] != None:
            po5.append(i['po5'])
        if i['po6'] != None:
            po6.append(i['po6'])
        if i['po7'] != None:
            po7.append(i['po7'])
        if i['po8'] != None:
            po8.append(i['po8'])
        if i['po9'] != None:
            po9.append(i['po9'])
        if i['po10'] != None:
            po10.append(i['po10'])
        if i['po11'] != None:
            po11.append(i['po11'])
        if i['po12'] != None:
            po12.append(i['po12'])
        if i['pso1'] != None:
            pso1.append(i['pso1'])
        if i['pso2'] != None:
            pso2.append(i['pso2'])
        if i['pso3'] != None:
            pso3.append(i['pso3'])
        if len(pso) == 4:
            if i['pso4'] != None:
                pso4.append(i['pso4'])
            
    if pso4 ==[]:
        final_list = [po1,po2,po3,po4,po5,po6,po7,po8,po9,po10,po11,po12,pso1,pso2,pso3]
    else:
        final_list = [po1,po2,po3,po4,po5,po6,po7,po8,po9,po10,po11,po12,pso1,pso2,pso3,pso4]
    avg = []
    for j in  final_list:
        if j != []:
            avg.append(round(sum(j)/len(j),2))
        elif j == []:
            avg.append(' ')
    return avg