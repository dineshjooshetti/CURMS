from django.db import models
from user_management.models import *
from programs.models import *


class CourseDegree(models.Model):
    name = models.CharField(max_length=30)
    status = models.IntegerField(default=1)
    class Meta:
        db_table = 'course_degree'

class CourseAdmittedBatch(models.Model):
    name = models.CharField(max_length=30)
    status = models.IntegerField(default=1)
    class Meta:
        db_table = 'course_admitted_batch'


class CourseType(models.Model):
    name = models.CharField(max_length=40)
    code = models.CharField(max_length=20)
    status = models.IntegerField(default=1)
    class Meta:
        db_table = 'course_course_type'

class CourseLevels(models.Model):
    level = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    status = models.IntegerField(default=1)
    course_type_id=models.ForeignKey(CourseType,on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = 'course_levels'

class CourseCategory(models.Model):
    category = models.CharField(max_length=70)
    code = models.CharField(max_length=20)
    status = models.IntegerField(default=1)
    short_code = models.CharField(max_length=20, null=True)
    priority = models.IntegerField(null=True)
    class Meta:
        db_table = 'course_course_category'

class CourseHeader(models.Model):
    status = models.BooleanField(default=1)
    program_status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_user_id')
    program = models.ForeignKey(Programs, on_delete=models.CASCADE,null=True)

    class Meta:
        db_table = 'course_course_header'
        
class CourseStatusLevels(models.Model):
    title = models.CharField(max_length=200)
    class Meta:
        db_table = 'course_status_levels'
class Course(models.Model):
    admitted_batch = models.ForeignKey(CourseAdmittedBatch, on_delete=models.CASCADE, null=True)
    degree = models.ForeignKey(CourseDegree, on_delete=models.CASCADE, null=True)
    course_header = models.ForeignKey(CourseHeader, on_delete=models.CASCADE, null=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE,null=True)
    program_type = models.ForeignKey(ProgramType, on_delete=models.CASCADE,null=True)
    course_name = models.TextField(null=True)
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE)
    level_of_course = models.ForeignKey(ProgramLevel, on_delete=models.CASCADE,null=True)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null=True)
    desc1 = models.TextField(null=True)
    instruction_plan = models.FileField(upload_to='media/course/', max_length=5000)
    instruction_plan_practical = models.FileField(upload_to='media/course/',null=True, max_length=5000)
    active_step = models.IntegerField(null=True)
    version = models.DecimalField(null=True,decimal_places=1,max_digits=4)
    version_status = models.BooleanField(default=0)
    total_no_of_contact_hours = models.TextField(null=True)
    L = models.TextField(null=True)
    T = models.TextField(null=True)
    P = models.TextField(null=True)
    S = models.TextField(null=True)
    J = models.TextField(null=True)
    C = models.TextField(null=True)
    pre_requisites = models.TextField(null=True)
    co_requisites = models.BooleanField(default=0)
    alternative_exposure = models.TextField(null=True)
    course_descrption = models.TextField(null=True)
    specific_instruction_objectives = models.TextField(null=True)
    co_requisite1 = models.TextField(null=True)
    co_requisite2 = models.TextField(null=True)
    co_requisite3 = models.TextField(null=True)
    co_requisite4 = models.TextField(null=True)
    co_requisite5 = models.TextField(null=True)
    pre_requisites_yes1 = models.TextField(null=True)
    pre_requisites_yes2 = models.TextField(null=True)
    pre_requisites_yes3 = models.TextField(null=True)
    pre_requisites_yes4 = models.TextField(null=True)
    pre_requisites_yes5 = models.TextField(null=True)
    course_code = models.CharField(max_length=100,null=True)
    practical_referance = models.JSONField(null=True)
    practical_topic_mapping = models.JSONField(null=True)
    project_topic = models.JSONField(null=True)
    course_outcome = models.JSONField(null=True)
    course_objectives = models.JSONField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_created_by')
    modified = models.DateTimeField(auto_now_add=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='course_modified_by')
    dept_code = models.ForeignKey(DepartmentInstituteCodes, on_delete=models.CASCADE, null=True)
    pass_fail = models.BooleanField(default=0)
    faculty = models.BooleanField(default=1)
    sdg=models.JSONField(null=True)
    sdg_description = models.TextField(null=True)
    form_type = models.IntegerField(null=True)
    status= models.ForeignKey(CourseStatusLevels,on_delete=models.CASCADE,null=True)
    
    class Meta:
        db_table = 'course'

class CourseCampusMapping(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course_campus_mapping'

class CourseDepartmentMapping(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    department = models.CharField(max_length=255,null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    c_i_c_d=models.ForeignKey(CampusInstitutionCourseDepartmentMapping,on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = 'course_department_mapping'

class CourseInstituteMapping(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    institute = models.CharField(max_length=255,null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course_institute_mapping'



class CoursePrerequestiesMapping(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    prerequesti = models.ForeignKey(Course, on_delete=models.CASCADE,related_name='course_prerequesting_mapping')
    created = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course_prerequesties_mapping'
class CourseCorequestiesMapping(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    corequesti = models.ForeignKey(Course, on_delete=models.CASCADE,related_name='course_corequesting_mapping')
    created = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course_corequesties_mapping'



class CourseUserMapping(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    course_header = models.ForeignKey(CourseHeader, on_delete=models.CASCADE, null=True)
    to_user = models.ForeignKey(User,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='course_created_user_id')
    course_status_level= models.ForeignKey(CourseStatusLevels,on_delete=models.CASCADE,related_name='course_status_level',null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    is_edit = models.IntegerField(null=True)
    comment = models.TextField(null=True)
    to_user_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name='cour_to_user_group')
    user_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(null=True,default=1)
    assigned_time=models.DateTimeField(null=True)
    class Meta:
        db_table = 'course_user_mapping'

class CourseOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_outcome = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course_outcome'
              


class CourseUnits(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    unit_no = models.IntegerField()
    class Meta:
        db_table = 'course_units'

class PedagogyTools(models.Model):
    name = models.CharField(max_length=50)
    class Meta:
        db_table = 'course_pedagogy_tools'


class CourseSyllabus(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    #course_unit = models.ForeignKey(CourseUnits, on_delete=models.CASCADE)
    unit_name = models.TextField()
    short_title = models.CharField(max_length=500)
    number_of_contact_hours = models.CharField(max_length=10)
    version = models.DecimalField(null=True, decimal_places=1, max_digits=4)
    outcome_1 = models.TextField(null=True)
    level_1 = models.TextField(null=True)
    outcome_2 = models.TextField(null=True)
    level_2 = models.TextField(null=True)
    outcome_3 = models.TextField(null=True)
    level_3 = models.TextField(null=True)
    outcome_4 = models.TextField(null=True)
    level_4 = models.TextField(null=True)
    outcome_5 = models.TextField(null=True)
    level_5 = models.TextField(null=True)
    pedagogy_tools = models.JSONField(null=True)
    #pedagogy_tool_1 = models.ForeignKey(PedagogyTools, on_delete=models.CASCADE, related_name='course_pedagogy_tool_1',null=True)
    #pedagogy_tool_2 = models.ForeignKey(PedagogyTools, on_delete=models.CASCADE, related_name='course_pedagogy_tool_2',null=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    course_unit = models.ForeignKey(CourseUnits, on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = 'course_syllabus'

class SyllabusType(models.Model):
    name = models.CharField(max_length=20)
    class Meta:
        db_table = 'course_syllabus_type'

class CourseSyllabusPractical(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    syllabus_type = models.ForeignKey(SyllabusType, on_delete=models.CASCADE)
    topic = models.TextField()
    version = models.DecimalField(null=True, decimal_places=1, max_digits=4)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course_syllabus_practical'

class CourseBooks(models.Model):
    title = models.TextField()
    author = models.TextField(null=True)
    publisher = models.TextField(null=True)
    place_of_publication = models.TextField(null=True)
    year = models.IntegerField(null=True)
    edition = models.TextField(null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    isbn = models.TextField(null=True)
    unit_mapping = models.TextField(null=True)
    class Meta:
        db_table = 'course_books'

class References(models.Model):
    title = models.TextField()
    author = models.TextField(null=True)
    publisher = models.TextField(null=True)
    place_of_publication = models.TextField(null=True)
    year = models.IntegerField(null=True)
    edition = models.TextField(null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    isbn = models.TextField(null=True)
    unit_mapping = models.TextField(null=True)
    class Meta:
        db_table = 'course_reference'

class CourseCoPoPso(models.Model):
    co = models.IntegerField()
    po1 = models.IntegerField(null=True)
    po2 = models.IntegerField(null=True)
    po3 = models.IntegerField(null=True)
    po4 = models.IntegerField(null=True)
    po5 = models.IntegerField(null=True)
    po6 = models.IntegerField(null=True)
    po7 = models.IntegerField(null=True)
    po8 = models.IntegerField(null=True)
    po9 = models.IntegerField(null=True)
    po10 = models.IntegerField(null=True)
    po11 = models.IntegerField(null=True)
    po12 = models.IntegerField(null=True)
    pso1 = models.IntegerField(null=True)
    pso2 = models.IntegerField(null=True)
    pso3 = models.IntegerField(null=True)
    pso4 = models.IntegerField(null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course_co_po_pso'


class JournalBooks(models.Model):
    title = models.TextField()
    author = models.TextField()
    year = models.TextField()
    doi_url = models.TextField()
    pages = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    unit_mapping = models.TextField()
    class Meta:
        db_table = 'course_journal_books'

class Websites(models.Model):
    name_website = models.TextField()
    last_accessed = models.DateTimeField(auto_now_add=True)
    website_url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    unit_mapping = models.TextField()
    class Meta:
        db_table = 'course_websites'



