import os
import json
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Movie, Cast

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".ENV")
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")
API_BASE_URL = os.getenv("API_URL", "https://jsonfakery.com/movies/paginated?page=")


def _save_movies_List(data):
    """Helper to save a list of movie dicts into the database."""
    for item in data:
        movie_id = item.get('movie_id') or item.get('id')
        if not movie_id:
            continue

        movie, created = Movie.objects.get_or_create(
            id=str(movie_id),
            defaults={
                'original_title': item.get('original_title', ''),
                'release_date': item.get('release_date'),
                'overview': item.get('overview', ''),
                'poster_path': item.get('poster_path'),
                'backdrop_path': item.get('backdrop_path'),
                'original_language': item.get('original_language', 'en'),
                'vote_average': float(item.get('vote_average') or 0.0),
                'vote_count': int(item.get('vote_count') or 0),
                'popularity': float(item.get('popularity') or 0.0),
            }
        )

        casts = item.get('casts', [])
        for cast in casts:
            cast_id = cast.get('id')
            if not cast_id:
                continue

            cast_obj, cast_created = Cast.objects.get_or_create(
                id=str(cast_id),
                defaults={
                    'name': cast.get('name', ''),
                    'character': cast.get('character', ''),
                    'profile_path': cast.get('profile_path'),
                    'popularity': float(cast.get('popularity') or 0.0),
                }
            )
            movie.casts.add(cast_obj)


def dataBase(request):
    # 1. Handle JSON data sent from the frontend browser
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            data = payload.get('data', [])
            fetched_page = payload.get('page')

            _save_movies_List(data)

            if fetched_page:
                request.session['last_fetched_api_page'] = int(fetched_page)

            messages.success(request, f"Loaded page {fetched_page} movies successfully!")
            return JsonResponse({"status": "ok"})
        except Exception as e:
            logger.exception("Failed saving movies from frontend")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    # 2. Fallback if someone visits the URL directly via GET
    return redirect('home')


def home(request):
    movies = Movie.objects.prefetch_related('casts').order_by('id')
    search = request.GET.get('q')
    if search:
        movies = movies.filter(original_title__icontains=search)
    paginator = Paginator(movies, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    next_api_page = request.session.get('last_fetched_api_page', 0) + 1

    return render(request, 'movies/home.html', {
        'movies': page_obj,
        'next_api_page': next_api_page,
        'api_base_url': API_BASE_URL,
    })


def registerUser(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'user/register.html', {'form': form})


def loginUser(request):
    if request.method == "POST":
        data = request.POST
        form = AuthenticationForm(request, data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form})


def logoutUser(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")


@login_required(login_url="login")
def profile(request):
    liked_movies = request.user.Watchlist.all()
    return render(request, 'movies/home.html', {'movies': liked_movies})


@login_required(login_url="login")
def watchlist(request, movie_id):
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        if request.user in movie.user.all():
            movie.user.remove(request.user)
        else:
            movie.user.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def CastView(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    release_year = movie.release_date[-4:] if movie.release_date else ''
    return render(request, 'movies/details.html', {
        'movie': movie,
        'releaseYear': release_year,
        'cast_list': movie.casts.all(),
    })
