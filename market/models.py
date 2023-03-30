from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from PIL import Image
from django.utils import timezone

User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsList:
    @staticmethod
    def queryset(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        ct_models = ContentType.objects.filter(model__in=args)
        global products
        total_products = []
        for ct_model in ct_models:
            products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            for product in products:
                total_products.append(product)
            print(products)
        return total_products


class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to),
                                  reverse=True
                                  )

        return products


class LatestProducts:
    objects = LatestProductsManager()


class LatestProductsAPI:
    objects = LatestProductsList()


class Product(models.Model):
    class Meta:
        abstract = True

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (1800, 1800)
    # MAX_IMAGE_SIZE = 3145728
    MAX_IMAGE_SIZE = 314

    title = models.CharField(max_length=255, verbose_name='Наименование товара')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    photo = models.ImageField(upload_to='photos/%y/%m/%d', verbose_name='Фото', blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Категория')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    def save(self, *args, **kwargs):
        img = self.photo
        img = Image.open(img)
        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise MinResolutionErrorException('Разрешение изображения меньше минимального')
        if img.height > max_height or img.width > max_width:
            raise MaxResolutionErrorException('Разрешение изображения больше максимального')
        super().save(*args, **kwargs)

    def get_model_name(self):
        return self.__class__.__name__.lower()


class NoteBook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    chargeless_time = models.CharField(max_length=255, verbose_name='Время автономной работы')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    class Meta:
        verbose_name = 'Ноутбук'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class SmartPhones(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Разрешение экрана')
    battery_volume = models.CharField(max_length=255, verbose_name='Объем батареи')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True, verbose_name='Карта памяти')
    sd_volume = models.CharField(max_length=255, verbose_name='Максимальный объем карты памяти', null=True, blank=True)
    main_cam_mp = models.CharField(max_length=255, verbose_name='Основная камера')
    front_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')

    class Meta:
        verbose_name = 'Смартфон'

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


class CategoryManager(models.Manager):
    CATEGORY_NAME_COUNT_NAME = {
        'Ноутбуки': 'notebook__count',
        'Смартфоны': 'smartphones__count',

    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categores_for_left_sidebar(self):
        print('self queryset   ', self.get_queryset())
        models = get_models_for_count('notebook', 'smartphones')

        # qs = list(self.get_queryset().annotate(*models).values())
        qs = list(self.get_queryset().annotate(*models))
        q = list(self.get_queryset().annotate(Count('notebook')))
        print('qqqqqqqqqqq', q)
        print(vars(q[0]))
        print(models)
        print(qs)
        print(vars(qs[1]))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        print(data)
        return data
        # return [dict(name=c['name'], slug=c['slug'], count=c[self.CATEGORY_NAME_COUNT_NAME[c['name']]]) for c in qs]


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Имя категории')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']


class CartProd(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='cart_for_pr')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveBigIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return 'Продукт: {} (для корзины)'.format(self.content_object.title)

    def get_absolute_url(self):
        return reverse('cart_product', kwargs={'id': self.pk})

    class Meta:
        verbose_name = 'Корзина продукта'
        # verbose_name_plural = 'Категории'
        ordering = ['id']

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Покупатель', on_delete=models.CASCADE)
    products = models.ManyToManyField('CartProd', blank=True, related_name='cart_product')
    total_products = models.PositiveBigIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)
    another = models.CharField(max_length=255)

    def __str__(self):
        if self.owner is not None:
            return 'Корзина покупателя {}'.format(self.owner.user)
        return 'Корзина покупателя {}'.format(self.owner)

    def get_absolute_url(self):
        return reverse('cart', kwargs={'id': self.pk, })

    class Meta:
        verbose_name = 'Корзина'
        # verbose_name_plural = 'Категории'
        ordering = ['id']


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='rel_customer')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)

    def get_absolute_url(self):
        return reverse('customer', kwargs={'id': self.pk})

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'
        ordering = ['id']


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен'),
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'самовывоз'),
        (BUYING_TYPE_DELIVERY, 'доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', on_delete=models.CASCADE,
                                 related_name='rel_orders')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес')
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying = models.CharField(max_length=100, verbose_name='Статус заказа', choices=BUYING_TYPE_CHOICES,
                              default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)
