from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import requests

def home(request):
    if request.user.is_authenticated:
        url = "https://www.googleapis.com/books/v1/volumes?q=subject:fiction&maxResults=10"
        response = requests.get(url)
        data = response.json()

        books = []

        for item in data.get('items', []):
            volume = item['volumeInfo']

            authors = volume.get('authors', [])
            books.append({
                'title': volume.get('title', 'No Title'),
                'authors': authors if authors else ['Unknown'],
                'thumbnail': volume.get('imageLinks', {}).get('thumbnail'),
            })

        return render(request, 'accounts/home_logged_in.html', {'books': books})
    
    else:
        # GİRİŞ YAPMAMIŞ → landing page
        return render(request, 'accounts/landing.html')


def search(request):
    query = request.GET.get('q', '').strip()

    books = []

    if query:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=20"
        response = requests.get(url)
        data = response.json()
        for item in data.get('items', []):
            volume = item.get('volumeInfo', {})
            authors = volume.get('authors', [])
            books.append({
                'title': volume.get('title', 'No Title'),
                'authors': authors if authors else ['Unknown'],
                'thumbnail': volume.get('imageLinks', {}).get('thumbnail'),
            })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


