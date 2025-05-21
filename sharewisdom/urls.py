# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static



# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('base.urls')),
#     # path('room/', include('base.urls')),
#     path('api/', include('base.api.urls'))

# ]

# urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('rosetta/', include("rosetta.urls")),
    path('', include('base.urls')), 
    path('api/', include('base.api.urls')), 
    path('i18n/', include('django.conf.urls.i18n')), 
    path('notification/', include('follow.urls')),
    path('chat/', include('chat.urls')),
)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# urlpatterns = [
#     path('i18n/', include('django.conf.urls.i18n')),  # ✅ This enables built-in language switching
# ]

# urlpatterns += i18n_patterns(
#     path('admin/', admin.site.urls),
#     path('', include('base.urls')),
#     path('api/', include('base.api.urls')),
# )