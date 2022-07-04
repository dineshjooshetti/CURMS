from django.db import models
from user_management.models import *
from course_management.models import *
from .models import *


class ProgramCourseGroup(models.Model):
    group_name = models.TextField()
    symbol = models.TextField(null=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    course_count = models.IntegerField(null=True)
    choice_count = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'program_course_group'
        

class ProgramCourseBasket(models.Model):
    basket_name = models.TextField()
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    group = models.ForeignKey(ProgramCourseGroup, on_delete=models.CASCADE,null=True)
    course_count = models.IntegerField(null=True)
    credit_count = models.IntegerField(null=True)
    choice_count = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name='program_basket_created_by')
    L = models.TextField(null=True)
    T = models.TextField(null=True)
    P = models.TextField(null=True)
    S = models.TextField(null=True)
    J = models.TextField(null=True)
    C = models.TextField(null=True)
    level_of_course = models.ForeignKey(ProgramLevel, on_delete=models.CASCADE,null=True)
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = 'program_course_basket'



     
class ProgramCourseMapping(models.Model):
    basket = models.ForeignKey(ProgramCourseBasket, on_delete=models.CASCADE,null=True)
    group = models.ForeignKey(ProgramCourseGroup, on_delete=models.CASCADE,null=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    item_type = models.IntegerField(default=0)
    class Meta:
        db_table = 'program_course_mapping'
        

class ProgramSpecificOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE,null=True)
    pso = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'program_specific_outcome'


class ProgramCourseOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE,null=True)
    po = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'program_course_outcome'

class ProgramCategoryCountMapping(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    category= models.ForeignKey(CourseCategory,on_delete=models.CASCADE,null=True)
    #label_category= models.ForeignKey(null=True,related_name='course_label')
    label_category= models.JSONField(null=True)
    count= models.IntegerField()
    created = models.DateTimeField(auto_now_add=True,null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='program_course_category_created_by')
    class Meta:
        db_table = 'program_category_count_mapping'


class ProgramCourseCOPOMapping(models.Model):
    co = models.ForeignKey(CourseOutcome, on_delete=models.CASCADE)
    po = models.ForeignKey(ProgramCourseOutcome, on_delete=models.CASCADE)
    po_points = models.IntegerField(null=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'program_course_co_po_mapping'

class ProgramCourseCOPSOMapping(models.Model):
    co = models.ForeignKey(CourseOutcome, on_delete=models.CASCADE)
    pso = models.ForeignKey(ProgramSpecificOutcome, on_delete=models.CASCADE)
    pso_points = models.IntegerField(null=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = 'program_course_co_pso_mapping'


class MinorCoreProgramMapping(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    mapped_program = models.ForeignKey(Programs, on_delete=models.CASCADE,related_name='minor_prog')
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name='program_minor_category_created_by')
    class Meta:
        db_table = 'program_minor_core_program_mapping'        
        