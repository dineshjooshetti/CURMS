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
@group_required('BOSC')
def index(request):

    programs = Programs.objects.filter(user_id=request.user.id).count()
    pab = User.objects.filter(is_superuser=0, usergroups__group_id__in=[9], dept_code_id=request.user.dept_code_id).count()
    courses = Course.objects.filter(dept_code_id=request.user.dept_code_id).count()
    csmm_pending=CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=1,is_edit=1).values('course_id').distinct().count()
    csmm_completd=CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=2).values('course_id').distinct().count()
    csmi_pending=CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id__in=[2,11],is_edit=1).values('course_id').distinct().count()
    csmi_completd=CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=4,is_edit=0).values('course_id').distinct().count()
    bosc_pending=CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=4,is_edit=1).values('course_id').distinct().count()
    bosc_completd=CourseUserMapping.objects.filter(course__dept_code_id=request.user.dept_code_id,course_status_level_id=10).values('course_id').distinct().count()
    bosc_assigned=csmm_pending+csmm_completd
    bosc_unassigned=courses-bosc_assigned
    
    context={'programs': programs,'pab':pab,'courses':courses,'csmm_pending':csmm_pending,
            'csmm_completd':csmm_completd,'csmi_pending':csmi_pending,'csmi_completd':csmi_completd,
            'bosc_pending':bosc_pending,'bosc_completd':bosc_completd,'bosc_assigned':bosc_assigned,
            'bosc_unassigned':bosc_unassigned
    }            
    return render(request, 'bosc/index.html', context)

@login_required
@group_required('BOSC')
def programme(request):
    programs = Programs.objects.filter(user_id=request.user.id).values('name', 'program_type__type', 'id','program_category__name').order_by('-created')
    program = []
    for i in programs:
        status = ProgramUserMapping.objects.filter(program_id=i['id']).values('program_status_level__title',
                                                            'program_status_level_id').exclude(program_status_level_id__in=[8, 9]).last()
        i['program_status'] = status['program_status_level__title']
        i['program_status_id'] = status['program_status_level_id']
        i['encrypt_id'] = encrypt(i['id'])
        program.append(i)
    return render(request, 'bosc/program_list.html', {'programs': program})

@login_required
@group_required('BOSC')
def create_program(request):
    #Programs.objects.filter().delete()
    campus = Campus.objects.filter(status=1).values('name', 'address', 'id')
    ptype = ProgramType.objects.values('type', 'id', 'status')
    plevel = ProgramLevel.objects.filter(status=1).values('level')
    categories = ProgramCategory.objects.filter(status=1).values('id','name')
    context = {'campus': campus, 'ptype': ptype, 'plevel': plevel,'categories':categories}
    if request.method == "POST":
        try:
            insert = Programs.objects.create(name=request.POST.get('p_name'), created=datetime.now(),
                                             program_type_id=request.POST.get('p_type'), user_id=request.user.id,
                                             department=request.user.department)
            p_level = request.POST.getlist('p_level')
            for v in range(len(p_level)):
                ProgramLevelMapping.objects.create(level_id=p_level[v], program_id=insert.id, created=datetime.now())

            campus = request.POST.getlist('campus')
            for c in range(len(campus)):
                ProgramCampusMapping.objects.create(campus_id=campus[c], program_id=insert.id, created=datetime.now())

            for c in request.POST.getlist('inst'):
                ProgramInstituteMapping.objects.create(institute=c, program_id=insert.id, created=datetime.now(),user_id=request.user.id)


            for c in request.POST.getlist('dept'):
                ProgramDepartmentMapping.objects.create(department=c, program_id=insert.id,created=datetime.now(),user_id=request.user.id)

            user_group = UserGroups.objects.filter(user_id=request.user.id, is_active=1, is_block=0).values('group_id')
            pcm = request.POST.getlist('pcmc')
            pcm.insert(0, request.POST.get('pcmi'))
            members = User.objects.filter(id__in=pcm).values('id', 'first_name')
            pcm_list = [i['first_name'] for j in pcm for i in members if int(j) == i['id']]

            if not UserGroups.objects.filter(user_id=request.POST.get('pcmi'), group_id=5).exists():
                add_group = UserGroups.objects.create(user_id=request.POST.get('pcmi'), group_id=5, is_active=0,
                                                      is_block=0,
                                                      is_default=0, role='PCMI')
                ProgramUserMapping.objects.create(program_id=insert.id, user_id=request.user.id,
                                                  to_user_id=request.POST.get('pcmi')
                                                  , created=datetime.now(), program_status_level_id=1, is_edit=1,
                                                  to_user_group_id=5,
                                                  user_group_id=6)
            else:
                ProgramUserMapping.objects.create(program_id=insert.id, user_id=request.user.id,
                                                  to_user_id=request.POST.get('pcmi'), created=datetime.now(),
                                                  program_status_level_id=1, is_edit=1, to_user_group_id=5,
                                                  user_group_id=6)

            email = User.objects.filter(id=request.POST.get('pcmi')).values('email', 'id', 'first_name')
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Team member for the Programme Curriculum Modification committee for " + request.POST.get(
                'p_name')
            message = render_to_string('bosc/email_templates/create_program_email.html', {
                'email': encrypt(email[0]['email']),
                'domain': current_site.domain,
                'guest_firstname': email[0]['first_name'],
                'program': request.POST.get('p_name'),
                'members': pcm_list
            })
            #e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            EmailStatus.objects.create(hint="BOSC Create Program", message=message, to_user_email=email[0]['email'], to_user_id=email[0]['id'], user_id=request.user.id)
            pcmc = request.POST.getlist('pcmc')
            for l in range(len(pcmc)):
                if not UserGroups.objects.filter(user_id=pcmc[l], group_id=4).exists():
                    ad_group = UserGroups.objects.create(user_id=pcmc[l], group_id=4, is_active=0, is_block=0,
                                                         is_default=0, role='PCMM')
                    ProgramUserMapping.objects.create(program_id=insert.id, user_id=request.user.id, to_user_id=pcmc[l],
                                                      created=datetime.now(), program_status_level_id=1, is_edit=0,
                                                      to_user_group_id=4
                                                      , user_group_id=6)
                else:
                    ProgramUserMapping.objects.create(program_id=insert.id, user_id=request.user.id, to_user_id=pcmc[l],
                                                      created=datetime.now(), program_status_level_id=1, is_edit=0,
                                                      to_user_group_id=4, user_group_id=6)
                email = User.objects.filter(id=pcmc[l]).values('email', 'id', 'first_name')
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Team member for the Programme Curriculum Modification committee for " + request.POST.get(
                    'p_name')
                message = render_to_string('bosc/email_templates/create_program_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'program': request.POST.get('p_name'),
                    'members': pcm_list
                })
                #e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
                EmailStatus.objects.create(hint="BOSC Create Program", message=message, to_user_email=email[0]['email'],to_user_id=email[0]['id'], user_id=request.user.id)

            messages.success(request, "Program created successfully ")
            return redirect('/bosc')
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST, user_id=request.user.id)
            return render(request, 'bosc/create_program.html', context)
    return render(request, 'bosc/create_program.html', context)


@login_required
@group_required('BOSC')
def program_edit(request, program_id):
    program_id = decrypt(program_id)
    campus = Campus.objects.filter(status=1).values('name', 'address', 'id')
    ptype = ProgramType.objects.filter(status=1).values('type', 'id', 'status')
    program = Programs.objects.get(id=program_id)
    plevel = ProgramLevel.objects.filter(status=1, program_type_id=program.program_type_id).values('level', 'id')
    p_levels = ProgramLevelMapping.objects.filter(program_id=program_id).values('level_id', 'program_id')
    p_campus = ProgramCampusMapping.objects.filter(program_id=program_id).values('campus_id', 'program_id')
    categories = ProgramCategory.objects.filter(status=1).values('id', 'name')
    user_di = User.objects.values('dept_code__dept_code', 'institution').distinct()

    dept = list(set([j['dept_code__dept_code'] for j in user_di if j['dept_code__dept_code'] != None]))
    inst = list(set([j['institution'] for j in user_di if j['institution'] != None]))
    dept_det = ProgramDepartmentMapping.objects.filter(program_id=program_id).values('department')
    inst_det = ProgramInstituteMapping.objects.filter(program_id=program_id).values('institute')


    pcmi = ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=5, is_active=1,
                                             program_status_level_id__in=[1, 10]).values('to_user_id',
                                                                                         'to_user__username',
                                                                                         'to_user__first_name',
                                                                                         'to_user__email').last()
    pcmc = ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=4, is_active=1).values(
        'to_user_id', 'to_user__username', 'to_user__first_name', 'to_user__email')
    program_edit = True
    if ProgramUserMapping.objects.filter(program_id=program_id, program_status_level_id=3).exists():
        program_edit = False

    if request.method == "POST":
        try:
            Programs.objects.filter(id=program_id).update(name=request.POST.get('p_name'), modified=datetime.now(),
                                                          modified_by_id=request.user.id,
                                                          program_type_id=request.POST.get('p_type'))
            ProgramLevelMapping.objects.filter(program_id=program_id).delete()
            p_level = request.POST.getlist('p_level')
            for v in range(len(p_level)):
                ProgramLevelMapping.objects.create(level_id=p_level[v], program_id=program_id, created=datetime.now())
            campus = request.POST.getlist('campus')
            ProgramCampusMapping.objects.filter(program_id=program_id).delete()
            for c in range(len(campus)):
                ProgramCampusMapping.objects.create(campus_id=campus[c], program_id=program_id, created=datetime.now())

            ProgramInstituteMapping.objects.filter(program_id=program_id).delete()
            for c in request.POST.getlist('inst'):
                ProgramInstituteMapping.objects.create(institute=c, program_id=program_id, created=datetime.now(),user_id=request.user.id)

            ProgramDepartmentMapping.objects.filter(program_id=program_id).delete()
            for c in request.POST.getlist('dept'):
                ProgramDepartmentMapping.objects.create(department=c, program_id=program_id,created=datetime.now(),user_id=request.user.id)

            pcmi = ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=5, is_active=1,
                                                     to_user_id=request.POST.get('pcmi_old')).values(
                'program_status_level_id', 'to_user_id').last()
            if not pcmi['to_user_id'] == int(request.POST.get('pcmi')):
                if ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=5, is_active=1,
                                                     to_user_id=request.POST.get('pcmi_old')).exists():
                    ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=5, is_active=1,
                                                      to_user_id=request.POST.get('pcmi_old')).update(is_active=0,
                                                                                                      is_edit=0)
                if not UserGroups.objects.filter(user_id=request.POST.get('pcmi'), group_id=5).exists():
                    ad_group = UserGroups.objects.create(user_id=request.POST.get('pcmi'), group_id=5, is_active=0,
                                                         is_block=0, is_default=0, role='PCMI')

                ProgramUserMapping.objects.create(program_id=program_id, user_id=request.user.id,
                                                  to_user_id=request.POST.get('pcmi'), created=datetime.now(),
                                                  program_status_level_id=10, is_edit=1, to_user_group_id=5,
                                                  user_group_id=6, is_active=1)
                ProgramUserMapping.objects.create(program_id=program_id, user_id=request.user.id,
                                                  to_user_id=request.POST.get('pcmi'), created=datetime.now(),
                                                  program_status_level_id=pcmi['program_status_level_id'], is_edit=1,
                                                  to_user_group_id=5, user_group_id=6)
            pcmc_id = ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=4, is_active=1).values(
                'to_user_id', 'program_status_level_id')

            pcmc = request.POST.getlist('pcmc')
            for l in range(len(pcmc)):
                if not ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=4, is_active=1,
                                                         to_user_id=int(pcmc[l])).values('to_user_id',
                                                                                         'program_status_level_id').exists():
                    if not UserGroups.objects.filter(user_id=pcmc[l], group_id=4).exists():
                        ad_group = UserGroups.objects.create(user_id=pcmc[l], group_id=4, is_active=0, is_block=0,
                                                             is_default=0, role='PCMM')
                    ProgramUserMapping.objects.create(program_id=program_id, user_id=request.user.id,
                                                      to_user_id=pcmc[l],
                                                      created=datetime.now(), program_status_level_id=10, is_edit=0,
                                                      to_user_group_id=4, user_group_id=6)

            for j in pcmc_id:
                if not str(j['to_user_id']) in request.POST.getlist('pcmc'):
                    if ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=4,
                                                         to_user_id=j['to_user_id'], is_active=1).exists():
                        ProgramUserMapping.objects.filter(program_id=program_id, to_user_group_id=4,
                                                          to_user_id=j['to_user_id'],
                                                          is_active=1).update(is_active=0, is_edit=0)

            messages.success(request, 'Updated Successfully')
            return redirect('/bosc/program_edit/' + encrypt(program_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e) + '-- Programme Edit', info=request.POST, user_id=request.user.id)
            return redirect('/bosc/program_edit/' + encrypt(program_id))

    context = {'program': program, 'ptype': ptype, 'plevel': plevel, 'p_levels': p_levels, 'p_campus': p_campus,
               'campus': campus, 'program_id': encrypt(program_id),'dept_det': dept_det, 'inst_det': inst_det, 'dept': dept,'inst': inst,
               'pcmi': pcmi, 'pcmc': pcmc, 'program_edit': program_edit,'categories':categories}
    return render(request, 'bosc/edit_program.html', context)


@login_required
@group_required('BOSC')
def program_delete(request):
    if request.method == "POST":
        try:
            program_id = request.POST.get('program_del')
            Programs.objects.filter(id=program_id).delete()
            messages.success(request, 'Programme Deleted')
            return redirect(request.POST.get('path'))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect(request.POST.get('path'))
    return redirect(request.POST.get('path'))


@csrf_exempt
def get_levels_by_ptype(request):
    if request.method == "POST":
        d = ProgramLevel.objects.filter(program_type_id=request.POST.get('p_type'), status=1).values('id', 'level')
        topics = list(d)
        return JsonResponse(topics, safe=False)
    else:
        return redirect('/')


@csrf_exempt
def get_pcm_incharges(request):
    if request.method == "POST":
        keyword = request.POST.get('term')
        users = User.objects.filter(
            Q(is_active=1),
            Q(first_name__icontains=keyword)
            | Q(username__icontains=keyword) | Q(email__icontains=keyword)).exclude(groups__name__in=['PAB']).values(
            'id', 'first_name', 'username', 'emp_id',
            'campus', 'institution', 'department', 'email')
        return JsonResponse(list(users), safe=False)
    else:
        return JsonResponse({'status': 500})


@csrf_exempt
def get_pcm_coordinators(request):
    if request.method == "POST":
        keyword = request.POST.get('term')
        users = User.objects.filter(
            Q(is_active=1),
            Q(first_name__icontains=keyword)
            | Q(username__icontains=keyword) | Q(email__icontains=keyword)).exclude(groups__name__in=['PAB']).values(
            'id', 'first_name', 'username',
            'emp_id', 'campus', 'institution', 'department', 'email')
        return JsonResponse(list(users), safe=False)
    else:
        return JsonResponse({'status': 500})


@csrf_exempt
def get_pab_members(request):
    if request.method == "POST":
        keyword = request.POST.get('term')
        users = User.objects.filter(
            Q(is_active=1), ~Q(id=request.user.id), Q(dept_code_id=request.user.dept_code_id),
            Q(first_name__icontains=keyword)
            | Q(username__icontains=keyword), Q(groups__name__in=['PAB'])).values('id', 'first_name', 'username',
                                                                                  'email', 'designation')
        return JsonResponse(list(users), safe=False)
    else:
        return JsonResponse({'status': 500})


@login_required
@group_required('BOSC')
def bosc_program_detail(request, p_id):
    p_id = decrypt(p_id)
    program = Programs.objects.filter(id=p_id, user__dept_code_id=request.user.dept_code_id).values()
    program_user_mapping = ProgramUserMapping.objects.filter(program_id=p_id, program_status_level_id=2).values()
    if program :
        program_detail = ProgramUserMapping.objects.exclude(program_status_level_id__in=[1, 8, 9]).filter(program_id=p_id, to_user_id=request.user.id).values('user_id', 'is_edit', 'program_status_level_id', 'comment')
        course_view_access = None
        if program_detail.filter(program_status_level_id=6).exists():
            course_view_access = 1
        program_level = ''
        program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created', 'to_user_id',
                                                                                             'user__first_name',
                                                                                             'user_id',
                                                                                             'program_status_level__title',
                                                                                             'to_user__first_name',
                                                                                             'user__image', 'comment',
                                                                                             'to_user_group__description',
                                                                                             'user_group__description').order_by('-id')

        program_structures = []
        program_assign_details = ''

        program_timeline = []
        pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id, is_edit=1).values('created', 'to_user_id',
                                                                                                'program_status_level__title',
                                                                                                'to_user__first_name',
                                                                                                'to_user__image',
                                                                                                'comment',
                                                                                                'to_user_group__description',
                                                                                                'user_group__description').last()
        program_timeline.append(pending_timeline)
        program_timeline.extend(program_timeline_actions)
        program_assign_details = program_detail.last()

        course_categories = CourseCategory.objects.filter(status=1).values()
        program_course_cat_mapp = ProgramCourseMapping.objects.filter(program_id=p_id).values('id', 'course_id',
                                                                                              'course_category_id',
                                                                                              'course__C')

        program_course_data = [get_program_course_data(k['course_id'], p_id, k['course_category_id']) for k in
                               program_course_cat_mapp]
        p_c_mpapping = ProgramCategoryCountMapping.objects.filter(program_id=p_id).values()

        total_credit_distribution = []
        total = 0
        for i in course_categories:
            c = 0
            if i['id'] in [3, 5]:
                x = [p['count'] for p in p_c_mpapping if i['id'] == p['category_id']]
                if x:
                    c = c + x[0]
            else:
                for j in program_course_cat_mapp:
                    if i['id'] == j['course_category_id']:
                        c = c + int(j['course__C'])
            i['credits'] = c
            total += c
            total_credit_distribution.append(i)
        z = [{'percentage': round(i['credits'] * 100 / total, 2), **i} for i in total_credit_distribution]
        return render(request, 'bosc/program_detail.html',
                      {'levels': program_level, 'p_id': encrypt(p_id), 'program_structures': program_structures,
                       'course_view_access': course_view_access,
                       'program': program.last(), 'program_assign_details': program_assign_details,
                       'program_timeline': program_timeline,'total_credit_distribution':z,'total':total,
                        'program_user_mapping':program_user_mapping,'course_categories':course_categories,'program_course_data':program_course_data,'p_c_mpapping':p_c_mpapping})
    else:
        return redirect('/')




@login_required
@group_required('BOSC')
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
    return render(request, 'bosc/program_course_preview.html', context)




@login_required
@group_required('BOSC')
def program_structure_approve(request, p_id):
    p_id = decrypt(p_id)
    if request.method == 'POST':
        try:
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                 user_id=int(request.POST.get('pcmi_user_id')),
                                                 program_status_level_id__in=[2, 5]).exists():
                ProgramUserMapping.objects.create(program_id=p_id, to_user_id=request.POST.get('pcmi_user_id'),
                                                  user_id=request.user.id, program_status_level_id=3, is_edit=1,
                                                  to_user_group_id=5, user_group_id=6)
                ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                  program_status_level_id__in=[2, 5]).update(is_edit=0)
                email = User.objects.filter(id=request.POST.get('pcmi_user_id')).values('email', 'id', 'first_name')
                progm = Programs.objects.get(id=p_id)
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Curriculum for " + progm.name + " has been approved proceed for further process"
                message = render_to_string('bosc/email_templates/program_structure_approved_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'program': progm.name,

                })
                e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
                EmailStatus.objects.create(hint='BOSC Program Structure Approve', message=message,to_user_email=email[0]['email'], to_user_id=email[0]['id'],
                                                                                        user_id=request.user.id)

            messages.success(request, "Approved Successfully..")
            return redirect('bosc_program_detail', encrypt(p_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('bosc_program_detail', encrypt(p_id))
    return redirect('bosc_program_detail', encrypt(p_id))


@login_required
@group_required('BOSC')
def program_structure_need_more(request, p_id):
    p_id = decrypt(p_id)
    if request.method == 'POST':
        try:
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                 user_id=int(request.POST.get('pcmi_user_id')),
                                                 program_status_level_id__in=[2, 5]).exists():
                ProgramUserMapping.objects.create(program_id=p_id, to_user_id=request.POST.get('pcmi_user_id'),
                                                  user_id=request.user.id, program_status_level_id=4, is_edit=1,
                                                  comment=request.POST.get('bosc_message'),
                                                  to_user_group_id=5, user_group_id=6)
                ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                  program_status_level_id__in=[2, 5]).update(is_edit=0)
                email = User.objects.filter(id=request.POST.get('pcmi_user_id')).values('email', 'id', 'first_name')
                progm = Programs.objects.get(id=p_id)
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Suggestions regarding the curriculum of " + progm.name + "."
                message = render_to_string('bosc/email_templates/suggestions_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'program': progm.name,

                })
                #e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
                EmailStatus.objects.create(hint='BOSC Need More Info Suggestions', message=message,to_user_email=email[0]['email'], to_user_id=email[0]['id'],user_id=request.user.id)

            messages.success(request, "Submitted Successfully..")
            return redirect('bosc_program_detail', encrypt(p_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('bosc_program_detail', encrypt(p_id))
    return redirect('bosc_program_detail', encrypt(p_id))


@login_required
@group_required('BOSC')
def program_structure_syllabus_need_more(request, p_id):
    p_id = decrypt(p_id)
    if request.method == 'POST':
        try:
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                 user_id=int(request.POST.get('pcmi_user_id')),
                                                 program_status_level_id__in=[2, 5, 6]).exists():
                ProgramUserMapping.objects.create(program_id=p_id, to_user_id=request.POST.get('pcmi_user_id'),
                                                  user_id=request.user.id, program_status_level_id=19, is_edit=1,
                                                  comment=request.POST.get('bosc_message'),
                                                  to_user_group_id=5, user_group_id=6)
                ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                  program_status_level_id__in=[2, 5, 6]).update(is_edit=0)
                email = User.objects.filter(id=request.POST.get('pcmi_user_id')).values('email', 'id', 'first_name')
                progm = Programs.objects.get(id=p_id)
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Suggestions regarding the curriculum and syllabi of " + progm.name + "."
                message = render_to_string('bosc/email_templates/course_suggestions_pcmi_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'program': progm.name,

                })
                e = send_html_mail(mail_subject, message, [email[0]['email']], sender)

            messages.success(request, "Submitted Successfully..")
            return redirect('bosc_program_detail', encrypt(p_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('bosc_program_detail', encrypt(p_id))
    return redirect('bosc_program_detail', encrypt(p_id))


@login_required
@group_required('BOSC')
def assign_program_pab(request, p_id):
    p_id = decrypt(p_id)
    if request.method == "POST":
        try:
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,
                                                 program_status_level_id__in=[6, 13]).exists():
                pab = request.POST.getlist('pab_assigned')
                for i in range(len(pab)):
                    to_user_group = UserGroups.objects.filter(user_id=pab[i], is_active=1, is_block=0).values(
                        'group_id')
                    user_group = UserGroups.objects.filter(user_id=request.user.id, is_active=1, is_block=0).values(
                        'group_id')
                    ProgramUserMapping.objects.create(program_id=p_id, to_user_id=pab[i], user_id=request.user.id,
                                                      is_edit=1,
                                                      comment=request.POST.get('bosc_message'),
                                                      program_status_level_id=7,
                                                      to_user_group_id=to_user_group[0]['group_id'],
                                                      user_group_id=user_group[0]['group_id'])
                    # ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,program_status_level_id=6).update(is_edit=0)
                    email = User.objects.filter(id=pab[i]).values('email', 'id', 'first_name')
                    progm = Programs.objects.get(id=p_id)
                    sender = settings.EMAIL_HOST_USER
                    current_site = get_current_site(request)
                    mail_subject = "Member of the Programme Advisory Board for " + progm.name
                    message = render_to_string('bosc/email_templates/assign_pab_email.html', {
                        'email': encrypt(email[0]['email']),
                        'domain': current_site.domain,
                        'guest_firstname': email[0]['first_name'],
                        'program': progm.name,
                    })
                    e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
                messages.success(request, 'Assigned Successfully..')
                return redirect('bosc_program_detail', encrypt(p_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('bosc_program_detail', encrypt(p_id))
    return redirect('bosc_program_detail', encrypt(p_id))


@login_required
@group_required('BOSC')
def course_need_more_info_by_bosc(request, c_id):
    c_id = decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                course_status_level_id=4).exists():
                csmi_user = CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                             to_user_group_id=3, course_status_level_id=4).values(
                    'user_id')

                # CourseUserMapping.objects.create(course_id=c_id,to_user_id=csmi_user[0]['user_id'],user_id=request.user.id,course_status_level_id=6,
                #                                 comment= request.POST.get('csmi_message'),is_edit=1,course_header_id=course.course_header_id)
                # CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                #                                  course_status_level_id=4).update(is_edit=0)
            return redirect('course_preview_bosc', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_bosc', encrypt(c_id))
    return redirect('course_preview_bosc', encrypt(c_id))


# PAB Users Methods
@login_required
@group_required('BOSC')
def view_pab(request):
    title = "PAB"
    guest_details = User.objects.filter(is_superuser=0, usergroups__group_id__in=[9],
                                        dept_code_id=request.user.dept_code_id).values('id', 'designation', 'username',
                                                                                       'first_name', 'email', 'phone',
                                                                                       'campus', 'institution',
                                                                                       'department', 'groups')
    user_detail = []
    for i in guest_details:
        i['encrypt_id'] = encrypt(i['id'])
        user_detail.append(i)
    return render(request, 'bosc/view_pab.html', {'guest_details': guest_details, 'title': title})


def handle_uploaded_file(f, temp_file):
    with open('media/' + temp_file + '.xlsx', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@login_required
@group_required('BOSC')
def pab_upload(request):
    if request.method == 'POST':
        try:
            import xlrd
            temp_file = 'data_upload'
            handle_uploaded_file(request.FILES['data'], temp_file)
            wb = xlrd.open_workbook('media/' + temp_file + '.xlsx')
            sheet = wb.sheet_by_index(0)
            for i in range(1, sheet.nrows):
                if not User.objects.filter(username=sheet.cell_value(i, 3)).exists():
                    guest = User.objects.create(first_name=sheet.cell_value(i, 1), phone=sheet.cell_value(i, 2) or None,
                                                email=sheet.cell_value(i, 3), is_active=1,
                                                username=sheet.cell_value(i, 3),
                                                designation=sheet.cell_value(i, 4) or None, is_staff=0,
                                                is_superuser=0, dept_code_id=sheet.cell_value(i, 5),
                                                address=sheet.cell_value(i, 6))
                    UserGroups.objects.create(role="PAB", is_active=1, is_block=0, group_id=9, user_id=guest.id)
            messages.success(request, 'Data Stored Successfully')
            return redirect('view_pab')
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('view_pab')
    else:
        return redirect('view_pab')


@login_required
@group_required('BOSC')
def add_pab_user(request):
    if request.method == "POST":
        try:
            email = request.POST.get('email')
            firstname = request.POST.get('firstname')
            phone = request.POST.get('phone')
            campus = request.POST.get('campus')
            designation = request.POST.get('designation')
            image = '/media/icons/guest_icon.png'
            if User.objects.filter(email=email).exists():
                messages.error(request, "User Already Exists")
                ErrorLogs.objects.create(log="User Already Exists", user_id=request.user.id)
                return render(request, 'bosc/add_pab.html')
            else:
                guest = User.objects.create_user(first_name=firstname, phone=phone, email=email, is_active=1,
                                                 image=image,
                                                 username=email,dept_code_id=request.user.dept_code_id, designation=designation, campus=campus, is_staff=0,
                                                 is_superuser=0)
                UserGroups.objects.create(role="PAB", is_active=1, is_block=0, group_id=9, user_id=guest.id)
                messages.success(request, "User Created Successfully")
                return redirect('/bosc/view_pab')
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return render(request, 'bosc/add_pab.html')
    else:
        return render(request, 'bosc/add_pab.html')


@login_required
@group_required("BOSC")
def forward_program_to_bos_by_bosc(request, p_id):
    p_id = decrypt(p_id)
    if request.method == "POST":
        try:
            if request.POST.get('program_status_level_id') == '13':
                program_status_level_id = 14
            else:
                program_status_level_id = 11
            to_user = BoschairInstituteMapping.objects.filter(dept_code_id=request.user.dept_code_id).values()
            if not to_user:
                ErrorLogs.objects.create(log='bos not found', user_id=request.user.id)
                messages.error(request, 'BOS Chair not assigned')
                return redirect('bosc_program_detail', encrypt(p_id))
            ProgramUserMapping.objects.create(created=datetime.now(), is_edit=1, program_id=p_id,
                                              program_status_level_id=program_status_level_id,
                                              to_user_id=to_user[0]['bos_chair_id'], user_id=request.user.id,
                                              to_user_group_id=7,
                                              user_group_id=6)


            ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1,
                                              program_status_level_id__in=[6, 11, 13]).update(is_edit=0)

            email = User.objects.filter(id=to_user[0]['bos_chair_id']).values('email', 'id', 'first_name')
            progm = Programs.objects.get(id=p_id)
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Curriculum and Syllabus of " + progm.name + " has been prepared and submitted for your Approval/Suggestions"
            message = render_to_string('bosc/email_templates/bosc_forward_bos_email.html', {
                'email': encrypt(email[0]['email']),
                'domain': current_site.domain,
                'guest_firstname': email[0]['first_name'],
                'program': progm.name,
            })
            e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, 'Forwarded Successfully..')
            return redirect('bosc_program_detail', encrypt(p_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('bosc_program_detail', encrypt(p_id))
    else:
        return redirect('bosc_program_detail', encrypt(p_id))







@login_required
@group_required("BOSC")
def course_structure_need_more(request, c_id):
    c_id = decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,course_status_level_id__in=[5, 18,4]).exists():
                csmi_user = CourseUserMapping.objects.filter(course_id=c_id,to_user_group_id=3).values('user_id').last()
                CourseUserMapping.objects.create(course_id=c_id, to_user_id=csmi_user['user_id'],
                                                 user_id=request.user.id, course_status_level_id=11,
                                                 comment=request.POST.get('bosc_message'), is_edit=1,
                                                 to_user_group_id=3, user_group_id=6
                                                 )
                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id).update(is_edit=0)

            messages.success(request, 'Forwarded Successfully..')
            return redirect('course_preview_bosc', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_bosc', encrypt(c_id))
    return redirect('course_preview_bosc', encrypt(c_id))


