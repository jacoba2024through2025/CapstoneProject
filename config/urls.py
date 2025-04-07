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
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.view_main_page, name="home"),

    # Authentication
    path("login/", views.view_login, name="login"),
    path("register/", views.register, name="register"),
    path("profile/<str:username>/", views.viewUserProfile, name="profile"),
    path("logout/", views.viewLogout, name="logout"),

    # Products and Cart
    path("products/", views.viewProducts, name="products"),
    path("products/<int:product_id>/", views.viewOneProduct, name="product_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path('config/', views.stripe_config, name='stripe_config'),
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),


    # Schedule and Contact
    path("schedule/", views.view_schedule_page, name="schedule"),
    path("schedule/<str:username>/", views.view_schedule_page, name="schedule"),  
    path('update_event/<int:event_id>/', views.update_event, name='update_event'),
    path('get_class_calendar/<int:class_id>/', views.get_class_calendar, name='get_class_calendar'),
    path('create_class/', views.create_class, name='create_class'),
    path('edit_class/<int:class_id>/', views.edit_class, name='edit_class'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="password_reset_form.html"), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path("contact/", ContactView.as_view(), name="contact"),
    path("success/", views.empty_cart, name="success"),
    path("cancelled/", views.cancel_payment, name="cancel"),
    path("adminpanel/", views.view_admin_page, name="adminpanel"),
    path("adminpanel/chart/", views.view_admin_chart, name="chart"),
    path("adminpanel/forms/", views.view_admin_forms, name="forms"),
    path("adminpanel/tabs/", views.view_admin_tabs, name="tabs"),
    path("adminpanel/ui/", views.view_admin_ui, name="ui"),
    path("adminpanel/tables/", views.view_admin_tables, name="tables"),
    path("admin/", admin.site.urls),
]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)