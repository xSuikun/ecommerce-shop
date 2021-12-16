from django.urls import path
from .views import *

urlpatterns = [
    path('', BaseSpecView.as_view(), name='specifications'),
    path('create_category/', CreateCategoryView.as_view(), name='create_category'),
    path('create_feature/', CreateCategoryFeatureView.as_view(), name='create_feature'),
    path('create_validator/', CreateFeatureValidatorView.as_view(), name='create_validator'),
    path('create_validator/', CreateFeatureValidatorView.as_view(), name='create_validator'),
]
