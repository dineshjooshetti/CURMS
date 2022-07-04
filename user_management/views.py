from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from .models import *
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

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipaddress = x_forwarded_for.split(',')[-1].strip()
    else:
        ipaddress = request.META.get('REMOTE_ADDR')
    return ipaddress

def not_found(request):
    return HttpResponse('Page not found')

def user_not_found(request):
    return render(request, 'user_not_found.html')

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


def login_auth(request):
    url = ''
    try:
        import sys
        import clr
        sys.path.append("C:\inetpub\wwwroot\CMS")
        clr.AddReference(R"ClassLibrary1")
        from testDLLApp import Class1
        a = Class1()
        enc_url = request.GET.get('id')
        url = Class1.Decrypt(enc_url, True, 'Cums$dHs')
        username = url.split("#")
        empl_id = username[0]
        email = username[1]
        first_name = username[2]
        user_role = username[3]
        try:
            #go = Group.objects.get(name=user_role,id=4)
            go = Group.objects.get(name=user_role)
        except Group.DoesNotExist:
            error = "User Group " + user_role + " not found"
            ErrorLogs.objects.create(log=error, info=url)
            return redirect('/user/not_found')
        phone = username[4]
        if phone == '':
            phone = 0
        department = username[5]
        institute = username[6]
        campus = username[7]
        user_image = 'https://gstaff.gitam.edu/img1.aspx?empid=' + str(empl_id)
        designation = username[8]
        dob = username[9]

    except Exception as e:
        ErrorLogs.objects.create(log=str(e), info=url)
        return redirect('/user/not_found')
    user = ''
    if User.objects.filter(username=empl_id).exists():
        user = User.objects.get(username=empl_id)
        User.objects.filter(username=empl_id).update(department=department, campus=campus, institution=institute)
    else:
        try:
            ErrorLogs.objects.create(log='User not found', info=url)
            return redirect('/user/user_not_found')
            user = User.objects.create(designation=designation, username=empl_id, email=email, first_name=first_name,
                                       emp_id=empl_id, phone=phone, image=user_image, dob=dob, campus=campus,
                                       institution=institute, department=department)
            insert = UserGroups.objects.create(role='STAFF', is_active=1, is_default=True, group_id=1, user_id=user.id)
            insert.save()
            
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=url)
            return redirect('/user/not_found')
    if user:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        create = UserAuthLogs.objects.create(user=user, login_time=datetime.now(), ip_address=get_ip(request),
                                             session_key=request.session.session_key, login_data=url)
        user.image = user_image
        user.save() 
        if request.user.groups.filter(name__in=['PCMI'],usergroups__is_active=1).exists():
            return redirect('/pcmi')
        elif request.user.groups.filter(name__in=['PCMC'],usergroups__is_active=1).exists():
            return redirect('/pcmc')
        elif request.user.groups.filter(name__in=['BOSC'],usergroups__is_active=1).exists():
            
            return redirect('/bosc')
        elif request.user.groups.filter(name__in=['BOS'],usergroups__is_active=1).exists():
            return redirect('/bos')
        elif request.user.groups.filter(name__in=['CSMI'],usergroups__is_active=1).exists():
            return redirect('/csmi')
        elif request.user.groups.filter(name__in=['CSMC'],usergroups__is_active=1).exists():
            return redirect('/csmc')
        elif request.user.groups.filter(name__in=['STAFF'],usergroups__is_active=1).exists():
            return redirect('/staff')
        elif request.user.groups.filter(name__in=['DOAA','DOAAAD','ADMIN'],usergroups__is_active=1).exists():
            return redirect('/doaa')


        return redirect('/')


@login_required
def users(request):
    pass

@login_required
def index(request):
    if request.user.groups.filter(name__in=['PCMI'],usergroups__is_active=1).exists():
        return redirect('/pcmi')
    elif request.user.groups.filter(name__in=['PCMC'],usergroups__is_active=1).exists():
        return redirect('/pcmc')
    elif request.user.groups.filter(name__in=['BOSC'],usergroups__is_active=1).exists():
        return redirect('/bosc')
    elif request.user.groups.filter(name__in=['BOS'],usergroups__is_active=1).exists():
        return redirect('/bos')
    elif request.user.groups.filter(name__in=['CSMI'],usergroups__is_active=1).exists():
        return redirect('/csmi')
    elif request.user.groups.filter(name__in=['CSMC'],usergroups__is_active=1).exists():
        return redirect('/csmc')
    elif request.user.groups.filter(name__in=['STAFF'],usergroups__is_active=1).exists():
        return redirect('/staff')
    elif request.user.groups.filter(name__in=['PAB'],usergroups__is_active=1).exists():
        return redirect('/pab')
    elif request.user.groups.filter(name__in=['DOAA','DOAAAD','ADMIN'],usergroups__is_active=1).exists():
        return redirect('/doaa')

@login_required  
def userlogout(request):
    UserAuthLogs.objects.filter(user_id=request.user.id,session_key=request.session.session_key).update(logout_time=datetime.now())
    logout(request)
    return HttpResponseRedirect('https://login.gitam.edu/Login.aspx')

def pab_user_login(request,email):
    email=decrypt(email)
    if User.objects.filter(email=email).exists():
        user=User.objects.get(email=email)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        create = UserAuthLogs.objects.create(user=user, login_time=datetime.now(), ip_address=get_ip(request),
                                             session_key=request.session.session_key, login_data=email)
        return redirect('/pab')
    else:
        ErrorLogs.objects.create(log="user not found")
        return redirect('/user/not_found')


@login_required
def create_role(request,id):
    user_id = None
    if type(id) == str:
        user_id = decrypt(id)
    if request.method == "POST":
        user=User.objects.get(id=int(user_id))
        if User.objects.filter(groups__id=request.POST['group_id'], campus=user.campus,institution=user.institution, department=user.department).exists():
            group = Group.objects.get(id=request.POST['group_id'])
            messages.error(request, group.name + " User Role Already Exists")
            return redirect('/user/user_details/' + str(id))
        try:
            insert = UserGroups.objects.create(role=request.POST['role'],is_active=0,group_id=request.POST['group_id'],user_id=user_id)
            insert.save()
            insert_history = UserGroupsHistory.objects.create(role=request.POST['role'], is_active=0,is_default=False,
                                               group_id=request.POST['group_id'], user_id=user_id,createdby_id=request.user.id)
            insert_history.save()
            messages.success(request,"Roles created Successfully")
            return redirect('/user/user_details/'+str(id))
        except Exception as e:
            messages.error(request,str(e))
            ErrorLogs.objects.create(log=str(e),user_id=request.user.id)
            return redirect('/user/user_details/'+str(id))
    else:
        return redirect('/user/user_details/' + str(id))

@login_required
def update_role(request,id):
    user_id = None
    if type(id) == str:
        user_id = decrypt(id)
    if request.method == "POST":
        if UserGroups.objects.filter(id=request.POST['id'],role=request.POST['role'],group_id=request.POST['group_id']).exists():
            messages.success(request, "No changes applied")
            return redirect('/user/user_details/' + str(id))
        try:
            UserGroupsHistory.objects.filter(group_id=request.POST['group_id'], user_id=user_id, is_expired=0).update(
                is_expired=1,modified=datetime.now(), modifiedby_id=request.user.id)
            UserGroups.objects.filter(id=request.POST['id']).update(role=request.POST['role'],group_id=request.POST['group_id'])
            insert_history = UserGroupsHistory.objects.create(role=request.POST['role'],group_id=request.POST['group_id'], is_active=0,
                                user_id=request.user.id, createdby_id=request.user.id, is_default=0)
            insert_history.save()
            messages.success(request,"Roles Updated Successfully")
            return redirect('/user/user_details/'+str(id))
        except Exception as e:
            messages.error(request,str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('/user/user_details/'+str(id))
    else:
        return redirect('/user/user_details/' + str(id))



@login_required
def delete_role(request,id):
    user_id=None
    if type(id) == str:
        user_id = decrypt(id)
    if request.method == "POST":
        try:
            UserGroups.objects.filter(id=request.POST['id'],is_default=False).delete()
            UserGroupsHistory.objects.filter(group_id=request.POST['group_id'],is_default=False,user_id=user_id,is_expired=0).update(is_expired=1,
                                                modified=datetime.now(),modifiedby_id=request.user.id)
            a=UserGroups.objects.filter(user_id=user_id).first()
            a.is_active=True
            a.save()
            messages.success(request, "Roles Deleted Successfully")
            return redirect('/user/user_details/'+str(id))
        except Exception as e:
            messages.error(request,str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('/user/user_details/'+str(id))
    else:
        return redirect('/user/user_details/' + str(id))

@login_required
def switch_role(request,group_id):
    UserGroups.objects.filter(user_id=request.user.id).update(is_active=0)
    if UserGroups.objects.filter(user_id=request.user.id).exists():
        UserGroups.objects.filter(user_id=request.user.id,group_id=group_id).update(is_active=1)
        # messages.success(request, " Role changed successfully")
    else:
        messages.error(request,"You don't have Permission to access this role")
    return redirect('/')

@login_required
def my_profile(request):
    title = "My Profile"
    user = User.objects.get(id=request.user.id)
    return render(request, 'my_profile.html', {'title': title, 'user': user})


def url_encode(request):
    import sys
    import clr
    sys.path.append("F:\DSPS _Development\PHD_COUNSELLING\phd_counselling")
    clr.AddReference(R"ClassLibrary1")
    from testDLLApp import Class1
    a = Class1()
    enc_url = request.GET.get('id')
    #500853#lyedlapa@gitam.edu#Mr. Yedlapalli Lava Raju#STAFF#9618912359#CATS#CAO#VSP#PM#27-Jul-2021
    enc_url_data="2613#rkocharl@gitam.edu#Dr. K.V. Ramesh#STAFF#9848292228#ELEPHY#GIS#VSP#Senior Professor#23-Mar-2022"
    #url = Class1.Encrypt(enc_url_data, True, 'PrS$dHs')
    #url = Class1.Encrypt(enc_url_data, True, 'Cums$dHs')
    #url = Class1.Encrypt(enc_url_data, True, 'eFs$DHS')
    url = Class1.Encrypt(enc_url_data, True, 'glearn')
    #url = Class1.Decrypt(enc_url_data, True, 'Cums$dHs')
    #url = Class1.Decrypt(enc_url_data, True, 'PrS$dHs')
    return HttpResponse(url)




@login_required
@group_required('ADMIN','DOAA','DOAAAD')
def allstaff(request):
    title = "Users"
    users = User.objects.filter(is_superuser=0).exclude(usergroups__group_id=9).values('id',
    'last_login','username','first_name','campus','institution','department','phone','email','phone','designation','dept_code__dept_code')
    user_groups=UserGroups.objects.filter().values('user_id','group_id','group__name','role').order_by('-group_id')
    for i in users:
        i['groups']=[]
        i['enc_id']=encrypt(i['id'])
        for j in user_groups: 
            if i['id']==j['user_id']:
                i['groups'].append(j['role'])
        
    return render(request, 'user/staff.html', {'users':users,'title':title})
    

def session(request,id):
    id=decrypt(id)
    if User.objects.filter(id=id).exists():
        user = User.objects.get(id=id)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        #create = UserAuthLogs.objects.create(user=user, login_time=datetime.now(), ip_address=get_ip(request),
        #                                     session_key=request.session.session_key,login_data=url)
        if request.user.groups.filter(name__in=['PCMI'],usergroups__is_active=1).exists():
            return redirect('/pcmi')
        elif request.user.groups.filter(name__in=['PCMC'],usergroups__is_active=1).exists():
            return redirect('/pcmc')
        elif request.user.groups.filter(name__in=['BOSC'],usergroups__is_active=1).exists():
            return redirect('/bosc')
        elif request.user.groups.filter(name__in=['BOS'],usergroups__is_active=1).exists():
            return redirect('/bos')
        elif request.user.groups.filter(name__in=['CSMI'],usergroups__is_active=1).exists():
            return redirect('/csmi')
        elif request.user.groups.filter(name__in=['CSMC'],usergroups__is_active=1).exists():
            return redirect('/csmc')
        elif request.user.groups.filter(name__in=['STAFF'],usergroups__is_active=1).exists():
            return redirect('/staff')
        elif request.user.groups.filter(name__in=['DOAA','DOAAAD','ADMIN'],usergroups__is_active=1).exists():
            return redirect('/doaa')
        else:
            return redirect('/user/not_found')
    else:
        return redirect('/user/not_found')



def update_u_codes(request):
    import xlrd
    loc = ("media/U_C_I_C_D_mapping.xlsx")
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    
    for i in range(1, sheet.nrows):
        try:
            #campus institution mapping
            '''a=CampusInstitutionMapping.objects.filter(campus_id=Campus.objects.get(address=sheet.cell_value(i, 0)).pk,
                institution_id=Institutions.objects.get(institution_code=sheet.cell_value(i, 1)).pk).values()
            if not a:
                CampusInstitutionMapping.objects.create(campus_id=Campus.objects.get(address=sheet.cell_value(i, 0)).pk,
                institution_id=Institutions.objects.get(institution_code=sheet.cell_value(i, 1)).pk)'''
                
            #campus institution course mapping
            '''a=CampusInstitutionCourseMapping.objects.filter(campus_id=Campus.objects.get(address=sheet.cell_value(i, 0)).pk,
                institution_id=Institutions.objects.get(institution_code=sheet.cell_value(i, 1)).pk,
                course_id=UCourse.objects.get(name=sheet.cell_value(i, 4)).pk
                
                ).values()
            if not a:
                CampusInstitutionCourseMapping.objects.create(campus_id=Campus.objects.get(address=sheet.cell_value(i, 0)).pk,
                institution_id=Institutions.objects.get(institution_code=sheet.cell_value(i, 1)).pk,
                course_id=UCourse.objects.get(name=sheet.cell_value(i, 4)).pk
                )  '''  
            '''if DepartmentInstituteCodes.objects.filter(dept_code=sheet.cell_value(i, 6)).exists():
               DepartmentInstituteCodes.objects.filter(dept_code=sheet.cell_value(i, 6)).update(name=sheet.cell_value(i,2))
            else:
                print(sheet.cell_value(i, 6))'''
            department_id=DepartmentInstituteCodes.objects.filter(name=sheet.cell_value(i, 2)).values()
            if department_id:        
                a=CampusInstitutionCourseDepartmentMapping.objects.filter(
                    campus_id=Campus.objects.get(address=sheet.cell_value(i, 0)).pk,
                    institution_id=Institutions.objects.get(institution_code=sheet.cell_value(i, 1)).pk,
                    course_id=UCourse.objects.get(name=sheet.cell_value(i, 4)).pk,
                    department_id=department_id[0]['id']).values()
                if not a:
                    CampusInstitutionCourseDepartmentMapping.objects.create(
                    campus_id=Campus.objects.get(address=sheet.cell_value(i, 0)).pk,
                    institution_id=Institutions.objects.get(institution_code=sheet.cell_value(i, 1)).pk,
                    course_id=UCourse.objects.get(name=sheet.cell_value(i, 4)).pk,
                    department_id=department_id[0]['id'])
                    
        except Exception as e:
            print(e)
            pass
    return redirect('/')    