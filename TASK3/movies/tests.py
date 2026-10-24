from django.test import TestCase, override_settings

from .models import Movie


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class HomeViewTests(TestCase):
    def test_home_paginates_movies_in_stable_order(self):
        Movie.objects.create(
            id="movie-b",
            original_title="Movie B",
            overview="",
            original_language="en",
        )
        Movie.objects.create(
            id="movie-a",
            original_title="Movie A",
            overview="",
            original_language="en",
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [movie.id for movie in response.context["movies"]],
            ["movie-a", "movie-b"],
        )
