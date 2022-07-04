from course_management.functions import *


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


@csrf_exempt
def get_coursedepartment_by_campusinst(request):
    a = {}
    if request.method == "POST":
        campus=request.POST.getlist('campus_inst')[0].split(',')
        c_inst =CampusInstitutionMapping.objects.filter(id__in=campus).values('institution_id','campus_id')
        c_inst_course =CampusInstitutionCourseMapping.objects.filter(campus_id__in=c_inst.values_list('campus_id'),
            institution_id__in=c_inst.values_list('institution_id')).values('institution_id','campus_id','campus__name',
            'course__name','course_id','institution__institution_code')
        
        course_dept=CampusInstitutionCourseDepartmentMapping.objects.filter(campus_id__in=c_inst.values_list('campus_id'),
                   institution_id__in=c_inst.values_list('institution_id') ).values('course__name','department__dept_code',
                   'id','course_id','department_id','institution_id','campus_id').distinct()
        b=[]
        for i in c_inst_course:
            i['optgrou_value']=str(i['campus_id'])+'-'+str(i['institution_id'])+'-'+str(i['course_id'])
            i['depts']=[]
            for j in course_dept:
                if i['campus_id']==j['campus_id'] and i['institution_id']==j['institution_id'] and i['course_id']==j['course_id']:
                    i['depts'].append(j)
        a = {}
        a['course_dept'] = list(c_inst_course)
    return JsonResponse(a, safe=False)

@login_required
@group_required("BOSC")
def course_list(request):
    courses = Course.objects.filter(created_by_id=request.user.id).values('L', 'T', 'P', 'J', 'S', 'C', 'course_name','course_type_id',
                                                    'id', 'course_type__name','level_of_course__level','pass_fail','faculty','degree__name','admitted_batch__name',
                        'program_type__type','status_id','status__title','course_code','dept_code__dept_code').order_by('created')
    courses_users = CourseUserMapping.objects.filter(user_id=request.user.id, user_group_id=6).values('to_user_id__username', 'course_id','course__course_name','to_user_id',
                                                                                                      'to_user_group_id', 'to_user_id__first_name','to_user__email')
    campus_detail = CourseCampusMapping.objects.values('campus__name', 'course_id')
    depart_detail = CourseDepartmentMapping.objects.values('department', 'course_id')
    inst_detail = CourseInstituteMapping.objects.values('institute', 'course_id')
    l = []
    for i in courses:
        i['encrypt_id'] = encrypt(i['id'])
        for j in courses_users:
            if i['id'] == j['course_id']:
                if j['to_user_group_id'] == 2:
                    i['csmm'] = j['to_user_id__username']
                    i['csmm_name'] = j['to_user_id__first_name']
                if j['to_user_group_id'] == 3:
                    i['csmi'] = j['to_user_id__username']
                    i['csmi_name'] = j['to_user_id__first_name']

        l.append(i)
    return render(request, 'bosc/course/course_list.html', {'title': "Course List", 'courses': l,'course_status':[4,10,11]})

@login_required
@group_required("BOSC")
def course_assigned(request):
    courses_users = CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=1,is_active=1).exclude(course_status_level_id=19).values('to_user_id__username', 'course_id','course__course_name','to_user_id',
                              'to_user_group_id', 'to_user_id__first_name','to_user__email')
    courses = Course.objects.filter(id__in=courses_users.values_list('course_id')).values('L', 'T', 'P', 'J', 'S', 'C', 'course_name','course_type_id',
                        'id', 'course_type__name','level_of_course__level','pass_fail','faculty','degree__name','admitted_batch__name',
                        'program_type__type','status_id','status__title','course_code','dept_code__dept_code').order_by('created')
    
    l = []
    for i in courses:
        i['encrypt_id'] = encrypt(i['id'])
        for j in courses_users:
            if i['id'] == j['course_id']:
                if j['to_user_group_id'] == 2:
                    i['csmm'] = j['to_user_id__username']
                    i['csmm_name'] = j['to_user_id__first_name']
                if j['to_user_group_id'] == 3:
                    i['csmi'] = j['to_user_id__username']
                    i['csmi_name'] = j['to_user_id__first_name']
        l.append(i)
                
    return render(request, 'bosc/course/course_assigned.html', {'title': "Course List", 'courses': l,'course_status':[4,10,11]})

@login_required
@group_required("BOSC")
def course_unassigned(request):
    courses_users = CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=19,is_active=1).values('to_user_id__username', 'course_id','course__course_name','to_user_id',
                              'to_user_group_id', 'to_user_id__first_name','to_user__email')
    courses = Course.objects.filter(dept_code_id=request.user.dept_code_id,status_id=19).values('L', 'T', 'P', 'J', 'S', 'C', 'course_name','course_type_id',
                        'id', 'course_type__name','level_of_course__level','pass_fail','faculty','degree__name','admitted_batch__name',
                        'program_type__type','status_id','status__title','course_code','dept_code__dept_code').order_by('created')
    
    l = []
    for i in courses:
        i['encrypt_id'] = encrypt(i['id'])
        for j in courses_users:
            if i['id'] == j['course_id']:
                if j['to_user_group_id'] == 2:
                    i['csmm'] = j['to_user_id__username']
                    i['csmm_name'] = j['to_user_id__first_name']
                if j['to_user_group_id'] == 3:
                    i['csmi'] = j['to_user_id__username']
                    i['csmi_name'] = j['to_user_id__first_name']
        l.append(i)
                
    return render(request, 'bosc/course/course_unassigned.html', {'title': "Course List", 'courses': l,'course_status':[4,10,11]})

@login_required
@group_required("BOSC")
def course_approved(request):
    courses_users = CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=1,is_active=1).values('to_user_id__username', 'course_id','course__course_name','to_user_id',
                              'to_user_group_id', 'to_user_id__first_name','to_user__email')
    courses = Course.objects.filter(dept_code_id=request.user.dept_code_id,status_id=10).values('L', 'T', 'P', 'J', 'S', 'C', 'course_name','course_type_id',
                        'id', 'course_type__name','level_of_course__level','pass_fail','faculty','degree__name','admitted_batch__name',
                        'program_type__type','status_id','status__title','course_code','dept_code__dept_code').order_by('created')
    
    l = []
    for i in courses:
        i['encrypt_id'] = encrypt(i['id'])
        for j in courses_users:
            if i['id'] == j['course_id']:
                if j['to_user_group_id'] == 2:
                    i['csmm'] = j['to_user_id__username']
                    i['csmm_name'] = j['to_user_id__first_name']
                if j['to_user_group_id'] == 3:
                    i['csmi'] = j['to_user_id__username']
                    i['csmi_name'] = j['to_user_id__first_name']
        l.append(i)
                
    return render(request, 'bosc/course/course_approved.html', {'title': "Course List", 'courses': l,'course_status':[4,10,11]})

@login_required
@group_required("BOSC")
def course_pending(request):
    courses_users = CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=1,is_active=1).values('to_user_id__username', 'course_id','course__course_name','to_user_id',
                              'to_user_group_id', 'to_user_id__first_name','to_user__email')
    courses = Course.objects.filter(dept_code_id=request.user.dept_code_id,status_id=4).values('L', 'T', 'P', 'J', 'S', 'C', 'course_name','course_type_id',
                        'id', 'course_type__name','level_of_course__level','pass_fail','faculty','degree__name','admitted_batch__name',
                        'program_type__type','status_id','status__title','course_code','dept_code__dept_code').order_by('created')
    
    l = []
    for i in courses:
        i['encrypt_id'] = encrypt(i['id'])
        for j in courses_users:
            if i['id'] == j['course_id']:
                if j['to_user_group_id'] == 2:
                    i['csmm'] = j['to_user_id__username']
                    i['csmm_name'] = j['to_user_id__first_name']
                if j['to_user_group_id'] == 3:
                    i['csmi'] = j['to_user_id__username']
                    i['csmi_name'] = j['to_user_id__first_name']
        l.append(i)
                
    return render(request, 'bosc/course/course_pending.html', {'title': "Course List", 'courses': l,'course_status':[4,10,11]})


@csrf_exempt
def validate_ltpjs_dept_inst_camp(request):
    if request.method == "POST":
        courses = Course.objects.filter(id__in=request.POST.getlist('course_id')).values('L', 'T', 'P', 'J', 'S', 'C',
                                                  'course_name', 'course_type_id',
                                                  'id', 'course_type__name',
                                                  'program_type__type')

        depart_detail = CourseDepartmentMapping.objects.values('course_id').distinct()
        depins_course = []
        dept_course = depart_detail.values_list('course_id', flat=True)
        l = []
        ltpjs_course = []
        for i in courses:

            if i['course_type_id'] == 1:
                if i['P'] != '0' or i['J'] != '0' or i['S'] != '0' or i['L']+i['T']>'4':
                    ltpjs_course.append(i['course_name'])
            elif i['course_type_id'] == 2:
                if i['L'] != '0' or i['T'] != '0' or i['J'] != '0' or i['S'] != '0' or i['P'] not in ['2','4','6']:
                    ltpjs_course.append(i['course_name'])
            elif i['course_type_id'] == 3:
                if i['J'] != '0' or i['S'] != '0' or i['P'] not in ['0','2','4','6']  :
                    ltpjs_course.append(i['course_name'])
            elif i['course_type_id'] == 4:
                if i['L'] != '0' or i['T'] != '0' or i['P'] != '0' or i['S'] != '0':
                    ltpjs_course.append(i['course_name'])
            elif i['course_type_id'] == 5:
                if i['L'] != '0' or i['T'] != '0' or i['P'] != '0' or i['J'] != '0' or int(i['S'])>10:
                    ltpjs_course.append(i['course_name'])
            if i['id'] not in dept_course:
                depins_course.append(i['course_name'])
            l.append(i)
        dept_inst_course = list(set(depins_course))
        return JsonResponse({'status':200,'dept_inst_course':dept_inst_course,'ltpjs_course':ltpjs_course})
    else:
        return JsonResponse({'status': 500})


@login_required
@group_required("BOSC")
def course_upload(request):
    if request.method == 'POST':
        try:
            import xlrd
            temp_file = 'data_upload'
            handle_uploaded_file(request.FILES['data'], temp_file)
            wb = xlrd.open_workbook('media/' + temp_file + '.xlsx')
            sheet = wb.sheet_by_index(0)

            not_exists_csm = []
            exists_course = ['These Course Already Exists-->']
            error = False
            exists_course_error=False
            for i in range(1, sheet.nrows):
                d = {}
                d['course_title'] = sheet.cell_value(i, 1)
                d['course_type'] = sheet.cell_value(i, 2)
                csm_incharge_emp_id = int(sheet.cell_value(i, 12))
                csm_member_emp_id = int(sheet.cell_value(i, 13))
                if not User.objects.filter(username=csm_incharge_emp_id).exists():
                    error = True
                    d['CSMI'] = csm_incharge_emp_id
                    d['CSMI Message'] = 'CSM Incharge not exists'
                elif not User.objects.filter(username=csm_incharge_emp_id, groups__name='CSMI').exists():
                    user_csmi=User.objects.get(username=csm_incharge_emp_id)
                    UserGroups.objects.create(user_id=user_csmi.id, group_id=3, is_active=0, is_block=0,is_default=0, role='CSMI')

                if not User.objects.filter(username=csm_member_emp_id).exists():
                    error = True
                    d['CSMC'] = csm_member_emp_id
                    d['CSMC Message'] = 'CSM Member not exists'
                elif not User.objects.filter(username=csm_member_emp_id, groups__name='CSMC').exists():
                    user_csmc=User.objects.get(username=csm_member_emp_id)
                    UserGroups.objects.create(user_id=user_csmc.id, group_id=2, is_active=0, is_block=0,is_default=0, role='CSMM')

                if Course.objects.filter(course_name=sheet.cell_value(i, 1)).exists():
                    exists_course_error = True
                    exists_course.append(sheet.cell_value(i, 1))
                if not sheet.cell_value(i, 10) in ['Y','N']:
                    messages.error(request, 'Pass/Fail should be Y/N')
                    return redirect('course_list')
                if not sheet.cell_value(i, 11) in ['Y', 'N']:
                    messages.error(request, 'Faculty should be Y/N')
                    return redirect('course_list')
                if not CourseAdmittedBatch.objects.filter(status=1,name=sheet.cell_value(i, 14)).exists():
                    messages.error(request, 'Enter valid Admitted Batch '+str(sheet.cell_value(i, 14)))
                    return redirect('course_list')
                not_exists_csm.append(d)

            if exists_course_error is True:
                messages.error(request, exists_course)
                return redirect('course_list')
            if error is True:
                messages.error(request, not_exists_csm)
                return redirect('course_list')
            else:
                for i in range(1, sheet.nrows):
                    course_name = sheet.cell_value(i, 1)
                    l = int(sheet.cell_value(i, 4))
                    t = int(sheet.cell_value(i, 5))
                    p = int(sheet.cell_value(i, 6))
                    s = int(sheet.cell_value(i, 7))
                    j = int(sheet.cell_value(i, 8))
                    c = int(sheet.cell_value(i, 9))
                    if sheet.cell_value(i, 10) == 'Y':
                        pass_fail=1
                    elif sheet.cell_value(i, 10) == 'N':
                        pass_fail=0
                    if sheet.cell_value(i, 11) == 'Y':
                        faculty=1
                    elif sheet.cell_value(i, 11) == 'N':
                        faculty=0
                    course_type = CourseType.objects.get(code=sheet.cell_value(i, 2), status=1).id
                    program_type = ProgramType.objects.get(code=sheet.cell_value(i, 3), status=1).id
                    admitted_batch_id = CourseAdmittedBatch.objects.get(name=sheet.cell_value(i, 14), status=1).id
                    dept_details=DepartmentInstituteCodes.objects.get(id=request.user.dept_code_id)
                    insert = Course.objects.create(course_name=course_name, L=l, T=t, P=p, J=j, S=s, C=c,
                           course_type_id=course_type, created_by_id=request.user.id,pass_fail=pass_fail,
                           dept_code_id=request.user.dept_code_id, program_type_id=program_type,faculty=faculty,
                           admitted_batch_id=admitted_batch_id,status_id=19,
                           course_code=str(dept_details.dept_code)+'XXXX')

                    # csm_member
                    csm_member_emp_id = int(sheet.cell_value(i, 13))
                    csm_member = User.objects.get(username=csm_member_emp_id, groups__name='CSMC').id
                    CourseUserMapping.objects.create(is_edit=2, course_id=insert.id, course_status_level_id=19,
                                                     to_user_id=csm_member, to_user_group_id=2,
                                                     user_id=request.user.id, user_group_id=6)

                    # csm_incharge
                    csm_incharge_emp_id = int(sheet.cell_value(i, 12))
                    csm_incharge = User.objects.get(username=csm_incharge_emp_id, groups__name='CSMI').id
                    CourseUserMapping.objects.create(is_edit=2, course_id=insert.id, course_status_level_id=19,
                                                     to_user_id=csm_incharge, to_user_group_id=3,
                                                     user_id=request.user.id, user_group_id=6)

                messages.success(request, 'Data Stored Successfully')
                return redirect('course_list')
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_list')
    else:
        return redirect('course_list')


@login_required
@group_required('BOSC')
def course_edit(request, course_id):
    course_id = decrypt(course_id)
    if Course.objects.filter(created_by=request.user.id).exists():
        course_details = Course.objects.get(id=course_id)
        course_type = CourseType.objects.filter(status=1).values('id', 'name')
        program_type = ProgramType.objects.filter(status=1).values('id', 'type')
        course_degree = CourseDegree.objects.filter(status=1).values('id', 'name')
        course_admitted_batch = CourseAdmittedBatch.objects.filter(status=1).values('id', 'name')
        csmi = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=3, is_active=1,
                course_status_level_id__in=[1, 13,19]).values('to_user_id','to_user__username',
                'to_user__first_name','to_user__email')
        csmc = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=2, is_active=1).values(
            'to_user_id', 'to_user__username', 'to_user__first_name',
            'to_user__email')
        campus_det = Campus.objects.values('id', 'name','campus_code')
        campus_institutions = CampusInstitutionMapping.objects.values('id','institution_id','institution__institution_code','campus__campus_code','campus_id')
        c_dept_mapping=CourseDepartmentMapping.objects.filter(course_id=course_id)
        c_campus_inst=c_dept_mapping.values('c_i_c_d_id__campus_id','c_i_c_d_id__institution_id')
        for i in campus_det:
            i['insts']=[]
            for j in campus_institutions:
                if i['id']==j['campus_id']:
                    j['is_seleted']=False
                    for k in c_campus_inst:
                        if j['campus_id']==k['c_i_c_d_id__campus_id'] and j['institution_id']==k['c_i_c_d_id__institution_id']:
                            j['is_seleted']=True
                    i['insts'].append(j)
        
        c_inst_course =CampusInstitutionCourseMapping.objects.filter(campus_id__in=c_campus_inst.values_list('c_i_c_d_id__campus_id'),
            institution_id__in=c_campus_inst.values_list('c_i_c_d_id__institution_id')).values('institution_id','campus_id','campus__name',
            'course__name','course_id','institution__institution_code').distinct()
        course_dept=CampusInstitutionCourseDepartmentMapping.objects.filter(campus_id__in=c_campus_inst.values_list('c_i_c_d_id__campus_id'),
                   institution_id__in=c_campus_inst.values_list('c_i_c_d_id__institution_id')).values('course__name','department__dept_code',
                   'id','course_id','department_id','institution_id','campus_id').distinct()
        selected_depts=list(c_dept_mapping.values_list('c_i_c_d_id',flat=True))
        for i in c_inst_course:
            #i['label_name']=
            i['depts']=[]
            i['optgrou_value']=str(i['campus_id'])+'-'+str(i['institution_id'])+'-'+str(i['course_id'])
            for j in course_dept:
                if i['campus_id']==j['campus_id'] and i['institution_id']==j['institution_id'] and i['course_id']==j['course_id']:
                    j['is_seleted']=False
                    if j['id'] in selected_depts:
                        j['is_seleted']=True
                    i['depts'].append(j)
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
                    C = int(L) + int(T)
                elif request.POST['type_of_course'] == '2':
                    P = int(request.POST['P'])
                    C = int(P) * 0.5
                elif request.POST['type_of_course'] == '3':
                    L = int(request.POST['L'])
                    T = int(request.POST['T'])
                    P = int(request.POST['P'])
                    C = int(L) + int(T) + (int(P) * 0.5)
                elif request.POST['type_of_course'] == '4':
                    J = int(request.POST['J'])
                    C = int(request.POST['C'])
                elif request.POST['type_of_course'] == '5':
                    S = int(request.POST['S'])
                    C = S
                elif request.POST['type_of_course'] == '6':
                    L = int(request.POST['L'])
                    T = int(request.POST['T'])
                    P = int(request.POST['P'])
                    J = int(request.POST['J'])
                    S = int(request.POST['S'])
                    C = 0

                campus_get = request.POST.getlist('campus')
                course_dept = request.POST.getlist('course_dept')
                
                if Course.objects.filter(id=course_id).exists():
                    Course.objects.filter(id=course_id).update(course_name=request.POST['course_title'],
                           course_type_id=request.POST['type_of_course'],
                           program_type_id=request.POST['program_type'],
                           L=L, T=T, P=P, S=S, J=J, C=int(C),
                           total_no_of_contact_hours=int(C) * 15,pass_fail=request.POST['pass_fail'],
                           modified=datetime.now(), modified_by_id=request.user.id,faculty=request.POST['faculty'],
                           admitted_batch_id=request.POST['admitted_batch'])

                    try:
                        csmi_id = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=3, is_active=1,
                                                               to_user_id=request.POST.get('csmi_old')).values('course_status_level_id', 'to_user_id')
                    except Exception as e:
                        csmi_id = None
                    if csmi_id:
                        
                        csmi_id = csmi_id.last()
                        if not csmi_id['to_user_id'] == int(request.POST.get('csmi')):
                            CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=3, is_active=1,
                                                             to_user_id=csmi_id['to_user_id']).update(is_active=0,
                                                                                                      is_edit=2)

                            CourseUserMapping.objects.create(created=datetime.now, is_edit=2,
                                                             course_id=course_id, course_status_level_id=csmi_id['course_status_level_id'],
                                                             to_user_id=request.POST.get('csmi'),
                                                             user_id=request.user.id,
                                                             to_user_group_id=3, user_group_id=6)

                            if not UserGroups.objects.filter(user_id=request.POST.get('csmi'), group_id=3).exists():
                                UserGroups.objects.create(user_id=request.POST.get('csmi'), group_id=3, is_active=0,
                                                          is_block=0, is_default=0, role='CSMI')

                    else:
                        CourseUserMapping.objects.create(created=datetime.now, is_edit=2,
                                                             course_id=course_id, course_status_level_id=13,
                                                             to_user_id=request.POST.get('csmi'),
                                                             user_id=request.user.id,
                                                             to_user_group_id=3, user_group_id=6
                                                         )
                        if not UserGroups.objects.filter(user_id=request.POST.get('csmc'), group_id=2).exists():
                            UserGroups.objects.create(user_id=request.POST.get('csmi'), group_id=3, is_active=0,
                                                          is_block=0, is_default=0, role='CSMI')
                    
                    try:
                        csmc_id = CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=2, is_active=1,
                                                                   to_user_id=request.POST.get('csmc_old')).values('course_status_level_id', 'to_user_id')
                    except Exception as e:
                        csmc_id = None
                    if csmc_id:
                        csmc_id = csmc_id.last()
                        if not csmc_id['to_user_id'] == int(request.POST.get('csmc')):
                            CourseUserMapping.objects.filter(course_id=course_id, to_user_group_id=2,
                                                             to_user_id=csmc_id['to_user_id'], is_active=1).update(
                                is_active=0, is_edit=2)
                            CourseUserMapping.objects.create(created=datetime.now, is_edit=2,
                                                             course_id=course_id, course_status_level_id=csmc_id['course_status_level_id'],
                                                             to_user_id=request.POST.get('csmc'),
                                                             user_id=request.user.id,
                                                             to_user_group_id=2, user_group_id=6)
                        if not UserGroups.objects.filter(user_id=request.POST.get('csmc'), group_id=2).exists():
                            UserGroups.objects.create(user_id=request.POST.get('csmc'), group_id=2, is_active=0,
                                                      is_block=0,
                                                      is_default=0, role='CSMM')
                    else:
                        CourseUserMapping.objects.create(created=datetime.now, is_edit=2,
                                                         course_id=course_id, course_status_level_id=13,
                                                         to_user_id=request.POST.get('csmc'), user_id=request.user.id,
                                                         to_user_group_id=2, user_group_id=6,
                                                         )
                        if not UserGroups.objects.filter(user_id=request.POST.get('csmc'), group_id=2).exists():
                            UserGroups.objects.create(user_id=request.POST.get('csmc'), group_id=2, is_active=0,
                                                      is_block=0,
                                                      is_default=0, role='CSMM')
                    CourseDepartmentMapping.objects.filter(course_id=course_id).delete()
                    for j in course_dept:
                        CourseDepartmentMapping.objects.create(department=None, course_id=course_id,
                                    created=datetime.now(),user_id=request.user.id,c_i_c_d_id=int(j))
                    messages.success(request, 'Updated successful')

                    return redirect('/bosc/course_list')
            except Exception as e:
                messages.error(request, str(e))
                ErrorLogs.objects.create(log=str(e) + '--Course Edit', info=request.POST, user_id=request.user.id)
                response = {'status': 500, 'error': str(e), 'project': 'project'}
                return render(request, 'bosc/course/course_edit.html',
                              {'course_type': course_type, 'program_type': program_type,
                               'course_details': course_details, 'course_id': encrypt(course_id),
                               'campus_det': campus_det,'c_inst_course':c_inst_course,
                               'course_admitted_batch':course_admitted_batch}
                              )
        context = {'course_type': course_type, 'program_type': program_type,
                   'course_details': course_details, 'p_id': encrypt(course_details.program_id),
                   'course_id': encrypt(course_id), 'csmi': csmi, 'csmc': csmc,'campus_det':campus_det,'c_inst_course':c_inst_course,
                   'pre_url': request.META.get('HTTP_REFERER'),'course_admitted_batch':course_admitted_batch}
        return render(request, 'bosc/course/course_edit.html', context)
    else:
        ErrorLogs.objects.create(log='Not Authorised Access --Course Edit', user_id=request.user.id)
        return redirect('/')


@login_required
@group_required('BOSC')
def course_del(request):
    if request.method == "POST":
        try:
            course = decrypt(request.POST['course_del'])
            Course.objects.filter(id=course).delete()
            messages.success(request, "Deleted Successfully..")
            return redirect('/bosc/course_list')
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            return redirect('/bosc/course_list')
    else:
        return redirect('/')


@login_required
@group_required("BOSC")
def add_course(request):
    course_type = CourseType.objects.filter(status=1).values('id', 'name')
    program_type = ProgramType.objects.filter(status=1).values('id', 'type')
    course_degree = CourseDegree.objects.filter(status=1).values('id', 'name')
    course_admitted_batch= CourseAdmittedBatch.objects.filter(status=1).values('id', 'name')

    user_di = User.objects.values('dept_code__dept_code', 'institution', 'campus').distinct()
    dept = set([j['dept_code__dept_code'] for j in user_di if j['dept_code__dept_code'] != None])
    inst = list(set([j['institution'] for j in user_di if j['institution'] != None]))
    campus_det = Campus.objects.values('id', 'name','campus_code')
    campus_institutions = CampusInstitutionMapping.objects.values('id','institution__id','institution__institution_code','campus__campus_code','campus_id')
    #campus_institutions_mapping=[]
    for i in campus_det:
        i['insts']=[]
        for j in campus_institutions:
            if i['id']==j['campus_id']:
                i['insts'].append(j)
        
    if request.method == 'POST':
        try:
            campus = request.POST.getlist('campus')
            course_dept = request.POST.getlist('course_dept')
            #inst = request.POST.getlist('inst')

            L = 0
            T = 0
            P = 0
            S = 0
            J = 0
            C = 0
            if request.POST['type_of_course'] == '1':
                L = request.POST['L']
                T = request.POST['T']
                C = int(L) + int(T)
            elif request.POST['type_of_course'] == '2':
                P = request.POST['P']
                C = int(P) * 0.5
            elif request.POST['type_of_course'] == '3':
                L = request.POST['L']
                T = request.POST['T']
                P = request.POST['P']
                C = int(L) + int(T) + (int(P) * 0.5)
            elif request.POST['type_of_course'] == '4':
                J = int(request.POST['J'])
                C = int(request.POST['C'])
            elif request.POST['type_of_course'] == '5':
                S = request.POST['S']
                C = int(S)
            elif request.POST['type_of_course'] == '6':
                L = request.POST['L']
                T = request.POST['T']
                P = request.POST['P']
                S = request.POST['S']
                J = request.POST['J']
                C = 0
            # if request.POST['pass_fail'] == '1':
            #     L = request.POST['L']
            #     T = request.POST['T']
            #     P = request.POST['P']
            #     S = request.POST['S']
            #     J = request.POST['J']
            #     C = 0
            dept_details=DepartmentInstituteCodes.objects.get(id=request.user.dept_code_id)
                    
            insert = Course.objects.create(course_name=request.POST['course_title'],
                                           course_type_id=request.POST['type_of_course'],
                                           dept_code_id=request.user.dept_code_id,
                                           program_type_id=request.POST['program_type'],
                                           L=L, T=T, P=P, S=S, J=J, C=int(C),status_id=19,
                                           total_no_of_contact_hours=int(C) * 15,pass_fail=request.POST['pass_fail'],
                                           created=datetime.now(), created_by_id=request.user.id,faculty=request.POST['faculty'],
                                            admitted_batch_id=request.POST['admitted_batch'],degree_id=None,
                                            course_code=str(dept_details.dept_code)+'XXXX'
                                            )

            '''for i in range(len(dept)):
                CourseDepartmentMapping.objects.create(department=dept[i], course_id=insert.id,
                                                       created=datetime.now(), user_id=request.user.id)
            for k in range(len(inst)):
                CourseInstituteMapping.objects.create(institute=inst[k], course_id=insert.id,
                                                      created=datetime.now(), user_id=request.user.id)
            for j in range(len(campus)):
                CourseCampusMapping.objects.create(campus_id=campus[j], course_id=insert.id,
                                                    created=datetime.now(), user_id=request.user.id)'''
            for j in course_dept:
                CourseDepartmentMapping.objects.create(department=None, course_id=insert.id,
                   created=datetime.now(), user_id=request.user.id,c_i_c_d_id=int(j))
            
            # csm_member

            CourseUserMapping.objects.create(is_edit=2, course_id=insert.id, course_status_level_id=19,
                                             to_user_id=request.POST['csmc'], to_user_group_id=2,
                                             user_id=request.user.id, user_group_id=6)

            # csm_incharge

            CourseUserMapping.objects.create(is_edit=2, course_id=insert.id, course_status_level_id=19,
                                             to_user_id=request.POST['csmi'], to_user_group_id=3,
                                             user_id=request.user.id, user_group_id=6)

            messages.success(request, "Created Successfully..")
            return redirect('/bosc/course_list')
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e) + '--Course Create', info=request.POST, user_id=request.user.id)
            return render(request, 'bosc/course/add_course.html',
                          {'course_type': course_type, 'program_type': program_type,'campus':campus,
                          'course_dept':course_dept,'campus_det': campus_det})
    return render(request, 'bosc/course/add_course.html',
                  {'course_type': course_type, 'program_type': program_type, 'dept': dept,
                   'inst': inst, 'campus_det': campus_det,'course_degree':course_degree,'course_admitted_batch':course_admitted_batch})


@login_required
@group_required("BOSC")
def bosc_course_final_submit(request):
    courses_users = CourseUserMapping.objects.filter(user_id=request.user.id, user_group_id=6).values(
                                                                                    'to_user_id__username', 'course_id', 'course__course_name', 'to_user_id',
                                                                                    'to_user_group_id', 'to_user_id__first_name',
                                                                                    'to_user__email')
    if request.method == "POST":
        course_ids=request.POST.getlist('course_id')
        CourseUserMapping.objects.filter(user_id=request.user.id, user_group_id=6,to_user_group_id=2,course_id__in=course_ids).update(assigned_time=datetime.now(),is_edit=1,course_status_level_id=1)
        CourseUserMapping.objects.filter(user_id=request.user.id, user_group_id=6,to_user_group_id=3,course_id__in=course_ids).update(assigned_time=datetime.now(),is_edit=0,course_status_level_id=1)
        Course.objects.filter(id__in=course_ids).update(status_id=1)
        sender = settings.EMAIL_HOST_USER
        for i in courses_users:
            members=courses_users.filter(course_id=i['course_id']).values('to_user_group_id', 'to_user_id__first_name',)
            email = i['to_user__email']
            current_site = get_current_site(request)
            mail_subject = "Assigned as a team member for the Course Syllabus Modification committee for " + i['course__course_name'] + "."
            message = render_to_string('bosc/email_templates/course_assign_email.html', {
                'members':members,
                'domain': current_site.domain,
                'guest_firstname': i['to_user_id__first_name'],
                'course_name': i['course__course_name'],

            })
            e = send_html_mail(mail_subject, message, [email], sender)
            EmailStatus.objects.create(hint='BOSC Course Final Submit', message=message, to_user_email=email, to_user_id=i['to_user_id'], user_id=request.user.id)
        messages.success(request, "Submitted Successfully..")
        return redirect(request.POST['rerurn_url'])
    else:
        return redirect('/')

@login_required
@group_required('BOSC')
def course_preview(request, course_id):
    course_id = decrypt(course_id)
    if Course.objects.filter(id=course_id,dept_code_id=request.user.dept_code_id).exists():
        course_details = Course.objects.get(id=course_id)
        dept = DepartmentInstituteCodes.objects.values('id', 'dept_inst')
        course_type = CourseType.objects.values('id', 'name')
        level_of_course = ProgramLevel.objects.filter(status=1).values('id', 'level')
        course_category = CourseCategory.objects.values('id', 'category')
        course_syllabus = get_syllabus(request, course_id)
        course_book_details = get_course_book_details(request, course_id)
        references_details = get_ref_details(request, course_id)
        journal_details = get_journal_details(request, course_id)
        website_details = get_website_details(request, course_id)
        course = Course.objects.filter(id=course_id).values()
        course_outcome = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
        pedagogy_tools = PedagogyTools.objects.values('id', 'name')
        practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values('topic','syllabus_type__name').order_by('id')
        course_owner = CourseUserMapping.objects.filter(is_active=1, to_user_group_id=2, course_id=course_id).values(
            'to_user__first_name', 'to_user__username', 'to_user__dept_code_id', 'to_user__designation',
            'to_user__dept_code__dept_inst').last()

        course_pre_requisite = CoursePrerequestiesMapping.objects.filter(course_id=course_id).values('id',
                                                                                                     'prerequesti__course_name')
        course_timeline = []
        course_timeline_actions = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                                                                                               'user__first_name',
                                                                                               'user_id',
                                                                                               'course_status_level__title',
                                                                                               'to_user__first_name',
                                                                                               'to_user_group__description',
                                                                                               'user_group__description',
                                                                                               'user__image',
                                                                                               'comment').order_by(
            '-id')

        pending_timeline = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id',
                                                                                        'course_status_level__title',
                                                                                        'to_user__first_name',
                                                                                        'to_user_group__description',
                                                                                        'user_group__description',
                                                                                        'to_user__image',
                                                                                        'comment').last()
        course_timeline.append(pending_timeline)
        course_timeline.extend(course_timeline_actions)
        if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=6, is_edit=1,
                                            course_status_level_id__in=[5, 18,4], to_user_id=request.user.id).exists():
            is_edit = 1
        else:
            is_edit = 0


        context = {'course_id': encrypt(course_details.id), 'dept': dept, 'practical_syllabus': practical_syllabus,
                   'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
                   'course_details': course_details, 'active_step': course_details.active_step,
                   'course_syllabus': course_syllabus, 'p_id': encrypt(course_details.program_id),
                   'course_book_details': course_book_details, 'references_details': references_details,
                   'course': course,
                   'course_outcome': course_outcome, 'is_edit': is_edit,
                   'course_timeline': course_timeline,'course_pre_requisite':course_pre_requisite,
                   'course_owner': course_owner,
                   'pedagogy_tools': pedagogy_tools, 'course_edit': course_edit, 'journal_details': journal_details,
                   'website_details': website_details}
        return render(request, 'bosc/course/course_preview.html', context)
        #return render(request, 'bosc/preview.html', context)
    return redirect('/')        
    
 
@login_required
@group_required("BOSC")
def course_need_more(request, c_id):
    c_id = decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,course_status_level_id__in=[5, 18,4]).exists():
                csmi_user = CourseUserMapping.objects.filter(course_id=c_id,user_group_id=3).values('user_id').last()
                CourseUserMapping.objects.create(course_id=c_id, to_user_id=csmi_user['user_id'],
                                                 user_id=request.user.id, course_status_level_id=11,
                                                 comment=request.POST.get('bosc_message'), is_edit=1,
                                                 to_user_group_id=3, user_group_id=6
                                                 )
                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id).update(is_edit=0)
                Course.objects.filter(id=c_id).update(status_id=11)
            messages.success(request, 'Forwarded Successfully..')
            return redirect(request.POST['return_url'])
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect(request.POST['return_url'])
    return redirect('/bosc')


@login_required
@group_required("BOSC")
def course_approve(request, c_id):
    c_id = decrypt(c_id)
    if request.method == 'POST' and Course.objects.filter(id=c_id,dept_code_id=request.user.dept_code_id).exists():
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,is_edit=1).exists():
                to_user = BoschairInstituteMapping.objects.filter(dept_code_id=request.user.dept_code_id).values()
                if not to_user:
                    ErrorLogs.objects.create(log='bos not found', user_id=request.user.id)
                    messages.error(request, 'BOS Chair not assigned')
                    return redirect(request.POST['return_url'])
                CourseUserMapping.objects.create(course_id=c_id, to_user_id=to_user[0]['bos_chair_id'],
                         user_id=request.user.id, course_status_level_id=10, is_edit=1,
                         course_header_id=course.course_header_id, to_user_group_id=7,
                                                 user_group_id=6)

                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                 course_status_level_id__in=[5, 18,4]).update(is_edit=0)
                Course.objects.filter(id=c_id).update(status_id=10)
            messages.success(request, "Approved.....")
            return redirect('/bosc/course_preview/' + encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('/bosc/course_preview/' + encrypt(c_id))
    return redirect('/bosc')
 