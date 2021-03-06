from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth

from apps.cart.forms import CartAddProductForm
from apps.category.models import Category
from apps.ecommerce.forms import CommentForm
from .models import Product, Comment
from django.views.generic import ListView, CreateView, DetailView
from django.core.paginator import Paginator


def product_list(request):
    search_query = request.GET.get('search', '')
    categories = Category.objects.filter(parent=None).order_by('title')

    if search_query:
        product = Product.objects.filter(Q(p_name__icontains=search_query))
    else:
        product = Product.objects.all()
    paginator = Paginator(product, 3)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()

    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    context = {
        'page_object': page,
        'is_paginated': is_paginated,
        'next_url': next_url,
        'prev_url': prev_url,
        'categories': categories,
    }

    return render(request, 'products_list.html', context=context)



def index(request):
    return render(request, 'index.html', {})


"""class ProductListView(ListView):
    model = Product
    template_name = 'products_list.html'
    fields = ['p_name', 'price', 'category']
"""

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'


def add_comment_to_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.author = auth.get_user(request)
            comment.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'products_list.html', {'category':
                                                      category,
                                                  'categories':
                                                      categories,
                                                  'products':
                                                      products})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    return render(request, 'product_detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})




