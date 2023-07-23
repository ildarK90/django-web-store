from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from .models import *


class CategoryDetailMixin(SingleObjectMixin):
    CATEGORY_SLUG2PRODUCT_MODEL = {
        'laptop': NoteBook,
        'smartphones': SmartPhones
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(self.get_object(), Category):
            # m = self.get_object()
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context['categories'] = Category.objects.get_categores_for_left_sidebar()
            context['category_products'] = model.objects.all()
            return context
        else:
            context['categories'] = Category.objects.get_categores_for_left_sidebar()
            # context['category_products'] = model.objects.all()
            m = self.get_object()
            return context


class CategoryMixin(SingleObjectMixin):
    CATEGORY_SLUG2PRODUCT_MODEL = {
        'laptop': NoteBook,
        'smartphones': SmartPhones
    }

    def get_context(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('mixin contexxxxt',context.items())
        if isinstance(self.get_object(), Category):
            m = self.get_object()
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context['categories'] = Category.objects.get_categores_for_left_sidebar()
            context['category_products'] = model.objects.all()
            return context
        else:
            context['categories'] = Category.objects.get_categores_for_left_sidebar()
            # context['category_products'] = model.objects.all()
            m = self.get_object()
            return context


class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            # print(cart,'Caaaaaaaaaaaart')
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            # if not cart:
            #     cart = Cart.objects.create(for_anonymous_user=True)
            #     self.cart = cart
        self.cart = cart
        # print(self.cart.total_products, self.cart.final_price)
        return super().dispatch(request, *args, **kwargs)
