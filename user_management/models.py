from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

# Group.add_to_class('priority',models.IntegerField(null=True))
Group.add_to_class('description',models.CharField(max_length=100,null=True))




class Campus(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    campus_code = models.CharField(max_length=10,null=True)
    status = models.BooleanField(default=0)
    icon = models.ImageField(upload_to='campus_icons', null=True)
    class Meta:
        db_table = "u_campus"
        
class Institutions(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=0)
    institution_code=models.CharField(max_length=100,null=True)
    
    class Meta:
        db_table = "u_institutions"
    def __str__(self):
        return self.name

class CampusInstitutionMapping(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institutions, on_delete=models.CASCADE)
    class Meta:
        db_table = "u_campus_institution_mapping"


class UCourse(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=0)
    full_name=models.TextField(max_length=100,null=True)
    
    class Meta:
        db_table = "u_courses"
    def __str__(self):
        return self.name

class CampusInstitutionCourseMapping(models.Model):
    institution = models.ForeignKey(Institutions, on_delete=models.CASCADE)
    course = models.ForeignKey(UCourse, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE,null=True)
    
    class Meta:
        db_table = "u_campus_institution_course_mapping"
        
class Departments(models.Model):
    name = models.CharField(max_length=70)
    code = models.CharField(max_length=5)
    class Meta:
        db_table = 'u_department' 
        


class DepartmentInstituteCodes(models.Model):
    name = models.CharField(max_length=70, null=True)
    dept_inst = models.CharField(max_length=70)
    dept_code = models.CharField(max_length=5)
    status=models.BooleanField(default=1)
    class Meta:
        db_table = 'u_department_institute_code' 
        
class CampusInstitutionCourseDepartmentMapping(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institutions, on_delete=models.CASCADE)
    course = models.ForeignKey(UCourse, on_delete=models.CASCADE)
    department = models.ForeignKey(DepartmentInstituteCodes, on_delete=models.CASCADE)
    class Meta:
        db_table = "u_campus_institution_course_department_mapping"
class User(AbstractUser):
    phone = models.BigIntegerField(null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=30)
    gender=models.CharField(max_length=30)
    designation=models.CharField(max_length=100,null=True)
    emp_id=models.CharField(max_length=15)
    dob=models.CharField(max_length=12)
    campus = models.CharField(max_length=100,null=True)
    institution = models.CharField(max_length=100,null=True)
    department = models.CharField(max_length=100,null=True)
    dept_email = models.EmailField(null=True)
    image = models.FileField(upload_to='media/user/profileimages',null=True)
    dept_code = models.ForeignKey(DepartmentInstituteCodes, on_delete=models.CASCADE,null=True)
    address = models.TextField(null=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
        through="UserGroups"
    )
    class Meta:
        db_table = "users"
    def __str__(self):
        return self.id

# User.group.add_to_class('description',models.CharField(max_length=100,null=True))
class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    #createdby = models.ForeignKey(User, related_name="user_group_created", on_delete=models.CASCADE)
    # organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = "user_groups"
    def __str__(self):
        return self.id


class UserGroupsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_expired=models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_history_created_by')
    modified = models.DateTimeField(null=True)
    modifiedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_history_modified_by',null=True)
    class Meta:
        db_table = "user_groups_history"

    def __str__(self):
        return self.id


class UserAuthLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address=models.GenericIPAddressField()
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True)
    session_key = models.TextField(null=True)
    login_data = models.TextField(null=True)
    class Meta:
        db_table = "user_auth_logs"

class ErrorLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    log=models.TextField(null=True)
    info=models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "error_logs"
        
class BoschairInstituteMapping(models.Model):
    school = models.TextField()
    institute = models.TextField()
    dept_code = models.ForeignKey(DepartmentInstituteCodes, on_delete=models.CASCADE,null=True)
    bos_chair = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField()
    active_from_date = models.DateTimeField(auto_now_add=True)
    active_to_date = models.DateTimeField(auto_now_add=True,null=True)
    class Meta:
        db_table = 'bos_chair_institute_mapping'



class EmailStatus(models.Model):
    hint= models.TextField(null=True)
    message = models.TextField(null=True)
    to_user_email = models.EmailField(null=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='email_user')
    to_user=models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='email_to_user')
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "email_status"