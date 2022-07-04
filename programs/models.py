from django.db import models
from user_management.models import *
from course_management.models import *



class ProgramStatusLevels(models.Model):
    title = models.CharField(max_length=200)
    class Meta:
        db_table = 'program_status_levels'

class ProgramType(models.Model):
    type = models.CharField(max_length=100)
    status = models.BooleanField(default=1)
    code = models.CharField(max_length=20,null=True)
    class Meta:
        db_table = 'program_type'

class ProgramLevel(models.Model):
    level = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    program_type = models.ForeignKey(ProgramType,on_delete=models.CASCADE)
    status = models.BooleanField(default=1)
    class Meta:
        db_table = 'program_level'

class ProgramCategory(models.Model):
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=1)
    class Meta:
        db_table = 'program_category'
class Programs(models.Model):
    name = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program_type = models.ForeignKey(ProgramType, on_delete=models.CASCADE,null=True)
    program_category = models.ForeignKey(ProgramCategory, on_delete=models.CASCADE,default=1)
    modified = models.DateTimeField(null=True)
    modified_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='program_modified_by')
    department = models.TextField(null=True)

    class Meta:
        db_table = 'programs'

class ProgramLevelMapping(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    level = models.ForeignKey(ProgramLevel,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True,null=True)
    class Meta:
        db_table = 'program_level_mapping'



class ProgramCampusMapping(models.Model):
    program = models.ForeignKey(Programs,on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)
    class Meta:
        db_table = 'program_campus_mapping'

class ProgramDepartmentMapping(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    department = models.CharField(max_length=255,null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'program_department_mapping'

class ProgramInstituteMapping(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    institute = models.CharField(max_length=255,null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'program_institute_mapping'



class ProgramUserMapping(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='program_created_user_id',null=True)
    program_status_level= models.ForeignKey(ProgramStatusLevels,on_delete=models.CASCADE,related_name='program_status_level',null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    is_edit = models.IntegerField(null=True)
    comment = models.TextField(null=True)
    to_user_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name='prog_to_user_group')
    user_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(null=True,default=1)
    class Meta:
        db_table = 'program_user_mapping'

