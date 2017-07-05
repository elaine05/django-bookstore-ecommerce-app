from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.contrib.gis.geoip2 import GeoIP2

# Create your views here.

from .models import Book, BookOrder, Cart, Review
from .forms import UserForm, ReviewForm


@login_required(login_url='/store/login')
def index(request):
    if request.user.is_authenticated():
        books = Book.objects.all()
        context = {
            'books': books
        }
        return render(request, 'index.html', context)
    return render(request, 'login.html')


def book_details(request, book_id=None):
    book = Book.objects.get(id=book_id)
    context = {
        'book': book
    }
    if request.user.is_authenticated():
        if request.method == "POST":
            new_review = Review(book=context['book'],user=request.user,text=request.POST['text'])
            new_review.save()
            # form = ReviewForm(request.POST or None)
            # if form.is_valid():
            #     new_review = Review(
            #         book=context['book'],
            #         user=request.user,
            #         text=form.cleaned_data.get('text')
            #         )
            #     new_review.save()
        else:
            if Review.objects.filter(user=request.user, book=context['book']).count() == 0:
                # form = ReviewForm()
                context['form'] = 1
    context['reviews'] = book.review_set.all()
    ip = GeoIP2().city('103.196.233.10')
    if not ip:
        ip = GeoIP2().city('72.14.207.99')
    context['ip'] = ip
    return render(request, 'details.html', context)



def add_to_cart(request, book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                cart = Cart.objects.get(user=request.user, active=True)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(
                    user=request.user
                )
                cart.save()
            cart.add_to_cart(book_id)
        return redirect('cart')
    else:
        return redirect('index')


def remove_from_cart(request, book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            cart = Cart.objects.get(user=request.user, active=True)
            cart.remove_form_cart(book_id)
        return redirect('cart')
    else:
        return redirect('index')


def cart(request):
    if request.user.is_authenticated():
        cart = Cart.objects.filter(user=request.user.id, active=True)
        orders = BookOrder.objects.filter(cart=cart)
        total = 0
        count = 0
        for order in orders:
            total += (order.book.price * order.quantity)
            count += order.quantity
        context = {
            'cart': orders,
            'total': total,
            'count': count,
        }
        return render(request, 'cart.html', context)
    else:
        return redirect('index')


@login_required(login_url='/store/login')
def store(request):
    return render(request, 'store.html', {})


def login_user(request):
    if request.user.is_authenticated():
        return redirect('/store/')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'index.html', {})
            else:
                return render(request, 'login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login'})
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('/store/login')


def register(request):
    if request.user.is_authenticated():
        return redirect('/store/')
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
    return render(request, 'registration.html', {})
