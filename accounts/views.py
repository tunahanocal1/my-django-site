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


from .models import BookReview
from .forms import ReviewForm

def book_detail(request, olid):
    url = f"https://openlibrary.org/works/{olid}.json"
    book = {}
    thumbnail_url = None # Varsayılan olarak boş

    try:
        response = requests.get(url)
        data = response.json()

        book['title'] = data.get('title', 'No Title')

        # GÖRSEL MANTIĞI: OpenLibrary'den kapak ID'sini alıp URL oluşturuyoruz
        covers = data.get('covers')
        if covers and len(covers) > 0:
            # Covers listesindeki ilk ID'yi kullanıyoruz
            thumbnail_url = f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg"

        # description
        desc = data.get('description')
        if isinstance(desc, dict):
            book['description'] = desc.get('value', '')
        else:
            book['description'] = desc

    except Exception as e:
        print(f"Detail error: {e}")
        book['title'] = "Error loading book"
        book['description'] = ""

    # REVIEWS
    reviews = BookReview.objects.filter(olid=olid).order_by('-created_at')

    # Ortalama rating
    avg_rating = None
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()

    # Form gönderme
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            review = form.save(commit=False)
            review.user = request.user
            review.olid = olid
            review.rating = request.POST.get('rating')
            review.save()
            return redirect('book_detail', olid=olid)
    else:
        form = ReviewForm()

    return render(request, 'accounts/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'form': form,
        'avg_rating': avg_rating,
        'thumbnail': thumbnail_url # Şablona bu isimle gönderiyoruz
    })


@login_required
def profile_view(request):
    # Bu kısımlar senin modellerine (BookReview veya ayrı bir UserBook tablosu) göre değişir
    read_books = # Kullanıcının "Okudum" işaretledikleri
    liked_books = # Kullanıcının "Beğendim" işaretledikleri
    watchlist_books = # Kullanıcının "Listem" dedikleri
    
    return render(request, 'accounts/profile.html', {
        'read_books': read_books,
        'liked_books': liked_books,
        'watchlist_books': watchlist_books,
    })
