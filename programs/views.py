from django.shortcuts import render,redirect
from .models import *
from datetime import datetime, timedelta
from django.contrib import messages

def create_program(request):
    campus = Campus.objects.filter(status=1).values('name','address','id')
    context ={'campus':campus}
    if request.method == "POST":
        try:
            insert = Programs.objects.create(name=request.POST.get(''),created=datetime.now(),program_type=request.POST.get(''),user_id=request.user.id)
            if insert:
                for c in request.POST.getlist(''):
                    ProgramCampusMapping.objects.create(campus=c,program_id=insert.id)
            return redirect('/')
        except Exception as e:
            messages.error(request, str(e))
            ErrorLogs.objects.create(log=str(e), info=request.POST)
            return render(request,'programs/create_program.html')
    return render(request,'programs/create_program.html',context)