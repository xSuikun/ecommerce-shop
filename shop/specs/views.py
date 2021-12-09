from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from mainapp.models import Category
from .forms import CreateCategoryForm, CreateCategoryFeatureForm


class BaseSpecView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'specs/product_features.html', {})


class CreateCategoryView(View):
    def get(self, request, *args, **kwargs):
        form = CreateCategoryForm(request.POST or None)
        context = {'form': form}
        return render(request, 'specs/new_category.html', context)

    def post(self, request, *args, **kwargs):
        form = CreateCategoryForm(request.POST or None)
        if form.is_valid():
            new_category = form.save(commit=False)
            new_category.name = form.cleaned_data['name']
            new_category.slug = form.cleaned_data['slug']
            new_category.save()
            return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'specs/new_category.html', context)


class CreateCategoryFeatureView(View):
    def get(self, request, *args, **kwargs):
        form = CreateCategoryFeatureForm(request.POST or None)
        context = {'form': form}
        return render(request, 'specs/create_feature.html', context)

    def post(self, request, *args, **kwargs):
        form = CreateCategoryFeatureForm(request.POST or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'specs/create_feature.html', context)


class CreateFeatureValidatorView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {'categories': categories}
        return render(request, 'specs/create_validator.html', context)

