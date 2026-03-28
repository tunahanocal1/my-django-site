from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import requests

def home(request):
    if request.user.is_authenticated:
        # Open Library'den fiction kategorisinde kitaplar (search by subject)
        url = "https://openlibrary.org/subjects/fiction.json?limit=10"
        try:
            response = requests.get(url)
            data = response.json()
            books = []

            for item in data.get('works', []):
                books.append({
                    'title': item.get('title', 'No Title'),
                    'authors': [author.get('name', 'Unknown') for author in item.get('authors', [])],
                    'thumbnail': f"https://covers.openlibrary.org/b/id/{item['cover_id']}-M.jpg" if item.get('cover_id') else None
                })

        except Exception as e:
            print(f"Open Library API error: {e}")
            books = []

        return render(request, 'accounts/home_logged_in.html', {'books': books})
    
    else:
        return render(request, 'accounts/landing.html')


def search(request):
    query = request.GET.get('q', '').strip()
    books = []

    if query:
        url = f"https://openlibrary.org/search.json?q={query}&limit=20"
        try:
            response = requests.get(url)
            data = response.json()
            for item in data.get('docs', []):
                books.append({
                    'title': item.get('title', 'No Title'),
                    'authors': item.get('author_name', ['Unknown']),
                    'thumbnail': f"https://covers.openlibrary.org/b/id/{item['cover_i']}-M.jpg" if item.get('cover_i') else None,
                    'olid': item.get('key').split('/')[-1]  # '/works/OL12345W' → 'OL12345W'
                })
        except Exception as e:
            print(f"Open Library search error: {e}")
            books = []

    return render(request, 'accounts/search.html', {
        'books': books,
        'query': query
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


def book_detail(request, olid):
    """
    Open Library API üzerinden tek bir kitabın detayını getirir.
    """
    url = f"https://openlibrary.org/works/{olid}.json"
    book = {}
    try:
        response = requests.get(url)
        data = response.json()
        book['title'] = data.get('title', 'No Title')
        book['description'] = ''
        # description bazen dict bazen string olarak gelir
        if isinstance(data.get('description'), dict):
            book['description'] = data['description'].get('value', '')
        elif isinstance(data.get('description'), str):
            book['description'] = data['description']
        book['authors'] = []
        for author in data.get('authors', []):
            # author key ile detay alıyoruz
            author_url = f"https://openlibrary.org{author['author']['key']}.json"
            a_res = requests.get(author_url).json()
            book['authors'].append(a_res.get('name', 'Unknown'))
        book['covers'] = []
        for cover_id in data.get('covers', []):
            book['covers'].append(f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg")
    except Exception as e:
        print(f"Open Library book detail error: {e}")

    return render(request, 'accounts/book_detail.html', {'book': book})
