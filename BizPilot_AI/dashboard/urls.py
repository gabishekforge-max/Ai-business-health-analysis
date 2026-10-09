from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_view, name='upload'),
    path('sample-data/', views.load_sample_data, name='sample_data'),
    path('download-sample/', views.download_sample_csv, name='download_sample'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('history/', views.history_view, name='history'),
]