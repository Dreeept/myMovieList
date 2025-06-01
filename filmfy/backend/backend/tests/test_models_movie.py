# filmfy/backend/backend/tests/test_models_movie.py
import pytest
from unittest.mock import MagicMock

# Sesuaikan path import ini jika berbeda
from ..models.movie import Movie

class TestMovieModel:

    def test_movie_creation_and_attributes(self):
        # Arrange & Act
        movie_data = {
            'id': 1, # Biasanya ID di-generate DB, tapi untuk tes model bisa di-set manual
            'title': "Inception",
            'genre': "Sci-Fi",
            'release_year': 2010,
            'rating': 9,
            'poster_path': "postersMovie/inception.jpg"
        }
        movie = Movie(**movie_data)

        # Assert
        assert movie.id == movie_data['id']
        assert movie.title == movie_data['title']
        assert movie.genre == movie_data['genre']
        assert movie.release_year == movie_data['release_year']
        assert movie.rating == movie_data['rating']
        assert movie.poster_path == movie_data['poster_path']

    def test_movie_to_dict_without_request(self):
        # Arrange
        movie = Movie(
            id=1,
            title="The Dark Knight",
            genre="Action",
            release_year=2008,
            rating=9,
            poster_path="postersMovie/tdk.jpg"
        )

        # Act
        movie_dict = movie.to_dict() # Panggil tanpa argumen request

        # Assert
        expected_dict = {
            'id': 1,
            'title': "The Dark Knight",
            'genre': "Action",
            'release_year': 2008,
            'rating': 9,
            'poster_path': "postersMovie/tdk.jpg",
            'poster_url': None # Karena tidak ada request
        }
        assert movie_dict == expected_dict

    def test_movie_to_dict_with_request_and_poster_path(self):
        # Arrange
        movie = Movie(
            id=2,
            title="Interstellar",
            genre="Sci-Fi",
            release_year=2014,
            rating=9,
            poster_path="postersMovie/interstellar.jpg" # poster_path ada
        )
        mock_request = MagicMock()
        mock_request.application_url = "http://localhost:6543" # Contoh application_url

        # Act
        movie_dict = movie.to_dict(request=mock_request)

        # Assert
        expected_poster_url = "http://localhost:6543/static/postersMovie/interstellar.jpg"
        expected_dict = {
            'id': 2,
            'title': "Interstellar",
            'genre': "Sci-Fi",
            'release_year': 2014,
            'rating': 9,
            'poster_path': "postersMovie/interstellar.jpg",
            'poster_url': expected_poster_url
        }
        assert movie_dict == expected_dict

    def test_movie_to_dict_with_request_but_no_poster_path(self):
        # Arrange
        movie = Movie(
            id=3,
            title="Tenet",
            genre="Action",
            release_year=2020,
            rating=8,
            poster_path=None # poster_path tidak ada
        )
        mock_request = MagicMock()
        mock_request.application_url = "http://localhost:6543"

        # Act
        movie_dict = movie.to_dict(request=mock_request)

        # Assert
        expected_dict = {
            'id': 3,
            'title': "Tenet",
            'genre': "Action",
            'release_year': 2020,
            'rating': 8,
            'poster_path': None,
            'poster_url': None # Karena poster_path tidak ada
        }
        assert movie_dict == expected_dict

    def test_movie_to_dict_with_poster_path_but_no_request(self):
        # Arrange
        movie = Movie(
            id=4,
            title="Oppenheimer",
            genre="Biography",
            release_year=2023,
            rating=9,
            poster_path="postersMovie/oppenheimer.jpg" # poster_path ada
        )
        # Tidak ada mock_request yang diberikan ke to_dict

        # Act
        movie_dict = movie.to_dict() # Panggil tanpa argumen request

        # Assert
        expected_dict = {
            'id': 4,
            'title': "Oppenheimer",
            'genre': "Biography",
            'release_year': 2023,
            'rating': 9,
            'poster_path': "postersMovie/oppenheimer.jpg",
            'poster_url': None # Karena request tidak diberikan
        }
        assert movie_dict == expected_dict