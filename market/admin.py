from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm
from django.utils.safestring import mark_safe
from .models import *
from django import forms

from PIL import Image


class NotebookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo'].help_text = mark_safe(
            '<span style ="color:red;font-size: 14px;">Загружайте изображение с минимальным разрешением {}x{}</span>'.format(
                *Product.MIN_RESOLUTION))

    def clean_image(self):
        photo = self.cleaned_data['photo']
        img = Image.open(photo)
        min_height, min_width = Product.MIN_RESOLUTION
        max_height, max_width = Product.MAX_RESOLUTION
        if img.size > Product.MAX_IMAGE_SIZE:
            raise ValidationError('Размер изображения не должен превышать 3МВ')
        if img.height < min_height or img.width < min_width:
            raise ValidationError('Разрешение изображения меньше минимального')
        if img.height > max_height or img.width > max_width:
            raise ValidationError('Разрешение изображения больше максимального')
        return photo


class NotebookAdmin(admin.ModelAdmin):
    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='laptop'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and not instance.sd:
            self.fields['sd_volume'].widget.attrs.update({
                'readonly': True, 'style': 'background: lightgray;'
            })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume'] = None
        return self.cleaned_data


class SmartphoneAdmin(admin.ModelAdmin):
    change_form_template = 'admin.html'
    form = SmartphoneAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



# admin.site.register(SmartPhones)
# admin.site.register(NoteBook)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProd)
admin.site.register(SmartPhones, SmartphoneAdmin)
admin.site.register(NoteBook, NotebookAdmin)
admin.site.register(Category)
admin.site.register(Order)
