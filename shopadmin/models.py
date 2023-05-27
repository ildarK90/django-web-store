from django.db import models


class TestModel(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Имя')
    product_category = models.ForeignKey('Category',on_delete=models.CASCADE,verbose_name='Имя категории')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL',blank=True,null=True)
    photo = models.ImageField(blank=True,verbose_name='фото товара')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100,db_index=True,verbose_name='имя категории')
    photo = models.ImageField(blank=True,verbose_name='фото категории')

    def __str__(self):
        return self.name