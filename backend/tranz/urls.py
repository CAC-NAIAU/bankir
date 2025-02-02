from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FigurantViewSet,
    TransactionViewSet,
    FigurantList,
    FigurantCreate, FigurantUpdate,
    convertator, network_analysis, global_search,
    create_chart, generate_reports,
    procurement_pivot, procurement_download, procurement_update
)
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings

app_name = 'tranz'

router = DefaultRouter()
router.register(r'figurant', FigurantViewSet)
router.register(r'transaction', TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('tranz/', login_required(FigurantList.as_view(), login_url='/'), name='figurant_list'),
    path('create/', login_required(FigurantCreate.as_view(), login_url='/'), name='create_figurant'),
    path('update/<str:pk>/', login_required(FigurantUpdate.as_view(), login_url='/'), name='update_figurant'),
    path('generate_reports/<str:pk>/', generate_reports, name='generate_reports'),
    path('create_chart/<str:pk>/', create_chart, name='create_chart'),
    path('procurement_download/<str:pk>/', procurement_download, name='procurement_download'),
    path('procurement_pivot/<str:pk>/', procurement_pivot, name='procurement_pivot'),
    path('procurement_update/<str:pk>/', procurement_update, name='procurement_update'),
    path('convertator/', convertator, name='convertator'),
    path('global_search/', global_search, name='global_search'),
    path('network_analysis/', network_analysis, name='network_analysis'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += router.urls
