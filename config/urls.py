"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from app.views import SuccessView, ContactView

urlpatterns = [
    path("", views.view_main_page, name="home"),
    path("login/", views.view_login, name="login"),
    path("register/", views.register, name="register"),
    path("profile/<str:username>/", views.viewUserProfile, name="profile"),
    path("logout/", views.viewLogout, name="logout"),
    path("products/", views.viewProducts, name="products"),
    path("schedule/<str:username>/", views.view_schedule_page, name="schedule"),  
    path('events/update/<int:event_id>/', views.update_event, name='update_event'),
    
    path('create_class/', views.create_class, name='create_class'),
    path('edit_class/<int:class_id>/', views.edit_class, name='edit_class'),
    
    path("contact/", ContactView.as_view(), name="contact"),
    path("success/", SuccessView.as_view(), name="success"),
    path("admin/", admin.site.urls),
]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)