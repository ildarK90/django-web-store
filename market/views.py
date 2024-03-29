from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.urls import reverse_lazy

from .models import *
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View, CreateView
from django.db import models
from .mixins import *
from .forms import OrderForm
from .utils import recalc_cart


class BaseView(CategoryDetailMixin, CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categores_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page('notebook', 'smartphones',
                                                                     with_respect_to='smartphones')
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart,

        }
        return render(request, 'base.html', context)


# def test_vew(request):
#     print(Category.objects.get_categores_for_left_sidebar())


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {

        'notebook': NoteBook,
        'smartphones': SmartPhones
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        print(self.model,'Это модееееееель')
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    # model = Model
    # queryset = NoteBook.objects.all()
    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart

        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['cart'] = self.cart
        return context


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        cart = self.cart
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProd.objects.get(user=cart.owner, cart=cart, content_type=content_type, object_id=product.id)
        # cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(cart)
        messages.add_message(request, messages.INFO, 'Товар успешно удален')
        return HttpResponseRedirect('/cart/')


def delete_pr(request, ct_model, product_slug):
    user = request.user
    customer = Customer.objects.filter(user=request.user).first()
    cart = Cart.objects.filter(owner=customer).first()
    content_type = ContentType.objects.get(model=ct_model)
    product = content_type.model_class().objects.get(slug=product_slug)
    print(product)
    cart_product = CartProd.objects.get(user=cart.owner, cart=cart, content_type=content_type, object_id=product.id)
    print(cart_product)
    cart.products.remove(cart_product)
    # cart_product.delete()
    # cart.save()
    print(cart)
    print(cart_product)
    return render(request, 'base.html')


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        # customer = Customer.objects.get(user=request.user)
        # cart = Cart.objects.get(owner=customer)
        cart = self.cart
        print(cart.owner.user)
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProd.objects.get_or_create(user=cart.owner, cart=cart, content_type=content_type,
                                                               object_id=product.id)
        # cart_product = CartProd.objects.create(user=cart.owner, cart=cart, content_type=content_type,
        #                                                        object_id=product.id)
        if created:
            print('Создан новый товарррррррррррррррррррррррр', created)
            print('Добавляеееееееееееем картпродакт', cart_product)
            cart.products.add(cart_product)
        else:
            print('Товар уже ееееееееееееееееесть ', cart_product)
        recalc_cart(cart)
        messages.add_message(request, messages.INFO, 'Товар успешно добавлен')

        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        cart = self.cart
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProd.objects.get(user=cart.owner, cart=cart, content_type=content_type,
                                            object_id=product.id)
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(cart)
        messages.add_message(request, messages.INFO, 'Количество изменено')
        print(request.POST)
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categores_for_left_sidebar()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)


class OrderView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        cart = self.cart
        customer = self.cart.owner
        categories = Category.objects.get_categores_for_left_sidebar()
        orders = Order.objects.filter(customer=customer)
        print(orders,'ordeeeeeers for order')
        context = {
            'cart': self.cart,
            'categories': categories,
            'orders': orders
        }
        return render(request, 'orders.html', context)


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categores_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying = form.cleaned_data['buying']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout')

class RegisterUser(CreateView):
    form_class = UserCreationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')

    def get_context_data(self,*,object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


