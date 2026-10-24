import os
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.paginator import Paginator #to seperate data into different different pages

from .models import Movie,Cast

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".ENV")
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")
API_BASE_URL = os.getenv("API_URL")

def dataBase(request):
  if not API_BASE_URL:
    messages.error(request, "Movie API URL is not configured.")
    return redirect('home')

  current_page = request.session.get('last_fetched_api_page',0)
  next_page = current_page + 1
  API_URL = f"{API_BASE_URL}{next_page}"
  try:
    response = requests.get(
        API_URL,
        headers={
            'Accept': 'application/json',
            'Referer': 'https://jsonfakery.com/',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json().get('data', [])

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
              'vote_average': float(item.get('vote_average', 0.0)),
              'vote_count': int(item.get('vote_count', 0)),
              'popularity': float(item.get('popularity', 0.0)),
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
                  'popularity': float(cast.get('popularity', 0.0)),
              }
          )
          movie.casts.add(cast_obj)
    request.session['last_fetched_api_page'] = next_page
    return redirect('home')
  except requests.HTTPError as e:
      status_code = e.response.status_code if e.response is not None else None
      logger.warning(
          "Movie API request failed: page=%s status=%s",
          next_page,
          status_code,
      )
      if status_code == 403:
          messages.error(
              request,
              f"The movie provider refused page {next_page} (HTTP 403). "
              "Please try again later.",
          )
      else:
          messages.error(request, f"The movie provider returned HTTP {status_code}.")
      return redirect('home')
  except requests.RequestException as e:
      messages.error(request, "Could not reach the movie provider. Please try again later.")
      return redirect('home')
      
def home(request):
    
    movies = Movie.objects.prefetch_related('casts').order_by('id')
    search = request.GET.get('q')
    if search:
      movies = movies.filter(original_title__icontains=search)
    paginator = Paginator(movies,20)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'movies/home.html', {'movies': page_obj})


def registerUser(request):
  if request.method == "POST":
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request,user)
      return redirect('home')
  else:
    form = UserCreationForm()
  return render(request,'user/register.html',{'form':form})

def loginUser(request):
  if request.method == "POST":
    data = request.POST
    form = AuthenticationForm(request,data)
    if form.is_valid():
      user = form.get_user()
      login(request,user)
      return redirect('home')
  else:
    form = AuthenticationForm()
  return render(request,'user/login.html',{'form':form})

def logoutUser(request):
  if request.method == "POST":
    logout(request)
    return redirect("home")

@login_required(login_url="login")
def profile(request):
    liked_movies = request.user.Watchlist.all()
    return render(request, 'movies/home.html', {'movies': liked_movies})

@login_required(login_url="login")
def watchlist(request,movie_id):
  if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        if request.user in movie.user.all():
            movie.user.remove(request.user)
        else:
            movie.user.add(request.user)
  return redirect(request.META.get('HTTP_REFERER', 'home'))


def CastView(request,movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    release_year = movie.release_date[-4:] if movie.release_date else ''
    return render(request, 'movies/details.html', {
        'movie': movie,
        'releaseYear': release_year,
        'cast_list': movie.casts.all(),
    })
