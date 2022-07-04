from course_management.functions import *
from programs.program_course_models import *
from django.contrib import messages

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
@group_required('PCMI')
def index(request):
    programs = ProgramUserMapping.objects.filter(Q(to_user_id=request.user.id),Q(is_active=1),Q(to_user_group_id=5)).values('id','program__name','program_status_level__title',
                                                                                    'program__program_type__type','program__program_type_id',
                                                                                    'program_id').order_by('-created')

    program = []
    program_id =[]
    for i in programs:
        if not i['program_id'] in program_id:
            i['encrypt_id'] = encrypt(i['program_id'])
            program.append(i)
        program_id.append(i['program_id'])
    return render(request, 'pcmi/programs.html', {'programs': program})

@login_required
def programs(request):
    programs = ProgramUserMapping.objects.filter(to_user_id=request.user.id).values('program__name',
                                                                                    'program__program_type__type','program_id')
    program = []
    for i in programs:
        i['encrypt_id']=encrypt(i['program_id'])
        program.append(i)

    return render(request,'pcmi/programs.html',{'programs':program})



def handle_uploaded_file(f,temp_file):
    with open('media/'+temp_file+'.xlsx', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
def pcmi_program_detail(request,p_id):
    p_id = decrypt(p_id)
    program=Programs.objects.filter(id=p_id).values()
    course_type = CourseType.objects.filter(status=1).values('id', 'name')
    
    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,to_user_group_id=5,is_active=1).\
                                                                                    values('user_id','is_edit','program_status_level_id').last()
        if program_assign_details:
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')

            program_timeline = []
            program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created','to_user_id','user__first_name','user_id','program_status_level__title',
                                                                                                 'to_user__first_name','user__image','comment',
                                                                                                 'to_user_group__description','user_group__description').order_by('-id')

            pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id,is_edit=1).values('created', 'to_user_id',
                                                                                         'program_status_level__title', 'to_user__first_name',
                                                                                         'to_user__image', 'comment','to_user_group__description','user_group__description').last()

            program_timeline.append(pending_timeline)
            program_timeline.extend(program_timeline_actions)




            program_user_mapping = None
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1).exists():
                program_user_mapping = ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,is_edit=1).values().last()



            course_categories=CourseCategory.objects.filter(status=1).values().exclude(id=9).order_by('priority')
            program_course_cat_mapp = ProgramCourseMapping.objects.filter(program_id=p_id).values('id',
            'course_id','course_category_id','course__C','basket_id','basket__basket_name','course__program_type__type','course__L',
            'course__T', 'course__P', 'course__J', 'course__S', 'course__C', 'course__course_name','course__pass_fail',
            'course__course_type_id', 'course__faculty','course__course_type__name','course__level_of_course__level','course__course_code',
            'group_id','group__group_name','group__choice_count','group__symbol')
            for i in course_categories:
                program_course_data=[]
                program_basket_data=[]
                program_group_data=[]
                
                pbd={}
                for j in program_course_cat_mapp:
                    if i['id'] == j['course_category_id'] and j['basket_id'] is None:
                        j['row_type']='course'
                        j['encrypt_id']=encrypt(j['course_id'])
                        j['course_name']=j['course__course_name']
                        j['course_type']=j['course__course_type__name']
                        j['course_level']=j['course__level_of_course__level']
                        j['course_code']=j['course__course_code']
                        j['pass_fail']=j['course__pass_fail']
                        j['faculty']=j['course__faculty']
                        j['L']=j['course__L']
                        j['T']=j['course__T']
                        j['P']=j['course__P']
                        j['J']=j['course__J']
                        j['S']=j['course__S']
                        j['C']=j['course__C']
                        j['id']=j['course_id']
                        j['group_symbol']=j['group__symbol']
                        program_course_data.append(j)
                basket_data=ProgramCourseBasket.objects.filter(program_id=p_id,category_id=i['id']).values('id','basket_name','L','T','P','J','S','C',
                    'course_type__name','level_of_course__level','course_type_id','level_of_course_id','choice_count','group_id','group__group_name','group__choice_count','group__symbol') 
                for j in  basket_data:
                    k={}
                    j['row_type']='basket'
                    j['course_name']=j['basket_name']
                    j['basket_id']=j['id']
                    j['course_type']=j['course_type__name']
                    j['course_level']=j['level_of_course__level']
                    j['group_symbol']=j['group__symbol']
                    program_course_data.append(j)
                    k['basket_name']=j['basket_name']
                    k['id']=j['basket_id']
                    a=program_course_cat_mapp.filter(basket_id=j['id'])
                    for l in a:
                        l['encrypt_id']=encrypt(l['course_id'])
                    k['basket_courses']  =a  
                    program_basket_data.append(k)
                groups=ProgramCourseGroup.objects.filter(program_id=p_id,category_id=i['id']).values('id','group_name','choice_count','symbol')    
                #group_courses=[]
                for m in groups:
                    group_courses=[]
                    for n in program_course_data:
                        if m['id']==n['group_id']:
                            group_courses.append(n)
                    m['group_courses'] =group_courses  
                    program_group_data.append(m)
                #program_course_data.sort(key=lambda d: d['course_level']) 
                i['program_course_data']=program_course_data  
                i['basket_data']=program_basket_data
                i['group_data']=program_group_data
                


            program_course_cat_mapp = ProgramCourseMapping.objects.filter(program_id=p_id).values('id','course_id','course_category_id','course__C')
            p_c_mpapping=ProgramCategoryCountMapping.objects.filter(program_id=p_id).values('count', 'category_id', 'program_id', 'label_category','category_id__category')
            p_c_mpapping_op_elective=ProgramCategoryCountMapping.objects.filter(program_id=p_id,category_id=5).values_list('label_category',flat=True)
            if p_c_mpapping_op_elective:
                if p_c_mpapping_op_elective[0]:
                    p_c_mpapping_op_elective=CourseCategory.objects.filter(id__in=p_c_mpapping_op_elective[0]).values('short_code')
            #print(p_c_mpapping_op_elective[0][0])
            total_credit_distribution=[]
            total=0
            for i in CourseCategory.objects.filter(status=1).values():
                c=0
                x = [p['count'] for p in p_c_mpapping if i['id'] == p['category_id']]
                if x:
                    c = c + x[0]
                i['credits']=c
                total+=c
                total_credit_distribution.append(i)


            z=[{'percentage':round(i['credits']*100/total,2),**i}  for i in total_credit_distribution if i['credits']>0]

            # minor core
            minor_programs = MinorCoreProgramMapping.objects.filter(program_id=p_id).values('mapped_program_id','mapped_program__name')
            for i in minor_programs:
                i['enc_mapped_id']=encrypt(i['mapped_program_id'])
                course_ids = ProgramCourseMapping.objects.filter(program_id=i['mapped_program_id']).values_list('course_id', flat=True)
                i['course_data']=get_course_data(list(course_ids))

            course_categories_short_names = CourseCategory.objects.filter(status=1,id__in=[2,3,4]).values()

            #final submit error mes
            below_credits=[]
            from django.db.models import Sum
            x=ProgramCourseMapping.objects.filter(program_id=p_id).values('course_category_id','course_category_id__category').annotate(sum=Sum('course_id__C'))
            for i in p_c_mpapping:
                if i['category_id'] in [j['course_category_id'] for j in x]:
                    for j in x:
                        if i['category_id'] == j['course_category_id'] and i['count']>j['sum']:
                            s=j['course_category_id__category']+' Credit value '+str(i['count'])+' is greater than the C sum value '+str(int(j['sum']))
                            below_credits.append(s)
                elif i['category_id'] == 9:
                    t=MinorCoreProgramMapping.objects.filter(program_id=p_id).values_list('mapped_program_id')
                    minor_C = ProgramCourseMapping.objects.filter(program_id__in=t).values('program_id').annotate(sum=Sum('course_id__C'))

                    if minor_C:
                        total1=0
                        for c in minor_C:
                            total1=total1+c['sum']
                        if i['count']>total1:
                            s = i['category_id__category'] + ' Credit value ' + str(i['count']) + ' is greater than the C sum value ' + str(int(total1))
                            below_credits.append(s)

                    else:
                        s = i['category_id__category'] + ' Credit value ' + str(i['count']) + ' but Courses not Mapped'
                        below_credits.append(s)
                else:
                    s = i['category_id__category'] + ' Credit value ' + str(i['count']) + ' but Courses not Mapped'
                    below_credits.append(s)

            context = {'levels': program_level,'course_type':course_type,'p_id':p_id,'program_assign_details':program_assign_details,'program_timeline':program_timeline,'program':program,
                        'program_id':encrypt(p_id),'total_credit_distribution':z,'total':total,'minor_programs':minor_programs,'course_categories_short_names':course_categories_short_names,
                        'program_user_mapping':program_user_mapping,'course_categories':course_categories,
                       'p_c_mpapping':p_c_mpapping,'below_credits':below_credits,'p_c_mpapping_op_elective':p_c_mpapping_op_elective,
                       }
            return render(request, 'pcmi/program_detail.html', context)
        else:
            return redirect('/') 
    else:
        return redirect('/')




@login_required
def pcmi_minor_program_detail(request,p_id):
    p_id = decrypt(p_id)
    program=Programs.objects.filter(id=p_id).values()

    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,to_user_group_id=5,is_active=1).\
                                                                                    values('user_id','is_edit','program_status_level_id').last()
        if program_assign_details:
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')

            program_timeline = []
            program_timeline_actions = ProgramUserMapping.objects.filter(program_id=p_id).values('created','to_user_id','user__first_name','user_id','program_status_level__title',
                                                                                                 'to_user__first_name','user__image','comment',
                                                                                                 'to_user_group__description','user_group__description').order_by('-id')

            pending_timeline = ProgramUserMapping.objects.filter(program_id=p_id,is_edit=1).values('created', 'to_user_id',
                                                                                         'program_status_level__title',
                                                                                         'to_user__first_name',
                                                                                         'to_user__image', 'comment','to_user_group__description','user_group__description').last()
            program_timeline.append(pending_timeline)
            program_timeline.extend(program_timeline_actions)

            program_course_mapp = ProgramCourseMapping.objects.filter(program_id=p_id).values('id', 'course_id',
                                                                                                  'course_category_id',
                                                                                                  'course__C',
                                                                                                  'basket_id',
                                                                                                  'basket__basket_name').distinct()
            program_course_data=[]
            for j in program_course_mapp:
                if j['basket_id'] is None:
                    program_course_data.extend(get_course_data([j['course_id']]))

            #program_basket_course_data = get_minor_program_course_basket_data(request, p_id)
            program_basket_course_data=None
            program_user_mapping = None
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1).exists():
                program_user_mapping = ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,is_edit=1).values().last()

            context = {'levels': program_level,'p_id':p_id,'program_assign_details':program_assign_details,'program_timeline':program_timeline,'program':program,
                        'program_id':encrypt(p_id),'program_basket_course_data':program_basket_course_data,
                        'program_user_mapping':program_user_mapping,'program_course_data':program_course_data
                       }
            return render(request, 'pcmi/minor_program_detail.html', context)
        else:
            return redirect('/')
    else:
        return redirect('/')

@login_required
def program_course_category_count(request):
    from django.db.models import Sum
    if request.method == "POST":
        try:
            ProgramCategoryCountMapping.objects.filter(category_id=request.POST['cat_id'],program_id=request.POST['program_id']).delete()
            if 'label' in request.POST:
                ProgramCategoryCountMapping.objects.create(label_category=request.POST.getlist('label'), count=request.POST['credit_count'], category_id=request.POST['cat_id'],
                                                           created_by_id=request.user.id, program_id=request.POST['program_id'])
            else:
                ProgramCategoryCountMapping.objects.create(count=request.POST['credit_count'],
                                                           category_id=request.POST['cat_id'],
                                                           created_by_id=request.user.id,
                                                           program_id=request.POST['program_id'])
            messages.success(request,'Submitted Successfully')
            return redirect(request.POST['path'])
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e) + '--- program_course_category_count', user_id=request.user.id,info=request.POST)
            return redirect(request.POST['path'])
    else:
        return redirect('/')

@login_required
def pcmi_program_courses(request,p_id,id):
    p_id = decrypt(p_id)
    program=Programs.objects.filter(id=p_id).values('id','program_type_id','program_type_id__type','name')
    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,to_user_group_id=5,is_active=1).\
                                                                                    values('user_id','is_edit','program_status_level_id').last()
        if program_assign_details:
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')

            course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id,course_category_id=id).values_list('course_id',flat=True)
            dept=None
            course_data = None
            #departments filter
            departments = DepartmentInstituteCodes.objects.filter(status=1).values('id','dept_code', 'dept_inst')
            if 'department' in request.GET:
                dept = request.GET.get('department')
                program_course_category_mapped_ids=ProgramCourseMapping.objects.filter(program_id=p_id).exclude(course_category_id=id).values_list('course_id')
                course_ids=CourseDepartmentMapping.objects.filter(course__dept_code_id=dept).exclude(course__in=program_course_category_mapped_ids)
                #,course__courseusermapping__course_status_level_id=1
                if program[0]['program_type_id'] == 1:
                    course_ids=course_ids.filter(course__program_type_id=1).values_list('course_id',flat=True)
                elif program[0]['program_type_id'] == 2:
                    course_ids = course_ids.filter(course__program_type_id=2).values_list('course_id',flat=True)
                else:
                    course_ids = course_ids.values_list('course_id', flat=True)
                course_data=get_course_data(list(course_ids))

            program_user_mapping = None
            is_edit = 0
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1).exists():
                program_user_mapping = ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,is_edit=1).values().last()
                if program_user_mapping['program_status_level_id'] in [1,4] and program_user_mapping['is_edit'] == 1:
                    is_edit=1

            course_category=CourseCategory.objects.get(id=id)
            
            basket_course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id, course_category_id=id).values('basket_id','course_id')
            all_baskets=ProgramCourseBasket.objects.filter(category_id=id,program_id=p_id).values()
            context = {'levels': program_level,'p_id':p_id,'program_assign_details':program_assign_details,'program':program,
                        'program_id':encrypt(p_id),'departments':departments,'dept':dept,'course_data':course_data,'course_mapped':list(course_mapped),
                     'is_edit':is_edit,'category_id':id,'enc_program_id':encrypt(p_id),'course_category':course_category,
                       'basket_course_mapped':basket_course_mapped,'all_baskets':all_baskets
                       }
            return render(request, 'pcmi/program_courses.html', context)
        else:
            return redirect('/')
    else:
        return redirect('/')

@login_required
@group_required('PCMI','PCMM')
def baskets(request,p_id,id):
    p_id = decrypt(p_id)
    program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,to_user_group_id=5,is_active=1)
    if program_assign_details:
        course_type = CourseType.objects.filter(status=1).values('id', 'name')
        course_category=CourseCategory.objects.get(id=id)
        program=Programs.objects.filter(id=p_id).values('id','program_type_id','program_type_id__type','name')
        program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')
        course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id,course_category_id=id).values_list('course_id',flat=True)
        basket_course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id, course_category_id=id,basket_id__isnull=False).values('basket_id','course_id')
        basket_course_mapped_ids=basket_course_mapped.values_list('course_id',flat=True)
        #exclude(course_id__in=basket_course_mapped.filter(basket_id__isnull=False).values_list('course_id')).
        program_course_cat_mapp = ProgramCourseMapping.objects.filter(program_id=p_id,course_category_id=id).values('id',
                                 'course_id','course_category_id','course__C', 'basket_id','basket__basket_name',
                        'course__program_type__type', 'course__L', 'course__T', 'course__P','course__J', 'course__S',
                        'course__C','course__course_name','course__pass_fail','course__course_type_id', 'course__faculty',
                         'course__course_type__name','course__level_of_course__level','course__course_code', 'group_id',
                         'group__group_name','group__choice_count','group__symbol')
        all_baskets=ProgramCourseBasket.objects.filter(category_id=id,program_id=p_id).values('id','basket_name','L','T','P','J','S','C',
                    'course_type__name','level_of_course__level','course_type_id',
                    'level_of_course_id','choice_count','group_id','group__group_name',
                    'group__choice_count','group__symbol')
        for i in all_baskets:
            i['encrypt_id']=encrypt(i['id'])
        context = {'levels': program_level,'p_id':p_id,'program_assign_details':program_assign_details,'program':program,
                    'program_id':encrypt(p_id),'course_mapped':list(course_mapped),
                    'category_id':id,'enc_program_id':encrypt(p_id),'course_category':course_category,'course_type':course_type,
                   'basket_course_mapped':basket_course_mapped,'all_baskets':all_baskets,'program_course_cat_mapp':program_course_cat_mapp,
                   'basket_course_mapped_ids':basket_course_mapped_ids
                   }
        return render(request, 'pcmi/baskets.html', context)
    else:
        return redirect('/')


@login_required
@group_required('PCMI','PCMM')
def add_basket(request):
    if request.method == 'POST':
        s = request.POST
        course_category_id = None
        if 'course_category_id' in s:
            course_category_id = s['course_category_id']
            L = 0
            T = 0
            P = 0
            S = 0
            J = 0
            C = 0
            if request.POST['course_type'] == '1':
                L = request.POST['L']
                T = request.POST['T']
                C = int(L) + int(T)
            elif request.POST['course_type'] == '2':
                P = request.POST['P']
                C = int(P) * 0.5
            elif request.POST['course_type'] == '3':
                L = request.POST['L']
                T = request.POST['T']
                P = request.POST['P']
                C = int(L) + int(T) + (int(P) * 0.5)
            elif request.POST['course_type'] == '4':
                J = int(request.POST['J'])
                C = int(request.POST['C'])
            elif request.POST['course_type'] == '5':
                S = request.POST['S']
                C = int(S)
            elif request.POST['course_type'] == '6':
                L = request.POST['L']
                T = request.POST['T']
                P = request.POST['P']
                S = request.POST['S']
                J = request.POST['J']
                C = 0
            if not request.POST.get('basket_id'):
                insert = ProgramCourseBasket.objects.create(basket_name=s['basket_name'], L=L, T=T, P=P, S=S, J=J,
                           C=int(C),course_type_id=request.POST['course_type'], choice_count=s['choice_count'], level_of_course_id=request.POST['course_level'],
                          category_id=course_category_id,created_by_id=request.user.id, program_id=s['program_id'])
                print(request.POST.getlist('course_id'))
                if request.POST.getlist('course_id'):
                    ProgramCourseMapping.objects.filter(program_id=s['program_id'],course_category_id=course_category_id,course_id__in=request.POST.getlist('course_id')).update(
                        basket_id=insert.id)
            elif ProgramCourseBasket.objects.filter(id=request.POST.get('basket_id')).exists():
                ProgramCourseBasket.objects.filter(id=request.POST.get('basket_id')).update(basket_name=s['basket_name'],
                            L=L, T=T, P=P, S=S, J=J,  C=int(C),course_type_id=request.POST['course_type'],
                          choice_count=s['choice_count'],level_of_course_id=request.POST['course_level'])
                if request.POST.getlist('course_id'):
                    ProgramCourseMapping.objects.filter(program_id=s['program_id'], course_category_id=course_category_id,basket_id=request.POST.get('basket_id')).update(
                        basket_id=None)
                    ProgramCourseMapping.objects.filter(program_id=s['program_id'],course_category_id=course_category_id,course_id__in=request.POST.getlist('course_id')).update(
                        basket_id=request.POST.get('basket_id'))

            messages.success(request, 'Basket Created Successfully')
        return redirect(s['path'])
    return redirect('/')


@login_required
def basket_delete(request):
    b_id = decrypt(request.POST['basket_id'])
    if ProgramCourseBasket.objects.filter(id=b_id).exists():
        ProgramCourseMapping.objects.filter(basket_id=b_id).update(basket_id=None)
        ProgramCourseBasket.objects.filter(id=b_id).delete()
        messages.success(request, 'Deleted Successfully')
        return redirect(request.POST['return_path'])
    else:
        return redirect('/')

@login_required
@group_required('PCMI','PCMM')
def groups(request,p_id,id):
    p_id = decrypt(p_id)
    program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,to_user_group_id=5,is_active=1)
    if program_assign_details:
        program=Programs.objects.filter(id=p_id).values('id','program_type_id','program_type_id__type','name')
        course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id,course_category_id=id).values_list('course_id',flat=True)
        group_course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id, course_category_id=id,group_id__isnull=False).values('basket_id','course_id')
        group_course_mapped_ids=group_course_mapped.values_list('course_id',flat=True)
        program_course_cat_mapp = ProgramCourseMapping.objects.filter(program_id=p_id,course_category_id=id).values('id',
                                 'course_id','course_category_id','course__C', 'basket_id','basket__basket_name',
                        'course__program_type__type', 'course__L', 'course__T', 'course__P','course__J', 'course__S',
                        'course__C','course__course_name','course__pass_fail','course__course_type_id', 'course__faculty',
                         'course__course_type__name','course__level_of_course__level','course__course_code', 'group_id',
                         'group__group_name','group__choice_count','group__symbol')
        program_course_data=[]
        for j in program_course_cat_mapp:
            if  j['basket_id'] is None:
                j['row_type'] = 'course'
                j['encrypt_id'] = encrypt(j['course_id'])
                j['course_name'] = j['course__course_name']
                j['course_type'] = j['course__course_type__name']
                j['course_level'] = j['course__level_of_course__level']
                j['course_code'] = j['course__course_code']
                j['pass_fail'] = j['course__pass_fail']
                j['faculty'] = j['course__faculty']
                j['L'] = j['course__L']
                j['T'] = j['course__T']
                j['P'] = j['course__P']
                j['J'] = j['course__J']
                j['S'] = j['course__S']
                j['C'] = j['course__C']
                j['id'] = j['course_id']
                j['group_symbol'] = j['group__symbol']
                program_course_data.append(j)
        basket_data = ProgramCourseBasket.objects.filter(program_id=p_id, category_id=id).values('id',
                  'basket_name','L', 'T', 'P','J', 'S', 'C','course_type__name','level_of_course__level','course_type_id',
                  'level_of_course_id','choice_count','group_id','group__group_name','group__choice_count','group__symbol')
        for j in basket_data:
            k = {}
            j['row_type'] = 'basket'
            j['course_name'] = j['basket_name']
            j['basket_id'] = j['id']
            j['course_type'] = j['course_type__name']
            j['course_level'] = j['level_of_course__level']
            j['group_symbol'] = j['group__symbol']
            program_course_data.append(j)
            k['basket_name'] = j['basket_name']
            k['id'] = j['basket_id']
            #a = program_course_cat_mapp.filter(basket_id=j['id'])
            #for l in a:
            #    l['encrypt_id'] = encrypt(l['course_id'])
            #k['basket_courses'] = a
            #program_basket_data.append(k)
        all_groups=ProgramCourseGroup.objects.filter(category_id=id,program_id=p_id).values('id','group_name','choice_count','symbol')
        for i in all_groups:
            i['encrypt_id']=encrypt(i['id'])
        context = {'p_id':p_id,'program_assign_details':program_assign_details,'program':program,
                    'program_id':encrypt(p_id),'course_mapped':list(course_mapped),
                    'category_id':id,'enc_program_id':encrypt(p_id),'program_course_data':program_course_data,
                   'basket_course_mapped':group_course_mapped,'all_groups':all_groups,'program_course_cat_mapp':program_course_cat_mapp,
                   'basket_course_mapped_ids':group_course_mapped_ids
                   }
        return render(request, 'pcmi/groups.html', context)
    else:
        return redirect('/')

@login_required
def pcmi_minor_program_courses(request,p_id):
    p_id = decrypt(p_id)
    program=Programs.objects.filter(id=p_id).values('id','program_type_id','program_type_id__type','name')
    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,to_user_group_id=5,is_active=1).\
                                                                                    values('user_id','is_edit','program_status_level_id').last()
        if program_assign_details:
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')

            course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id).values_list('course_id',flat=True)


            program_user_mapping = None
            is_edit = 0
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1).exists():
                program_user_mapping = ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,is_edit=1).values().last()
                if program_user_mapping['program_status_level_id'] in [1,4] and program_user_mapping['is_edit'] == 1:
                    is_edit=1

            dept = None
            course_data = None
            # departments filter
            departments = DepartmentInstituteCodes.objects.values('dept_code').distinct()
            if 'department' in request.GET:
                dept = request.GET.get('department')
                course_ids = CourseDepartmentMapping.objects.filter(department=request.GET['department'],course__dept_code__dept_code=dept)
                if program[0]['program_type_id'] == 1:
                    course_ids = course_ids.filter(course__program_type_id=1).values_list('course_id', flat=True)
                elif program[0]['program_type_id'] == 2:
                    course_ids = course_ids.filter(course__program_type_id=2).values_list('course_id', flat=True)
                else:
                    course_ids = course_ids.values_list('course_id', flat=True)
                course_data = get_course_data(list(course_ids))

            basket_data = ProgramCourseBasket.objects.filter(program_id=p_id).values()
            final_basket_data = []
            for i in basket_data:
                i['enc_id'] = encrypt(i['id'])
                final_basket_data.append(i)
            all_baskets=ProgramCourseBasket.objects.filter(program_id=p_id).values()
            basket_course_mapped = ProgramCourseMapping.objects.filter(program_id=p_id).values('basket_id', 'course_id')
            context = {'levels': program_level,'p_id':p_id,'program_assign_details':program_assign_details,'program':program,
                        'program_id':encrypt(p_id),'course_mapped':list(course_mapped),'basket_data':final_basket_data,'departments':departments,
                        'is_edit':is_edit,'category_id':id,'enc_program_id':encrypt(p_id),'dept':dept,'course_data':course_data,'all_baskets':all_baskets,
                        'basket_course_mapped':basket_course_mapped
                       }
            return render(request, 'pcmi/minor_program_courses.html', context)
        else:
            return redirect('/')
    else:
        return redirect('/')

@csrf_exempt
def program_course_mapping(request):
    if request.method == 'POST':
        course_id=request.POST['course_id']
        program_id=request.POST['program_id']
        status=request.POST['status']
        item_type=request.POST['item_type']
        basket_id=request.POST['basket_id']
        course_category_id=None
        if 'category_id' in request.POST:
            course_category_id = request.POST['category_id']


        try:
            pre=CoursePrerequestiesMapping.objects.filter(course_id=course_id).values('prerequesti_id','prerequesti_id__course_name')
            #program_courses=ProgramCourseMapping.objects.filter(program_id=program_id,course_category_id=course_category_id).values_list('course_id',flat=True)
            program_courses=ProgramCourseMapping.objects.filter(program_id=program_id).values_list('course_id',flat=True)
            pending_courses=[]
            for i in pre:
                if i['prerequesti_id'] not in program_courses:
                    pending_courses.append(i['prerequesti_id__course_name'])

            if len(pending_courses)>0:
                return JsonResponse({'status': 201,'pending_courses':pending_courses})

            if status == '1':
                ProgramCourseMapping.objects.create(basket_id=basket_id,course_id=course_id, created_by_id=request.user.id,program_id=program_id,item_type=item_type,
                                                    course_category_id=course_category_id)
            elif status == '0':
                ProgramCourseMapping.objects.filter(course_id=course_id, created_by_id=request.user.id,
                                                    program_id=program_id,item_type=item_type).delete()
            return JsonResponse({'status': 200})
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e) + '--- program_course_mapping', user_id=request.user.id)
            return JsonResponse({'status':500})
    else:
        return JsonResponse({'status': 500})




@csrf_exempt
def program_course_basket_update(request):
    if request.method == 'POST':
        course_id=request.POST['course_id']
        program_id=request.POST['program_id']
        basket_id=request.POST['basket_id']

        category_id = None
        if 'category_id' in request.POST:
            category_id = request.POST['category_id']
        try:
            if category_id:
                ProgramCourseMapping.objects.filter(course_id=course_id,program_id=program_id,course_category_id=category_id).update(basket_id=basket_id)
            elif category_id is None:
                ProgramCourseMapping.objects.filter(course_id=course_id, program_id=program_id).update(basket_id=basket_id)

            return JsonResponse({'status': 200})
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e) + '--- program_course_basket_update', user_id=request.user.id)
            return JsonResponse({'status':500})
    else:
        return JsonResponse({'status': 500})






@login_required
def po_pso_mapping(request,p_id,c_id):
    program_id=decrypt(p_id)
    program=Programs.objects.get(id=program_id)
    course=Course.objects.get(id=c_id)
    course_id=c_id
    program_course_outcome = ProgramCourseOutcome.objects.filter(course_id=course_id,program_id=program_id).values('id', 'po')
    program_specific_outcome = ProgramSpecificOutcome.objects.filter(course_id=course_id,program_id=program_id).values('id', 'pso')
    course_outcomes = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    co_po_map=ProgramCourseCOPOMapping.objects.filter(course_id=course_id,program_id=program_id,user_id=request.user.id).values()
    co_pso_map=ProgramCourseCOPSOMapping.objects.filter(course_id=course_id,program_id=program_id,user_id=request.user.id).values()
    if request.method == "POST":
        if ProgramCourseOutcome.objects.filter(course_id=course_id,program_id=program_id).exists():
            co_list = [i for i in request.POST.getlist('program_outcome_id') if i]
            ProgramCourseOutcome.objects.filter(course_id=course_id,program_id=program_id).exclude(id__in=co_list).delete()
            for i in range(len(request.POST.getlist('program_outcome'))):
                co = None
                if i < len(request.POST.getlist('program_outcome_id')):
                    co = request.POST.getlist('program_outcome_id')[i]
                    if co:
                        if ProgramCourseOutcome.objects.filter(id=co).exists():
                            ProgramCourseOutcome.objects.filter(id=request.POST.getlist('program_outcome_id')[i]).update(course_id=course_id,po=request.POST.getlist('program_outcome')[i],
                                                                                                                         user_id=request.user.id,program_id=program_id)
                    else:
                        ProgramCourseOutcome.objects.create(course_id=course_id,
                                                            po=request.POST.getlist('program_outcome')[i],
                                                            created=datetime.now(),
                                                            user_id=request.user.id, program_id=program_id)
        else:
            for i in range(len(request.POST.getlist('program_outcome'))):
                ProgramCourseOutcome.objects.create(course_id=course_id,po=request.POST.getlist('program_outcome')[i],created=datetime.now(),
                                                    user_id=request.user.id,program_id=program_id)
        if ProgramSpecificOutcome.objects.filter(course_id=course_id,program_id=program_id).exists():
            pso_list = [i for i in request.POST.getlist('pso_id') if i]

            ProgramSpecificOutcome.objects.filter(course_id=course_id,program_id=program_id).exclude(id__in=pso_list).delete()
            for i in range(len(request.POST.getlist('pso_id'))):
                pso = None
                if i < len(request.POST.getlist('pso_id')):
                    pso = request.POST.getlist('pso_id')[i]
                    if pso:
                        if ProgramSpecificOutcome.objects.filter(id=pso, course_id=course_id,program_id=program_id).exists():
                            ProgramSpecificOutcome.objects.filter(id=request.POST.getlist('pso_id')[i],
                                                                  course_id=course_id,program_id=program_id).update(course_id=course_id,
                                                                                              pso=request.POST.getlist(
                                                                                                  'pso')[i],
                                                                                              created=datetime.now(),
                                                                                              user_id=request.user.id)
                    else:
                        ProgramSpecificOutcome.objects.create(course_id=course_id, pso=request.POST.getlist('pso')[i],
                                                              created=datetime.now(), user_id=request.user.id,program_id=program_id)
        else:
            for i in range(len(request.POST.getlist('pso'))):
                ProgramSpecificOutcome.objects.create(course_id=course_id, pso=request.POST.getlist('pso')[i],
                                                      created=datetime.now(), user_id=request.user.id,program_id=program_id)

        messages.success(request,'Updated Successfully')
        context={'program':program,'course':course,'p_id':p_id,'c_id':encrypt(c_id),'program_course_outcome':program_course_outcome,
                 'program_specific_outcome':program_specific_outcome,'course_outcomes':course_outcomes,'co_po_map':co_po_map,'co_pso_map':co_pso_map}
        return render(request,'pcmi/po_pso_mapping.html',context)
    else:
        context = {'program': program, 'course': course, 'p_id': p_id, 'c_id': encrypt(c_id),'program_course_outcome':program_course_outcome,
                   'program_specific_outcome':program_specific_outcome,'course_outcomes':course_outcomes,'co_po_map':co_po_map,'co_pso_map':co_pso_map}
        return render(request, 'pcmi/po_pso_mapping.html', context)


@login_required
def program_course_outcome_delete(request):
    if request.method == 'POST':
        ProgramCourseOutcome.objects.filter(pk=request.POST['pk']).delete()
        messages.success(request, 'Deleted Successfully')
        return redirect(request.POST['path'])
    else:
        return redirect('/')


@login_required
def delete_course_from_program(request,p_id,c_id):
    course_id = decrypt(c_id)
    program_id = decrypt(p_id)
    if ProgramCourseMapping.objects.filter(program_id=program_id,course_id=course_id).exists():
        ProgramCourseMapping.objects.filter(program_id=program_id,course_id=course_id).delete()
        messages.success(request, 'Deleted Successfully')
        if Programs.objects.filter(id=program_id,program_type=6).exists():
            return redirect('pcmi_minor_program_detail', p_id)
        else:
            return redirect('pcmi_program_detail',p_id)
    else:
        return redirect('/')

@login_required
def program_course_specific_outcome_delete(request):
    if request.method == 'POST':
        ProgramSpecificOutcome.objects.filter(pk=request.POST['pso_pk']).delete()
        messages.success(request, 'Deleted Successfully')
        return redirect(request.POST['path'])
    else:
        return redirect('/')


@login_required
@group_required('PCMI')
def course_preview_by_pcmi(request,p_id,c_id):
    course_id = decrypt(c_id)
    program_id = decrypt(p_id)
    program=Programs.objects.get(id=program_id)

    course_details = Course.objects.get(id=course_id)
    course_syllabus = get_syllabus(request, course_id, )
    course_book_details = get_course_book_details(request, course_id)
    references_details = get_ref_details(request, course_id)
    journal_details = get_journal_details(request, course_id)
    website_details = get_website_details(request, course_id)
    course_outcomes = CourseOutcome.objects.filter(course_id=course_id).values('id', 'course_outcome')
    pedagogy_tools = PedagogyTools.objects.values('id', 'name')
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values('topic','syllabus_type__name')
    course_owner=CourseUserMapping.objects.filter(is_active=1,to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()
    course_pre_requisite = CoursePrerequestiesMapping.objects.filter(course_id=course_id).values('id','prerequesti__course_name')

    program_course_outcome = ProgramCourseOutcome.objects.filter(course_id=course_id, program_id=program_id).values(
        'id', 'po')
    program_specific_outcome = ProgramSpecificOutcome.objects.filter(course_id=course_id, program_id=program_id).values(
        'id', 'pso')
    co_po_map = ProgramCourseCOPOMapping.objects.filter(course_id=course_id, program_id=program_id,
                                                        user_id=request.user.id).values()
    co_pso_map = ProgramCourseCOPSOMapping.objects.filter(course_id=course_id, program_id=program_id,
                                                          user_id=request.user.id).values()

    po_co_average=[]
    for i in program_course_outcome:
        s=0
        for j in co_po_map:
            if i['id'] == j['po_id']:
                s=s+j['po_points']
        po_co_average.append(int(s/len(program_course_outcome)))
    pso_co_average = []

    for i in program_specific_outcome:
        s = 0
        for j in co_pso_map:
            if i['id'] == j['pso_id']:
                s = s + j['pso_points']
        pso_co_average.append(int(s / len(program_course_outcome)))


    context = {'course_id': encrypt(course_details.id),'po_co_average':po_co_average,'pso_co_average':pso_co_average,'c_id':course_id,'p_id':p_id,
               'course_details': course_details, 'active_step': course_details.active_step,'practical_syllabus':practical_syllabus,
               'course_syllabus': course_syllabus,'program':program,
               'course_book_details': course_book_details, 'references_details': references_details,
               'course_outcomes': course_outcomes,'pedagogy_tools':pedagogy_tools,'course_owner':course_owner,
               'course_pre_requisite':course_pre_requisite,
               'journal_details':journal_details,'website_details':website_details,'program_specific_outcome':program_specific_outcome,
               'program_course_outcome':program_course_outcome,'co_po_map':co_po_map,'co_pso_map':co_pso_map}
    return render(request, 'pcmi/course_preview.html',context)


@csrf_exempt
@login_required
@group_required('PCMI')
def pcmi_co_po_pso_save(request, course_id):
    course_id = decrypt(course_id)
    if request.method == "POST":
        try:
            course_id = request.POST['course_id']
            program_id = request.POST['program_id']
            co_id=request.POST.getlist('co_id')
            po_id=request.POST.getlist('po_id')
            po=request.POST.getlist('po')
            pso_id=request.POST.getlist('pso_id')
            pso=request.POST.getlist('pso')
            p_c = ProgramCourseOutcome.objects.filter(course_id=course_id, program_id=program_id,user_id=request.user.id).values()


            po_id_ids = []
            po_id_chunk_size = len(p_c)
            for i in range(0, len(po_id), po_id_chunk_size ):
                po_id_ids.append(po_id[i:i + po_id_chunk_size ])

            po_points = []
            po_points_chunk_size = len(p_c)
            for i in range(0, len(po), po_points_chunk_size):
                po_points.append(po[i:i + po_points_chunk_size])

            for i,j,z in  zip(co_id,po_id_ids,po_points):
                for k in range(len(j)):
                    po_points = None
                    if z[k]!='':
                        po_points=z[k]
                    values = {'course_id':course_id, 'program_id':program_id,'co_id':i,'po_id':j[k],'user_id':request.user.id,'po_points':po_points}
                    ProgramCourseCOPOMapping.objects.update_or_create(course_id=course_id, program_id=program_id,co_id=i,po_id=j[k],user_id=request.user.id,
                                                                                                defaults=values)
            ProgramCourseCOPOMapping.objects.filter(course_id=course_id, program_id=program_id,user_id=request.user.id,po_points=None).delete()

            ps_o = ProgramSpecificOutcome.objects.filter(course_id=course_id, program_id=program_id,user_id=request.user.id).values()
            pso_id_ids = []
            pso_id_chunk_size = len(ps_o)
            for i in range(0, len(pso_id), pso_id_chunk_size):
                pso_id_ids.append(pso_id[i:i + pso_id_chunk_size])

            pso_points = []
            pso_points_chunk_size = len(ps_o)
            for i in range(0, len(pso), pso_points_chunk_size):
                pso_points.append(pso[i:i + pso_points_chunk_size])

            for i,j,z in  zip(co_id,pso_id_ids,pso_points):
                for k in range(len(j)):
                    pso_points = None
                    if z[k]!='':
                        pso_points=z[k]
                    values = {'course_id':course_id, 'program_id':program_id,'co_id':i,'pso_id':j[k],'user_id':request.user.id,'pso_points':pso_points}
                    ProgramCourseCOPSOMapping.objects.update_or_create(course_id=course_id, program_id=program_id,co_id=i,pso_id=j[k],user_id=request.user.id,
                                                                                                defaults=values)
            ProgramCourseCOPSOMapping.objects.filter(course_id=course_id, program_id=program_id,user_id=request.user.id,pso_points=None).delete()

            messages.success(request,'Updated Successfully')
            return redirect(request.POST['path'])
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            return redirect(request.POST['path'])

@login_required
def minor_program_mapping(request,p_id):
    p_id = decrypt(p_id)
    program=Programs.objects.filter(id=p_id).values('id','program_type_id','program_type_id__type','name','department')
    if program:
        program_assign_details = ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,to_user_group_id=5,is_active=1).\
                                                                                    values('user_id','is_edit','program_status_level_id').last()
        if program_assign_details:
            program_level = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level', 'level_id').order_by('level__level')
            dept =program[0]['department']
            programs_data = ProgramDepartmentMapping.objects.filter(department=dept,program__program_type_id=6).values('program_id','program__name','program__program_type__type')
            for i in programs_data:
                course_ids=ProgramCourseMapping.objects.filter(program_id=i['program_id']).values_list('course_id',flat=True)
                i['course_data']=get_course_data(list(course_ids))

            #print(programs_data)
            program_user_mapping = None
            is_edit = 0
            if ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id, is_edit=1).exists():
                program_user_mapping = ProgramUserMapping.objects.filter(program_id=p_id, to_user_id=request.user.id,is_edit=1).values().last()
                if program_user_mapping['program_status_level_id'] in [1,4] and program_user_mapping['is_edit'] == 1:
                    is_edit=1

            course_category=CourseCategory.objects.get(id=9)

            mapped_minor_prograns=MinorCoreProgramMapping.objects.filter(category_id=9, program_id=p_id).values_list('mapped_program_id',flat=True)

            context = {'levels': program_level,'p_id':p_id,'program_assign_details':program_assign_details,'program':program,'programs_data':programs_data,
                        'program_id':encrypt(p_id),'is_edit':is_edit,'category_id':9,'enc_program_id':encrypt(p_id),'course_category':course_category,
                       'mapped_minor_prograns':list(mapped_minor_prograns)
                       }
            return render(request, 'pcmi/minor_program_mapping.html', context)
        else:
            return redirect('/')
    else:
        return redirect('/')

@csrf_exempt
def minor_core_programs_mapping(request):
    if request.method == 'POST':
        choosen_program_id = request.POST['choosen_program_id']
        program_id = request.POST['program_header_id']
        status = request.POST['status']
        course_category_id = request.POST['category_id']
        if status == '1':
            MinorCoreProgramMapping.objects.create(category_id=course_category_id, created_by_id=request.user.id, mapped_program_id=choosen_program_id, program_id=program_id)
        elif status == '0':
            MinorCoreProgramMapping.objects.filter(category_id=course_category_id,mapped_program_id=choosen_program_id, program_id=program_id).delete()
        return JsonResponse({'status': 200})
    else:
        return JsonResponse({'status': 500})

@login_required
@group_required('PCMI')
def delete_minor_core_program(request,p_id,mp_id):
    mp_id = decrypt(mp_id)
    program_id = decrypt(p_id)
    if MinorCoreProgramMapping.objects.filter(program_id=program_id, mapped_program_id=mp_id).exists():
        MinorCoreProgramMapping.objects.filter(program_id=program_id, mapped_program_id=mp_id).delete()
        messages.success(request, 'Deleted Successfully')
        return redirect('pcmi_program_detail', p_id)
    else:
        return redirect('/')

@login_required
@group_required('PCMI')
def add_group(request):
    if request.method == 'POST':
        s=request.POST
        course_category_id = None
        if 'course_category_id' in s:
            course_category_id = s['course_category_id']
            if not request.POST['group_id']:
                insert=ProgramCourseGroup.objects.create(group_name=s['group_name'],symbol=request.POST['symbol'],
                    choice_count=s['choice_count'],category_id=course_category_id,created_by_id=request.user.id,program_id=s['program_id'])
                course=[]
                basket=[]
                print(request.POST.getlist('course_id'),s['program_id'])
                for i in request.POST.getlist('course_id'):
                    l=i.split("-")
                    if l[0]=='course':
                        course.append(l[1])
                    elif l[0]=='basket':    
                         basket.append(l[1])
                if course:
                    ProgramCourseMapping.objects.filter(program_id=s['program_id'],course_id__in=course).update(group_id=insert.id)
                if basket:
                    ProgramCourseBasket.objects.filter(program_id=s['program_id'],id__in=basket).update(group_id=insert.id)
                
            # if ProgramCourseBasket.objects.filter(id=request.POST['basket_id']).exists():
                # ProgramCourseBasket.objects.filter(id=request.POST['basket_id']).update(basket_name=s['basket_name'],L=L, T=T, P=P, S=S, J=J, C=int(C),
                    # course_type_id=request.POST['course_type'],choice_count=s['choice_count'],level_of_course_id=request.POST['course_level'])
            
            messages.success(request, 'Basket Created Successfully')
        return redirect(s['path'])
    return redirect('/')

@login_required
def program_structure_upload(request):
    if request.method == 'POST':
        try:
            temp_file = 'data_upload'
            handle_uploaded_file(request.FILES['data'], temp_file)
            wb = xlrd.open_workbook('media/' + temp_file + '.xlsx')
            sheet = wb.sheet_by_index(0)
            insert_obj=[]
            course_header_id=Course.objects.filter(program_id=request.POST.get('program_id'),level_of_course_id = request.POST.get('level_of_course')).values_list('course_header_id')
            Course.objects.filter(program_id=request.POST.get('program_id'),level_of_course_id = request.POST.get('level_of_course')).delete()
            CourseHeader.objects.filter(id__in = course_header_id).delete()
            CourseCampusMapping.objects.filter(course__program_id=request.POST.get('program_id')).delete()

            for i in range(1, sheet.nrows):
                course_header=CourseHeader.objects.create(program_id=request.POST.get('program_id'),user_id=request.user.id,status=1,created = datetime.now())
                insert_obj.append(Course(created = datetime.now(),course_name=sheet.cell_value(i, 1),
                                         course_type_id = CourseType.objects.filter(code=sheet.cell_value(i, 2)).values('id'),
                                         course_category_id = CourseCategory.objects.filter(short_code=sheet.cell_value(i, 3)).values('id'),created_by_id=request.user.id,
                                            L = int(sheet.cell_value(i, 4)),T = int(sheet.cell_value(i, 5)),
                                         P=int(sheet.cell_value(i, 6)), J=int(sheet.cell_value(i, 7)),S=int(sheet.cell_value(i, 8)),C=int(sheet.cell_value(i, 9)),
                                         level_of_course_id= request.POST.get('level_of_course'),version=1.0,version_status=0,
                                         program_id=request.POST.get('program_id'),course_header_id=course_header.id,total_no_of_contact_hours=int(sheet.cell_value(i, 9))*15))
            insert = Course.objects.bulk_create(objs=insert_obj)
            course_id = Course.objects.filter(program_id=request.POST.get('program_id')).values('id')
            campus = ProgramCampusMapping.objects.filter(program_id=request.POST.get('program_id')).values('campus_id')
            for c in course_id:
                for m in campus:
                    CourseCampusMapping.objects.create(course_id=c['id'],campus_id=m['campus_id'],created = datetime.now(),user_id=request.user.id)
            messages.success(request,'Data Stored Successfully')
            return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e)+'--- Course Structure', user_id=request.user.id)
            return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))
    else:
        return redirect('pcmi_program_detail',encrypt(request.POST.get('program_id')))

@login_required
def program_forward(request,p_id):
    if request.method == 'POST':
        try:
            program_status_level_id= None
            if ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,program_status_level_id__in=[1,4]).exists():
                ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,program_status_level_id__in=[1,4]).update(is_edit=0)
                if request.POST.get('program_status_level_id') == '4':
                    program_status_level_id=5
                if request.POST.get('program_status_level_id') == '1':
                    program_status_level_id=2
                ProgramUserMapping.objects.create(program_id=p_id,is_edit=1,user_id=request.user.id,to_user_id=request.POST.get('bos_user_id'),
                                                  program_status_level_id=program_status_level_id,created=datetime.now(),to_user_group_id=6,
                                                  user_group_id=5
                                                  )
                email = User.objects.filter(id=request.POST.get('bos_user_id')).values('email', 'id', 'first_name')
                progm = Programs.objects.get(id=p_id)
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Curriculum for "+progm.name+" has been prepared and is submitted for your Approval/Suggestions"
                message = render_to_string('pcmi/email_templates/program_structure_forward_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'program':progm.name ,

                })
                e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
                EmailStatus.objects.create(hint='PCMI Program forward to BOSC', message=message,to_user_email=email[0]['email'], to_user_id=email[0]['id'],user_id=request.user.id)
                messages.success(request, 'Forwarded Successfully..')
                return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))

    return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))

@login_required
def course_assign(request):
    if request.method == "POST":
        try:
            csm = request.POST.getlist('csmc')
            csm.insert(0, request.POST.get('csmi'))
            members = User.objects.filter(id__in=csm).values('first_name','id')
            csm_list = [i['first_name']for j in csm for i in members if int(j) == i['id']]
            course = Course.objects.get(id=request.POST.get('course_id'))
            if not UserGroups.objects.filter(user_id=request.POST.get('csmi'), group_id=3).exists():
                UserGroups.objects.create(user_id=request.POST.get('csmi'), group_id=3, is_active=0, is_block=0,
                                          is_default=0, role='CSMI')

            CourseUserMapping.objects.create(created=datetime.now, is_edit=0, course_id=request.POST.get('course_id'), course_status_level_id=1,
                                             to_user_id=request.POST.get('csmi'), user_id=request.user.id,to_user_group_id=3,user_group_id=5,course_header_id=course.course_header_id)
            
            if not UserGroups.objects.filter(user_id=request.POST.get('csmc'), group_id=2).exists():
                UserGroups.objects.create(user_id=request.POST.get('csmc'), group_id=2, is_active=0, is_block=0,
                                          is_default=0, role='CSMM')
            CourseUserMapping.objects.create(created=datetime.now, is_edit=1, course_id=request.POST.get('course_id'), course_status_level_id=1,
                                             to_user_id=request.POST.get('csmc'), user_id=request.user.id,to_user_group_id=2,user_group_id=5,course_header_id=course.course_header_id)
            for j in range(len(csm)):
                email = User.objects.filter(id=csm[j]).values('email', 'id', 'first_name')
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Assigned as a team member for the Course Syllabus Modification committee for "+course.course_name+"."
                message = render_to_string('pcmi/email_templates/course_assign_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'members': csm_list
                })
                e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, "Assigned Successfully..")
            return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))

    return redirect('pcmi_program_detail', encrypt(request.POST.get('program_id')))

@csrf_exempt
@login_required
def get_csm_incharges(request):
    if request.method =="POST":
        keyword=request.POST.get('term')
        users = User.objects.filter(
                Q(is_active=1),
                Q(first_name__icontains=keyword)
                | Q(username__icontains=keyword) | Q(email__icontains=keyword)).exclude(groups__name__in=[ 'PAB']).values('id','first_name','username','email',
                                                                                            'emp_id','campus','institution','department')

        return JsonResponse(list(users),safe=False)
    else:
        return JsonResponse({'status':500})

@login_required
@group_required('PCMI')
def course_preview_pcmi(request,course_id):
    course_id = decrypt(course_id)
    if not Course.objects.filter(id=course_id).exists():
        return redirect('/')
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
    practical_syllabus = CourseSyllabusPractical.objects.filter(course_id=course_id).values('topic','syllabus_type__name').order_by('id')
    course_owner=CourseUserMapping.objects.filter(to_user_group_id=2,course_id=course_id).values('to_user__first_name','to_user__username','to_user__dept_code_id','to_user__designation','to_user__dept_code__dept_inst').last()
    co_po_psos = []
    count = 0
    if co_po_pso:
        for co in course_outcome:
            co['po'] = co_po_pso[count]
            co_po_psos.append(co)
            count = count + 1
    copo_average = co_po_pso_average(request, co_po_pso, course_id)
    course_timeline = []
    course_timeline_actions = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id','user__first_name', 'user_id','course_status_level__title',
                               'to_user__first_name','user__image','to_user_group__description','user_group__description','comment').order_by('-id')

    course_view_access=None
    if course_timeline_actions.filter(course_status_level_id=4,to_user_id=request.user.id,is_active=1).exists():
        course_view_access=1
    pending_timeline = CourseUserMapping.objects.filter(course_id=course_id).values('created', 'to_user_id','course_status_level__title',
                        'to_user__first_name', 'to_user_group__description','user_group__description','to_user__image', 'comment').last()
    course_timeline.append(pending_timeline)
    course_timeline.extend(course_timeline_actions)
    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=5,is_edit=1,to_user_id=request.user.id).exists():
        is_edit = 1
    elif ProgramUserMapping.objects.filter(program_id=course_details.program_id,program_status_level_id__in=[13,16],to_user_id=request.user.id,to_user_group_id=5,is_edit=1).exists():
        is_edit = 1
    else:
        is_edit = 0

    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=3,to_user_id=request.user.id,course_status_level_id__in=[5,6],is_edit=1).exists():
        edit = 1
    else:
        edit = 0

    if CourseUserMapping.objects.filter(course_id=course_id, to_user__groups=5,to_user_id=request.user.id,course_status_level_id=4).exists():
        course_edit = 1
    else:
        course_edit = 0
    context = {'course_id': encrypt(course_details.id), 'dept': dept,'practical_syllabus':practical_syllabus,'course_view_access':course_view_access,
               'course_type': course_type, 'level_of_course': level_of_course, 'course_category': course_category,
               'course_details': course_details, 'active_step': course_details.active_step,
               'course_syllabus': course_syllabus,'p_id':encrypt(course_details.program_id),
               'course_book_details': course_book_details, 'references_details': references_details, 'course': course,
               'course_outcome': course_outcome,'is_edit':is_edit,'copo_average':copo_average,
               'pso': pso,  'co_po_pso': co_po_psos,'course_timeline':course_timeline,'course_owner':course_owner,
               'pedagogy_tools': pedagogy_tools,'course_edit':course_edit,'edit':edit,'journal_details':journal_details,'website_details':website_details}
    return render(request, 'pcmi/preview.html',context)


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

@login_required
def course_structure_approve(request,c_id):
    c_id=decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id,to_user_id=request.user.id,course_status_level_id=4).exists():
                bosc_user = CourseUserMapping.objects.filter(course_id=c_id).values('course__program__user')
                CourseUserMapping.objects.create(course_id=c_id,to_user_id=bosc_user[0]['course__program__user'],user_id=request.user.id,course_status_level_id=5,is_edit=1,
                                                 course_header_id = course.course_header_id,to_user_group_id=6,user_group_id=5)
                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                 course_status_level_id=4).update(is_edit=0)
                email = User.objects.filter(id=bosc_user[0]['course__program__user']).values('email', 'id', 'first_name')
                course = Course.objects.get(id=c_id)
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Invite to Review Program structure and syllabus"
                message = render_to_string('pcmi/email_templates/course_structure_approve_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                })
                e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, "Approved.....")
            return redirect('course_preview_pcmi', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_pcmi', encrypt(c_id))
    return redirect('course_preview_pcmi',encrypt(c_id))

@login_required
@group_required("PCMI")
def forward_program_to_bosc_by_pcmi(request,p_id):
    p_id=decrypt(p_id)
    if request.method == "POST":
        try:
            bosc_user = Programs.objects.filter(id=p_id).values('user_id')
            to_user_group = UserGroups.objects.filter(user_id=bosc_user[0]['user_id'], is_active=1, is_block=0).values('group_id')
            user_group = UserGroups.objects.filter(user_id=request.user.id, is_active=1, is_block=0).values('group_id')
            ProgramUserMapping.objects.create(created=datetime.now(),is_edit=1,program_id=p_id,program_status_level_id=6,
                                              to_user_id=bosc_user[0]['user_id'],user_id=request.user.id,to_user_group_id=to_user_group[0]['group_id'],
                                              user_group_id=user_group[0]['group_id'])
            ProgramUserMapping.objects.filter(program_id=p_id,to_user_id=request.user.id,is_edit=1).update(is_edit=0)

            email = User.objects.filter(id=bosc_user[0]['user_id']).values('email', 'id', 'first_name')
            progm = Programs.objects.get(id=p_id)
            sender = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            mail_subject = "Curriculum and syllabus of "+progm.name+" is prepared and is submitted for your Approval/Suggestions"
            message = render_to_string('pcmi/email_templates/program_forward_bosc_email.html', {
                'email': encrypt(email[0]['email']),
                'domain': current_site.domain,
                'guest_firstname': email[0]['first_name'],
                'program': progm.name,

            })
            e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            EmailStatus.objects.create(hint='PCMI courses forward to BOSC', message=message, to_user_email=email[0]['email'],to_user_id=email[0]['id'], user_id=request.user.id)
            messages.success(request, 'Forwarded Successfully..')
            return redirect('/pcmi/pcmi_program_detail/'+encrypt(p_id))
        except Exception as e:
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('/pcmi/pcmi_program_detail/' + encrypt(p_id))
    else:
        return redirect('/pcmi/pcmi_program_detail/' + encrypt(p_id))

@login_required
@group_required("PCMI")
def course_structure_need_more(request,c_id):
    c_id=decrypt(c_id)
    if request.method == 'POST':
        course = Course.objects.get(id=c_id)
        try:
            if CourseUserMapping.objects.filter(course_id=c_id,to_user_id=request.user.id,course_status_level_id=4,is_active=1).exists():
                csmi_user = CourseUserMapping.objects.filter(course_id=c_id,to_user_id=request.user.id,course_status_level_id=4,is_active=1).values('id','user_id').order_by('-id')
                CourseUserMapping.objects.create(course_id=c_id,to_user_id=csmi_user[0]['user_id'],user_id=request.user.id,course_status_level_id=6,
                                                comment= request.POST.get('csmi_message'),is_edit=1,course_header_id=course.course_header_id,
                                                to_user_group_id=3,user_group_id=5
                                                )
                CourseUserMapping.objects.filter(course_id=c_id, to_user_id=request.user.id,
                                                 course_status_level_id=4).update(is_edit=0)
                email = User.objects.filter(id=csmi_user[0]['user_id']).values('email', 'id', 'first_name')
                course = Course.objects.get(id=c_id)
                sender = settings.EMAIL_HOST_USER
                current_site = get_current_site(request)
                mail_subject = "Suggestions regarding the syllabus of "+course.course_name
                message = render_to_string('pcmi/email_templates/pcmi_sugge_csmi_email.html', {
                    'email': encrypt(email[0]['email']),
                    'domain': current_site.domain,
                    'guest_firstname': email[0]['first_name'],
                    'course_code': course.course_code,
                    'course_name': course.course_name,

                })
                e = send_html_mail(mail_subject, message, [email[0]['email']], sender)
            messages.success(request, 'Forwarded Successfully..')
            return redirect('course_preview_pcmi', encrypt(c_id))
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), user_id=request.user.id)
            return redirect('course_preview_pcmi', encrypt(c_id))
    return redirect('course_preview_pcmi',encrypt(c_id))
    
    
@login_required
@group_required("PCMI")
def add_course(request,program_id):
    p_id = decrypt(program_id)
    course_type = CourseType.objects.filter(status=1).values('id', 'name')
    level_of_course = ProgramLevelMapping.objects.filter(program_id=p_id).values('level__level','level')
    course_category = CourseCategory.objects.values('id', 'category')
    user_di = User.objects.values('dept_code__dept_code','institution','campus').distinct()
    campus = ProgramCampusMapping.objects.filter(program=p_id).values('campus_id','campus__name','campus__address')
    dept = set([j['dept_code__dept_code'] for j in user_di if j['dept_code__dept_code'] != None])
    inst = set([j['institution'] for j in user_di for k in campus if j['institution'] != None and k['campus__address']==j['campus']])
    campus_det = Campus.objects.values('id','name')
    if request.method == 'POST':
        try:
            campus = request.POST.getlist('campus')
            dept = request.POST.getlist('dept')
            inst = request.POST.getlist('inst')
            course_header = CourseHeader.objects.create(program_id=p_id, user_id=request.user.id,status=1, created=datetime.now())
            L = 0
            T = 0
            P = 0
            S = 0
            J = 0
            C = 0
            if request.POST['type_of_course'] == '1':
                L = request.POST['L']
                T = request.POST['T']
                C = int(L)+int(T)
            elif request.POST['type_of_course'] == '2':
                P = request.POST['P']
                C=int(P)*0.5
            elif request.POST['type_of_course'] == '3':
                L = request.POST['L']
                T = request.POST['T']
                P = request.POST['P']
                C=int(L)+int(T)+(int(P)*0.5)
            elif request.POST['type_of_course'] == '4':
                J = int(request.POST['J'])
                C=int(request.POST['C'])
            elif request.POST['type_of_course'] == '5':
                S = request.POST['S']
                C=int(S)
            elif request.POST['type_of_course'] == '6':
                L = request.POST['L']
                T = request.POST['T']
                P = request.POST['P']
                S = request.POST['S']
                J =request.POST['J']
                C=0    
            insert = Course.objects.create(course_name=request.POST['course_title'],
                                  course_type_id=request.POST['type_of_course'],
                                  level_of_course_id=request.POST['level_of_course'],
                                  course_category_id=request.POST['course_category'],
                                  L=L, T=T,P=P, S=S,J=J, C=int(C),
                                  total_no_of_contact_hours=int(C)*15,
                                  created=datetime.now(), created_by_id=request.user.id,
                                  course_header_id=course_header.id,
                                  program_id=p_id
                                  )
                                  
            for i in range(len(dept)):
                CourseDepartmentMapping.objects.create(department = dept[i] ,course_id = insert.id ,
                                       created=datetime.now(),user_id = request.user.id )
            for k in range(len(inst)):
                CourseInstituteMapping.objects.create(institute= inst[k], course_id=insert.id,
                                                   created=datetime.now(), user_id=request.user.id)
            for j in range(len(campus)):
                CourseCampusMapping.objects.create(campus_id = campus[j],course_id = insert.id ,
                                       created=datetime.now(),user_id = request.user.id )
            messages.success(request, "Created Successfully..")
            return redirect('pcmi_program_detail', program_id)
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e)+'--Course Create', info=request.POST, user_id=request.user.id)
            return render(request,'pcmi/add_course.html',{'course_type':course_type,'level_of_course':level_of_course,'course_category':course_category,'p_id':program_id,
                                                                    'campus':campus,'dept':dept,'inst':inst,'campus_det':campus_det})
    return render(request, 'pcmi/add_course.html',{'course_type':course_type,
                                                   'level_of_course':level_of_course,'course_category':course_category,'p_id':program_id,'campus':campus,
                                                          'dept':dept,'inst':inst,'campus_det':campus_det})

@csrf_exempt
@login_required
def get_campus(request):
    if request.method =="POST":
        keyword=request.POST.get('term')
        campus = Campus.objects.filter(
                 Q(name__icontains=keyword)).values('id','name')
        return JsonResponse(list(campus),safe=False)
    else:
        return JsonResponse({'status':500})

@csrf_exempt
def get_institution_by_campus(request):
    a = {}
    if request.method == "POST":
        campus=request.POST.getlist('campus')[0].split(',')
        institutions =CampusInstitutionMapping.objects.filter(campus_id__in=campus).values('institution__id','institution__institution_code').distinct()
        a = {}
        a['institutions'] = list(institutions)
    return JsonResponse(a, safe=False)


@csrf_exempt
def get_dept_by_institution(request):
    a = {}
    if request.method == "GET":
        inst=request.GET.getlist('inst')[0].split(',')
        campus=request.GET.getlist('campus')[0].split(',')
        c = Campus.objects.filter(id__in=campus).values_list('address')
        p=User.objects.filter(campus__in=c,institution__in=inst).exclude(dept_code_id=None).values('dept_code__dept_code','dept_code__dept_inst').distinct()
        a['dept'] = list(p)

    return JsonResponse(a, safe=False)


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