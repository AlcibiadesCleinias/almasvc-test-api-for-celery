from . import views
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='Test Well Features Generator API',
        default_version='v0',
        description='TODO',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='test@test.local'),
        license=openapi.License(name='-'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


app_name = 'well_feature_generator'

urlpatterns = [
    path('creation', views.CreateComputationApiView.as_view(), name='creation'),
    path('computations', views.ComputationsApiView.as_view(), name='computations'),
    path('results/<int:pk>', views.ComputationsWithResultsApiView.as_view(), name='results'),
    path('swagger-ui/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger_ui'),
]
