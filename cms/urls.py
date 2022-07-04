"""CMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',include('user_management.urls') ),
    path('user/',include('user_management.urls') ),
    path('course/',include('course_management.urls') ),
    path('pcmi/',include('pcm.urlsi') ),
    path('pcmc/',include('pcm.urlsc') ),
    path('bos/',include('bos.urls') ),
    path('bosc/',include('bos.urlsc') ),
    path('csmc/',include('csm.urlsc') ),
    path('csmi/',include('csm.urlsi') ),
    path('staff/',include('faculty.urls')),
    path('pab/',include('pab.urls') ),
    path('doaa/',include('doaa.urls')),


    # path('programs/',include('programs.urls') ),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIAFILES_DIRS)
