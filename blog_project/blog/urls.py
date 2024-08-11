from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/update/', views.profile_update, name='profile_update'),
    path('accounts/profile/<str:username>/', views.user_profile, name='user_profile'),
    path('community/', views.community, name='community'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
