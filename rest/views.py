from django.views.generic import ListView, DetailView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet

from market.utils import recalc_cart
from .utils import catch_model
from .serializers import *
from market.models import LatestProducts
from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType
from market.mixins import CartMixin


# class ProductList(generics.ListAPIView):
#     queryset = LatestProducts.objects.get_products_for_main_page('notebook', 'smartphones',
#                                                                      with_respect_to='smartphones')
#     serializer_class = ProductSerializer





class ProductList(APIView):

    def get(self, request):
        products = LatestProducts.objects.get_products_for_main_page('smartphones','notebook')
        total_products = []
        for product in products:
            prod = {}
            prod['title'] = product.title
            prod['img'] = product.photo.url
            prod['url'] = product.get_absolute_url()
            total_products.append(prod)

        print(total_products)
        # total_prods = ProductSerializer().data
        return Response(total_products)


class NoteBookDetailed(RetrieveAPIView):
    """
    Выводим проект детально
    """
    serializer_class = NoteBookDetailSerializer

    def get_queryset(self, **kwargs):
        return NoteBook.objects.filter(pk=self.kwargs['pk'])


class ProductDet(APIView):
    # CT_MODEL_MODEL_CLASS = {
    #
    #     'notebook': NoteBook,
    #     'smartphones': SmartPhones
    # }
    #
    # def dispatch(self, request, *args, **kwargs):
    #
    #     self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
    #     print(self.model,'Это модееееееель')
    #     self.queryset = self.model._base_manager.all()
    #     return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # CT_MODEL_MODEL_CLASS = {
        #
        #     'notebook': NoteBook,
        #     'smartphones': SmartPhones
        # }
        # model = self.kwargs['model']
        # print(model)
        # model_prod = CT_MODEL_MODEL_CLASS[self.kwargs['model']]
        # queryset = model_prod._base_manager.all()
        queryset = catch_model(self.kwargs['model'])
        queryset = queryset._base_manager.all()
        prod = queryset.filter(pk=self.kwargs['pk']).values()
        # total_prods = ProductSerializer().data
        return JsonResponse({'notebook': list(prod)})
        # return Response(prod)


class ProductCategory(APIView):

    def get(self, request, *args, **kwargs):
        item = self.kwargs['model']
        queryset = catch_model(self.kwargs['model'])
        goods = queryset._base_manager.all().values()
        return JsonResponse({item: list(goods)})


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

        # cart = Cart.objects.filter(owner=customer).first()
        # cart_dict = cart.__dict__
        # print(type(cart_dict))
        # print('Это __dict__',list(cart.__dict__))
        # car = model_to_dict(cart)
        # print('Это model to dict',car)
        # print('Это model to dict values',car.values())

        try:
            cart = Cart.objects.filter(owner=customer, in_order=False).values().first()
        except cart.DoesNotExist:
            raise Http404
        carts = Cart._base_manager.all().values()

        return JsonResponse(dict(cart))

    # def put(self, request, pk, format=None):
    #     snippet = self.get_object(pk)
    #     serializer = SnippetSerializer(snippet, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class EditCategory(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response({'status': 'Товар успешно удален'})


class EditCart(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, request):
        try:
            customer = Customer.objects.filter(user=request.user).first()
            cart = Cart.objects.filter(owner=customer, in_order=False).values().first()
            return cart
        except Cart.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        cart = self.get_object(pk)
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


class CartList(APIView):
    """
    List all carts, or create a new snippet.
    """

    def get(self, request, format=None):
        customer = Customer.objects.filter(user=request.user).first()
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartProdList(APIView):
    """
    List all cartproducts
    """

    def get(self, request, format=None):
        serializer_context = {
            'request': request,
        }
        customer = Customer.objects.filter(user=request.user).first()
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        cartprod = CartProd.objects.filter(cart=cart)
        for i in cartprod:
            print(i.content_object)
        serializer = CartProductListSerializer(cartprod, context=serializer_context, many=True)
        return Response(serializer.data)

    # def get(self,request):
    #     cartprod = CartProd.objects.all()
    #     print(cartprod)
    #     serializer = CDSerializer(cartprod,many=True)
    #     print(serializer)
    #     return Response(serializer.data)

    # def post(self, request, format=None):
    #     serializer = CartSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartProdDetail(APIView):
    """
    List all cartproducts
    """

    def get_object(self, request, pk, format=None):
        serializer_context = {
            'request': request,
        }
        customer = Customer.objects.filter(user=request.user).first()
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        # cart1 = model_to_dict(cart)
        # print(cart1.values())
        cartprod = CartProd.objects.filter(cart=cart, pk=pk)
        cartproducts = CartProd.objects.values().all
        cartprod_test = CartProd.objects.values().first()
        print(cartproducts)
        print('Товаааааары',cartprod_test)
        serializer = CDSerializer(cartprod, context=serializer_context, many=True)
        return Response(serializer.data)

    # def post(self, request, format=None):
    #     serializer = CDSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def put(self, request, pk, format=None):
    #     category = self.get_object(pk)
    #     serializer = CDSerializer(category, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    def delete(self, request,pk):
        cart_prod = CartProd.objects.get(pk=pk)
        cart_prod.delete()
        return Response({'status': 'Корзина товара успешно удалена'})

    # def get(self,request):
    #     cartprod = CartProd.objects.all()
    #     print(cartprod)
    #     serializer = CDSerializer(cartprod,many=True)
    #     print(serializer)
    #     return Response(serializer.data)

    # def post(self, request, format=None):
    #     serializer = CartSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddtoCart(CartMixin,APIView):
    """
    Add to Cart
    """

    def get_queryset(self,request,**kwargs):
        serializer_context = {
            'request': request,
        }
        cart = self.cart
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProd.objects.get_or_create(user=cart.owner, cart=cart, content_type=content_type,
                                                               object_id=product.id)

    def post(self, request, pk,format=None,**kwargs, ):
        if get_queryset().exists():
            ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
            content_type = ContentType.objects.get(model=ct_model)
            product = content_type.model_class().objects.get(slug=product_slug)
            cart_product = CartProd.objects.get_or_create(user=cart.owner, cart=cart, content_type=content_type,
                                                          object_id=product.id)
            cart=self.cart
            cart.products.add(cart_product)
            recalc_cart(cart)
            serializer = CDSerializer(data=request.data)
            serializer.save()
            return Response(serializer.data)