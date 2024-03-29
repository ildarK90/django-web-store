from django.db import transaction
from django.views.generic import ListView, DetailView
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
import market
from market.utils import recalc_cart
from .utils import catch_model
from .serializers import *
from market.models import LatestProducts
from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from drf_multiple_model.views import ObjectMultipleModelAPIView
from django.contrib.contenttypes.models import ContentType
from market.mixins import CartMixin


# class ProductList(generics.ListAPIView):
#     queryset = LatestProducts.objects.get_products_for_main_page('notebook', 'smartphones',
#                                                                      with_respect_to='smartphones')
#     serializer_class = ProductSerializer

class LatestProductsList(ObjectMultipleModelAPIView):
    " Вывод списка товаров с помощью сериалайзера, в данном случае используется сразу два сериалазйера с помощью библиотеи ObjectMultipleModelAPIView "
    querylist = [
        {'queryset': SmartPhones.objects.all().order_by('-id'), 'serializer_class': SmartPhoneDetailSerializer,
         'label': 'smartphones'},
        {'queryset': NoteBook.objects.all().order_by('-id'), 'serializer_class': NoteBookDetailSerializer,
         'label': 'laptop'},
    ]


class ProductList(APIView):
    """ Функция для вывода полей разных товаров без применения сериалайзера"""

    def get_product_values(self, instance, fields, **kwargs):
        products = {}
        for elem in fields:
            try:
                products[elem] = getattr(instance, elem)
                if elem == 'photo':
                    products[elem] = str(getattr(instance, elem))
            except:
                pass
        return products

    def get(self, request,**kwargs):
        products = LatestProducts.objects.get_products_for_main_page(self.kwargs.get('slug'))
        total_products = []
        fields = (
            'title', 'description', 'price', 'photo', 'diagonal', 'resolution', 'battery_volume', 'sd', 'sd_volume',
            'main_cam_mp', 'front_cam_mp', 'display', 'processor', 'ram', 'video',
            'chargeless_time')
        for product in products:
            prod = self.get_product_values(product, fields=fields)
            total_products.append(prod)

        return Response(total_products)


class GeneralViewSet(viewsets.ModelViewSet):
    """С помощью динамического сериалайзера"""

    @property
    def model(self):
        return apps.get_model(app_label='market', model_name=str(self.kwargs['model']))

    def get_queryset(self):
        model = self.model
        return model.objects.all()

    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer


class MyView(APIView):
    def get(self, request, format=None):
        # ...
        GenericSzl = getGenericSerializer(self.kwargs.get('model')).object.all()
        print(GenericSzl)
        serializer = GenericSzl(many=True)
        return Response(serializer.data)


class ProductDet(APIView):
    """детальная информация о товаре без сериалайзера"""

    def get(self, request, *args, **kwargs):
        # Product_classes = {'notebook': }
        queryset = catch_model(self.kwargs['model'])
        queryset = queryset._base_manager.all()
        prod = queryset.filter(pk=self.kwargs['pk']).first().__dict__
        global prods
        for product in queryset:
            if self.kwargs['model'] == 'notebook':
                fields = (
                    'title', 'description', 'price', 'photo', 'diagonal', 'display', 'processor', 'ram', 'video',
                    'chargeless_time')
                prods = model_to_dict(product, fields=fields)
            elif self.kwargs['model'] == 'smartphones':
                fields = ['title', 'description', 'price', 'ram', 'photo', 'diagonal', 'display', 'resolution',
                          'battery_volume', 'sd', 'sd_volume', 'main_cam_mp', 'front_cam_mp']
                prods = model_to_dict(product, fields=fields)
                prods['photo'] = str(prods['photo'])
        return Response({str(self.kwargs['model']): dict(prods)})


class ProductCategory(APIView):
    """Вывод товаров по категории без использования сериалайзера"""
    def get(self, request, *args, **kwargs):
        CATEGORIES = {"1": "notebook", "2": "smartphones"}
        print('категорияяяяя', CATEGORIES['1'])
        item = self.kwargs['model']
        queryset = catch_model(self.kwargs['model'])
        print(queryset)
        goods = queryset._base_manager.all().values()
        for good in goods:
            good.pop('time_create')
            good.pop('time_update')
            good.pop('slug')
            good.pop('id')
            old_category = good['category_id']
            good['category_id'] = CATEGORIES.get(str(old_category))
        return Response({item: list(goods)})


class CategoryView(APIView):

    def get(self,request):
        context = {
            "request": request
        }
        categories = Category.objects.all()
        serializer = CategorySerializer(categories,context=context, many=True)
        return Response(serializer.data)


class CategoryProductView(APIView):
    # serializer_class = CategorySerializer

    def get(self, request, **kwargs):
        serializer_context = {
            'ct_model': self.kwargs['ct_model'],
        }
        categories = Category.objects.all()
        # products = categories.category_product.filter(slug='laptop')
        serializer = CategorySerializer(categories, context=serializer_context, many=True)
        return Response(serializer.data)


class DeletefromCart(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get(self, request):
        global customer
        # user = None
        # request = self.context.get("request")
        # if request and hasattr(request, "user"):
        #     user = request.user

        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            print('customerrrrrrrrr', customer)
            if not customer:
                Customer.objects.create(
                    user=request.user
                )
        try:
            cart = Cart.objects.filter(owner=customer, in_order=False).values().first()
        except cart.DoesNotExist:
            raise Http404
        carts = Cart._base_manager.all().values()

        return JsonResponse(dict(cart))

    def delete(self, request, format=None, **kwargs, ):
        # cart = self.get_object(pk)
        customer = Customer.objects.filter(user=request.user).first()
        cart = Cart.objects.filter(owner=customer, in_order=False).values().first()
        # cart = request.data
        content_type = ContentType.objects.get(model=catch_model(kwargs['model']))
        product = content_type.model_class().objects.get(slug=kwargs['slug'])
        cart_product = CartProd.objects.get(user=cart.owner, cart=cart, content_type=content_type, object_id=product.id)
        cart_product.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'Товар успешно удален'})


class EditCart(CartMixin, APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get(self, request):
        context = {'request': request}
        try:
            cart = self.cart
            serializer = CartSerializer(cart, context=context)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        cart = self.cart
        serializer = CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        cart = self.get_object(pk)
        # content_type = ContentType.objects.get(model=ct_model)
        # product = content_type.model_class().objects.get(slug=product_slug)
        # cart_product = CartProd.objects.get(user=cart.owner, cart=cart, content_type=content_type, object_id=product.id)
        cart.delete()
        return Response({'status': 'Товар успешно удален'})


class CartProdList(CartMixin, APIView):
    """
    List all cartproducts
    """

    def get(self, request, format=None):
        serializer_context = {
            'request': request,
        }
        cart = self.cart
        cartprod = CartProd.objects.filter(cart=cart)
        # for i in cartprod:
        #     print(i.content_object)
        serializer = CartProductListSerializer(cartprod, context=serializer_context, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartProdDetail(CartMixin, APIView):
    """
    List all cartproducts
    """

    def get(self, request, pk, format=None):
        cart = self.cart
        serializer_context = {
            'request': request,
        }
        cartprod = CartProd.objects.filter(cart=cart, pk=pk)
        serializer = CDSerializer(cartprod, context=serializer_context, many=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        cart = self.cart
        cart_prod = CartProd.objects.get(pk=pk)
        cart_prod.delete()
        recalc_cart(cart)
        return Response({'status': 'Корзина товара успешно удалена'})


class AddtoCart(CartMixin, APIView):
    """
    Add to Cart
    """

    # def get_queryset(self, request, **kwargs):
    #     serializer_context = {
    #         'request': request,
    #     }
    #     cart = self.cart
    #     ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
    #     content_type = ContentType.objects.get(model=ct_model)
    #     product = content_type.model_class().objects.get(slug=product_slug)
    #     cart_product = CartProd.objects.get_or_create(user=cart.owner, cart=cart, content_type=content_type,
    #                                                   object_id=product.id)

    def patch(self, request, format=None, **kwargs, ):
        serializer_context = {
                    'request': request,
                }
        cart = self.cart
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('product_slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProd.objects.get_or_create(user=cart.owner, cart=cart, content_type=content_type,
                                                               object_id=product.id)
        print('cart_product', cart_product)
        if created:
            cart.products.add(cart_product)
            # cart.save()
        recalc_cart(cart)
        serializer = CartSerializer(cart, data=request.data, context=serializer_context, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeQTY(CartMixin, APIView):

    def patch(self, reqest, pk):
        cart = self.cart
        cartproduct = CartProd.objects.filter(pk=pk).first()
        print(cartproduct)
        serializer = CDSerializer(cartproduct, data=reqest.data, partial=True)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            recalc_cart(cart)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderView(CartMixin, APIView):

    def get(self, request):
        context = {
            "request": request
        }
        cart = self.cart
        serializer = CartSerializer(cart, context=context)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        customer = Customer.objects.filter(user=request.user).first()
        cart = self.cart
        order = Order.objects.create(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            customer=customer,
            phone=request.data['phone'],
            address=request.data['address'],
            buying=request.data['buying'],
        )
        cart.in_order = True
        cart.save()
        order.cart = cart
        order.full_clean()
        order.save()
        customer.orders.add(order)
        # serializer = OrderSerializer(data=request.data)
        # if serializer.is_valid():
        #     model_obj = serializer.save()
        #     cart.in_order = True
        #     cart.save()
        #     model_obj.cart = cart
        #     customer.order.add(model_obj)
        #     serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
