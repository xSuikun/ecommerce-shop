from django import forms
from mainapp.models import Category
from .models import CategoryFeature, FeatureValidator


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class CreateCategoryFeatureForm(forms.ModelForm):
    class Meta:
        model = CategoryFeature
        fields = '__all__'


class CreateFeatureValidatorForm(forms.ModelForm):
    class Meta:
        model = FeatureValidator
        fields = ['category',]
