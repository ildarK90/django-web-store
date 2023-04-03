from django.views.generic import ListView, DetailView
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
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
    querylist = [
        {'queryset': SmartPhones.objects.all().order_by('-id'), 'serializer_class': SmartPhoneDetailSerializer,
         'label': 'smartphones'},
        {'queryset': NoteBook.objects.all().order_by('-id'), 'serializer_class': NoteBookDetailSerializer,
         'label': 'laptop'},
    ]


class ProductList(APIView):

    def get_product_values(self, instance, fields, **kwargs):
        products = {}
        for elem in fields:
            print(elem)
            try:
                products[elem] = getattr(instance, elem)
                if elem == 'photo':
                    products[elem] = str(getattr(instance, elem))
                print(products)
            except:
                pass
        return products

    def get(self, request):
        products = LatestProducts.objects.get_products_for_main_page('smartphones', 'notebook')
        print(products)
        total_products = []
        fields = (
            'title', 'description', 'price', 'photo', 'diagonal', 'resolution', 'battery_volume', 'sd', 'sd_volume',
            'main_cam_mp', 'front_cam_mp', 'display', 'processor', 'ram', 'video',
            'chargeless_time')
        for product in products:
            prod = self.get_product_values(product, fields=fields)
            total_products.append(prod)

        return Response(total_products)


class ProductDet(APIView):

    def get(self, request, *args, **kwargs):
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
        return Response({'notebook': dict(prods)})


class ProductCategory(APIView):

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

    def get_queryset(self, ):
        categories = Category.objects.all()
        return categories


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
        print(kwargs['model'])
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
        try:
            cart = self.cart
            serializer = CartSerializer(cart)
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
        customer = Customer.objects.filter(user=request.user).first()
        # cart = Cart.objects.filter(owner=customer, in_order=False).first()
        cartprod = CartProd.objects.filter(cart=cart, pk=pk)
        serializer = CDSerializer(cartprod, context=serializer_context, many=True)
        return Response(serializer.data)

    def patch(self, request, ct_model, product_slug, format=None):
        customer = Customer.objects.filter(user=request.user).first()
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cartprod = CartProd.objects.filter(cart=cart)
        cartprod.content_object.add(content_type, product)
        # cartprod.save()
        serializer = CDSerializer(cartprod, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cart_prod = CartProd.objects.get(pk=pk)
        cart_prod.delete()
        return Response({'status': 'Корзина товара успешно удалена'})


class AddtoCart(CartMixin, APIView):
    """
    Add to Cart
    """

    def get_queryset(self, request, **kwargs):
        serializer_context = {
            'request': request,
        }
        cart = self.cart
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProd.objects.get_or_create(user=cart.owner, cart=cart, content_type=content_type,
                                                      object_id=product.id)

    def patch(self, request, format=None, **kwargs, ):
        cart = self.cart
        print(cart.owner.user)
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('product_slug')
        content_type = ContentType.objects.get(model=ct_model)
        print(content_type)
        product = content_type.model_class().objects.get(slug=product_slug)
        print(product)
        cart_product, created = CartProd.objects.get_or_create(user=cart.owner, cart=cart, content_type=content_type,
                                                               object_id=product.id)
        print('cart_product', cart_product)
        if created:
            print(created)
            cart.products.add(cart_product)
        recalc_cart(cart)
        serializer = CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
