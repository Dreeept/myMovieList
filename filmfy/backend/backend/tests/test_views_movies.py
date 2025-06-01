# filmfy/backend/backend/tests/test_views_movies.py
import pytest
import os # Untuk os.path.join di helper
import uuid # Untuk mock uuid.uuid4
import shutil # Untuk mock shutil.copyfileobj
from io import BytesIO # Untuk mock file
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import (
    HTTPCreated, HTTPNotFound, HTTPBadRequest, HTTPNoContent, HTTPOk, HTTPUnauthorized
)
from unittest.mock import MagicMock, patch, mock_open
from ..models.movie import Movie as RealMovieModel

# --- PATH PENTING UNTUK PATCHING ---
# Sesuaikan 'filmfy.backend.backend' dengan nama root package aplikasi Anda
# jika berbeda. Ini adalah asumsi berdasarkan struktur yang umum.
VIEWS_MODULE_PATH = 'backend.views.movies'
MODELS_MOVIE_PATH = f'{VIEWS_MODULE_PATH}.Movie' # Movie seperti yang diimpor di views.movies
CHECK_SESSION_PATH = f'{VIEWS_MODULE_PATH}.check_session'
SAVE_POSTER_PATH = f'{VIEWS_MODULE_PATH}._save_poster'
DELETE_POSTER_PATH = f'{VIEWS_MODULE_PATH}._delete_poster'
OS_PATH = f'{VIEWS_MODULE_PATH}.os' # Jika Anda memanggil os.path, os.makedirs, os.remove
SHUTIL_PATH = f'{VIEWS_MODULE_PATH}.shutil'
UUID_PATH = f'{VIEWS_MODULE_PATH}.uuid'
OPEN_PATH = f'{VIEWS_MODULE_PATH}.open' # Untuk built-in open


# Impor class View dan helper jika ingin mengujinya secara terpisah juga
from ..views.movies import MovieViews, _save_poster, _delete_poster, check_session, POSTER_UPLOAD_DIR
from ..models.movie import Movie as RealMovieModel # Untuk membuat instance di data


# --- Pytest Fixtures ---
@pytest.fixture
def dummy_request(tmp_path): # tmp_path adalah fixture pytest untuk temporary directory
    request = DummyRequest()
    request.dbsession = MagicMock()
    request.session = MagicMock() # Mock session object
    request.POST = MagicMock() # Mock POST data
    request.matchdict = {}
    request.application_url = "http://example.com"

    # Pastikan POSTER_UPLOAD_DIR menggunakan tmp_path untuk isolasi tes file system
    # Ini akan me-override POSTER_UPLOAD_DIR di views.movies selama tes ini
    global POSTER_UPLOAD_DIR_TEST
    POSTER_UPLOAD_DIR_TEST = tmp_path / "static" / "postersMovie"
    os.makedirs(POSTER_UPLOAD_DIR_TEST, exist_ok=True)
    return request

@pytest.fixture
def movie_view_instance(dummy_request):
    return MovieViews(dummy_request)

# --- Tes untuk Helper Functions ---

class TestHelperFunctions:
    # Menggunakan patch untuk views.movies.os, views.movies.uuid, dll.
    @patch(f'{VIEWS_MODULE_PATH}.shutil.copyfileobj')
    @patch(f'{VIEWS_MODULE_PATH}.open', new_callable=mock_open)
    @patch(f'{VIEWS_MODULE_PATH}.uuid.uuid4')
    @patch(f'{VIEWS_MODULE_PATH}.os.path.splitext')
    def test_save_poster_success(self, mock_splitext_param, mock_uuid4_param, mock_file_open_param, mock_copyfileobj_param, tmp_path):
        # Arrange
        mock_poster_file = MagicMock()
        mock_poster_file.filename = "test_image.jpg"
        mock_poster_file.file = BytesIO(b"file_content")

        # PENTING: Mock method 'seek' pada objek BytesIO SEBELUM _save_poster dipanggil
        mock_poster_file.file.seek = MagicMock()

        # Atur return value untuk mock lainnya
        mock_uuid4_param.return_value = "test-uuid"
        # Pastikan return value mock_splitext_param sesuai dengan yang diharapkan os.path.splitext
        # yaitu tuple (nama_tanpa_ekstensi, ekstensi)
        mock_splitext_param.return_value = ('test_image', '.jpg') 

        expected_unique_filename = "test-uuid.jpg" # Ini berdasarkan mock_uuid4 dan mock_splitext
        expected_path_in_db = f"postersMovie/{expected_unique_filename}"
        expected_full_output_path = os.path.join(str(tmp_path), expected_unique_filename)

        # Act
        # Panggil _save_poster HANYA SEKALI setelah semua mock yang relevan (termasuk .seek) disiapkan
        with patch(f'{VIEWS_MODULE_PATH}.POSTER_UPLOAD_DIR', str(tmp_path)):
            saved_filename = _save_poster(mock_poster_file)

        # Assert
        # Verifikasi mock parameter decorator
        mock_splitext_param.assert_called_once_with("test_image.jpg")
        mock_uuid4_param.assert_called_once()
        mock_file_open_param.assert_called_once_with(expected_full_output_path, 'wb')
        
        # Verifikasi bahwa shutil.copyfileobj dipanggil. Anda bisa lebih spesifik dengan argumennya jika perlu.
        # mock_file_handle_opened = mock_file_open_param.return_value # atau mock_file_open_param().__enter__.return_value jika mock_open adalah context manager
        # mock_copyfileobj_param.assert_called_once_with(mock_poster_file.file, mock_file_handle_opened)
        mock_copyfileobj_param.assert_called_once() # Versi sederhana

        # Verifikasi bahwa mock_poster_file.file.seek dipanggil oleh _save_poster
        # Ini adalah inti perbaikannya.
        mock_poster_file.file.seek.assert_called_once_with(0)

        # Verifikasi hasil fungsi _save_poster
        assert saved_filename == expected_path_in_db

        # Baris 'mock_poster_file.file.seek(0)' yang Anda tambahkan di akhir harus dihapus
        # karena itu akan mengganggu assertion_called_once_with jika dipanggil lagi.

    def test_save_poster_no_file(self):
        assert _save_poster(None) is None
        mock_poster_file_no_filename = MagicMock(filename=None, file=BytesIO(b"content"))
        assert _save_poster(mock_poster_file_no_filename) is None
        mock_poster_file_no_file_attr = MagicMock(filename="file.jpg")
        del mock_poster_file_no_file_attr.file # Hapus atribut file
        assert _save_poster(mock_poster_file_no_file_attr) is None

    @patch(f'{VIEWS_MODULE_PATH}.os.remove')
    @patch(f'{VIEWS_MODULE_PATH}.os.path.exists')
    def test_delete_poster_success(self, mock_os_exists, mock_os_remove, tmp_path):
        poster_path_in_db = "postersMovie/existing_poster.jpg"
        actual_filename = "existing_poster.jpg"
        full_disk_path = os.path.join(str(tmp_path), actual_filename)

        mock_os_exists.return_value = True
        
        with patch(f'{VIEWS_MODULE_PATH}.POSTER_UPLOAD_DIR', str(tmp_path)):
            result = _delete_poster(poster_path_in_db)

        # mock_os_join.assert_called_once_with(str(tmp_path), actual_filename)
        mock_os_exists.assert_called_once_with(full_disk_path)
        mock_os_remove.assert_called_once_with(full_disk_path)
        assert result is True

    @patch(f'{VIEWS_MODULE_PATH}.os.remove')
    @patch(f'{VIEWS_MODULE_PATH}.os.path.exists')
    def test_delete_poster_not_exists(self, mock_os_exists, mock_os_remove, tmp_path):
        poster_path_in_db = "postersMovie/non_existing_poster.jpg"
        actual_filename = "non_existing_poster.jpg"
        full_disk_path = os.path.join(str(tmp_path), actual_filename)

        mock_os_exists.return_value = False # File tidak ada

        with patch(f'{VIEWS_MODULE_PATH}.POSTER_UPLOAD_DIR', str(tmp_path)):
            result = _delete_poster(poster_path_in_db)

        # mock_os_join.assert_called_once_with(str(tmp_path), actual_filename)
        mock_os_exists.assert_called_once_with(full_disk_path)
        mock_os_remove.assert_not_called()
        assert result is False

    def test_delete_poster_none_path(self):
        assert _delete_poster(None) is False

    def test_check_session_authenticated(self, dummy_request):
        dummy_request.session = {'user_id': 123} # User terautentikasi
        user_id = check_session(dummy_request)
        assert user_id == 123

    def test_check_session_unauthorized(self, dummy_request):
        dummy_request.session = {} # Tidak ada user_id di session
        with pytest.raises(HTTPUnauthorized) as excinfo:
            check_session(dummy_request)
        assert excinfo.value.json_body['error'] == 'Authentication required. Please log in.'


# --- Tes untuk MovieViews Class ---

class TestMovieViews:

    # --- CREATE ---
    @patch(SAVE_POSTER_PATH) # Patch _save_poster di dalam views.movies
    @patch(MODELS_MOVIE_PATH) # Patch Movie class di dalam views.movies
    @patch(CHECK_SESSION_PATH) # Patch check_session di dalam views.movies
    def test_create_movie_success_with_poster(self, mock_check_session, MockMovieClass, mock_save_poster, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1 # User ID (terautentikasi)
        
        # Mock request.POST data (form data)
        dummy_request.POST = {
            'title': 'New Movie Title',
            'genre': 'Comedy',
            'release_year': '2023',
            'rating': '8',
            'poster': MagicMock(filename="poster.jpg", file=BytesIO(b"imgdata")) # Mock file upload
        }
        
        mock_save_poster.return_value = "postersMovie/generated_uuid.jpg"
        
        mock_created_movie_instance = MagicMock(spec=RealMovieModel) # Instance dari Movie yang di-mock
        mock_created_movie_instance.to_dict.return_value = { # Apa yang akan dikembalikan oleh to_dict()
            'id': 1, 'title': 'New Movie Title', 'genre': 'Comedy', 
            'release_year': 2023, 'rating': 8, 
            'poster_path': "postersMovie/generated_uuid.jpg",
            'poster_url': f"{dummy_request.application_url}/static/postersMovie/generated_uuid.jpg"
        }
        MockMovieClass.return_value = mock_created_movie_instance # Saat Movie(...) dipanggil, kembalikan mock ini

        # Act
        response = movie_view_instance.create_movie()

        # Assert
        mock_check_session.assert_called_once_with(dummy_request)
        mock_save_poster.assert_called_once_with(dummy_request.POST['poster'])
        MockMovieClass.assert_called_once_with(
            title='New Movie Title',
            genre='Comedy',
            release_year=2023,
            rating=8,
            poster_path="postersMovie/generated_uuid.jpg"
        )
        dummy_request.dbsession.add.assert_called_once_with(mock_created_movie_instance)
        dummy_request.dbsession.flush.assert_called_once()
        
        assert isinstance(response, HTTPCreated)
        assert response.json_body['message'] == 'Movie created successfully!'
        assert response.json_body['movie']['title'] == 'New Movie Title'

    @patch(SAVE_POSTER_PATH)
    @patch(MODELS_MOVIE_PATH)
    @patch(CHECK_SESSION_PATH)
    def test_create_movie_success_without_poster(self, mock_check_session, MockMovieClass, mock_save_poster, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1
        dummy_request.POST = {
            'title': 'No Poster Movie',
            'genre': 'Drama',
            'release_year': '2024',
            'rating': '7',
            'poster': None # Tidak ada poster
        }
        mock_save_poster.return_value = None # _save_poster akan return None
        
        mock_created_movie_instance = MagicMock(spec=RealMovieModel)
        mock_created_movie_instance.to_dict.return_value = {
            'id': 2, 'title': 'No Poster Movie', 'genre': 'Drama', 
            'release_year': 2024, 'rating': 7, 
            'poster_path': None, 'poster_url': None
        }
        MockMovieClass.return_value = mock_created_movie_instance

        # Act
        response = movie_view_instance.create_movie()

        # Assert
        mock_save_poster.assert_called_once_with(None)
        MockMovieClass.assert_called_once_with(
            title='No Poster Movie',
            genre='Drama',
            release_year=2024,
            rating=7,
            poster_path=None
        )
        dummy_request.dbsession.add.assert_called_once_with(mock_created_movie_instance)
        assert isinstance(response, HTTPCreated)
        assert response.json_body['movie']['title'] == 'No Poster Movie'

    @patch(CHECK_SESSION_PATH)
    def test_create_movie_unauthorized(self, mock_check_session, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.side_effect = HTTPUnauthorized(json_body={'error': 'Auth required'})
        dummy_request.POST = {'title': 'A Movie'} # Data minimal

        # Act
        response = movie_view_instance.create_movie()

        # Assert
        assert isinstance(response, HTTPUnauthorized)
        assert response.json_body['error'] == 'Auth required'
        dummy_request.dbsession.add.assert_not_called()

    @patch(CHECK_SESSION_PATH)
    def test_create_movie_missing_title(self, mock_check_session, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1  # Simulasikan pengguna terautentikasi
        dummy_request.POST = {'genre': 'Action'}  # 'title' sengaja dihilangkan

        # Act
        response = movie_view_instance.create_movie()

        # Assert
        # 1. Pastikan respons adalah instance dari HTTPBadRequest
        assert isinstance(response, HTTPBadRequest), \
            f"Response was not HTTPBadRequest as expected. Got type: {type(response)}. Body: {getattr(response, 'json_body', 'Response has no json_body')}"

        # 2. Dapatkan pesan error aktual dari JSON body
        #    Ini penting untuk debugging jika assertion di bawah gagal.
        actual_error_message = response.json_body.get('error', 'Error key not found in json_body')
        print(f"\nDEBUG (test_create_movie_missing_title): Pesan error aktual yang diterima: '{actual_error_message}'\n")

        # 3. Verifikasi isi pesan error.
        #    Berdasarkan kode view Anda (except KeyError as e: return HTTPBadRequest(json_body={'error': f'Missing required form field: {e}'})),
        #    jika 'title' hilang, e akan menjadi KeyError('title'), dan str(e) biasanya "'title'".
        #    Jadi, pesan lengkap yang diharapkan adalah "Missing required form field: 'title'"

        expected_message_part_generic = "Missing required form field"
        expected_message_part_specific_key = "'title'" # Nama field yang hilang, biasanya dengan tanda kutip dari str(KeyError)

        assert expected_message_part_generic in actual_error_message, \
            f"Substring '{expected_message_part_generic}' tidak ditemukan dalam pesan error: '{actual_error_message}'"
        
        assert expected_message_part_specific_key in actual_error_message, \
            f"Substring spesifik field '{expected_message_part_specific_key}' tidak ditemukan dalam pesan error: '{actual_error_message}'"

        # Opsional: Jika Anda sudah sangat yakin dengan format pesan error setelah debugging dengan print,
        # Anda bisa melakukan assertion pada pesan error lengkap:
        # expected_full_message = "Missing required form field: 'title'"
        # assert actual_error_message == expected_full_message, \
        #     f"Pesan error lengkap tidak sesuai. Diharapkan: '{expected_full_message}', Diterima: '{actual_error_message}'"

    @patch(CHECK_SESSION_PATH)
    def test_create_movie_invalid_rating(self, mock_check_session, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1
        dummy_request.POST = {'title': 'Bad Rating Movie', 'rating': '11'} # Rating tidak valid

        # Act
        response = movie_view_instance.create_movie()

        # Assert
        assert isinstance(response, HTTPBadRequest)
        assert response.json_body['error'] == 'Rating must be an integer between 1 and 10'
    
    # --- LIST ---
    def test_list_movies_success(self, movie_view_instance, dummy_request):
        # Arrange
        mock_movie1 = MagicMock(spec=RealMovieModel)
        mock_movie1.to_dict.return_value = {'id': 1, 'title': 'Movie Alpha'}
        mock_movie2 = MagicMock(spec=RealMovieModel)
        mock_movie2.to_dict.return_value = {'id': 2, 'title': 'Movie Beta'}

        # --- Perbaikan Cara Mocking Rantai Pemanggilan ---
        # 1. Dapatkan mock untuk method 'query' itu sendiri
        mock_query_method = dummy_request.dbsession.query

        # 2. Atur apa yang akan dikembalikan oleh pemanggilan mock_query_method(RealMovieModel)
        query_result_mock = mock_query_method.return_value 
                        # ^ Ini adalah mock yang akan dikembalikan ketika dbsession.query(ANY_ARGUMENT) dipanggil

        # 3. Lanjutkan rantai mock dari query_result_mock
        ordered_query_result_mock = query_result_mock.order_by.return_value
        ordered_query_result_mock.all.return_value = [mock_movie1, mock_movie2]
        # --- Akhir Perbaikan Cara Mocking ---

        # Act
        response_data = movie_view_instance.list_movies()

        # Assert
        # 1. Pastikan dbsession.query (yaitu mock_query_method) dipanggil sekali dengan RealMovieModel
        mock_query_method.assert_called_once_with(RealMovieModel)

        # 2. Pastikan method order_by pada hasil query (query_result_mock) dipanggil sekali
        #    DAN dengan argumen yang benar (RealMovieModel.title)
        query_result_mock.order_by.assert_called_once_with(RealMovieModel.title)

        # 3. Pastikan method all pada hasil ordered query (ordered_query_result_mock) dipanggil sekali
        ordered_query_result_mock.all.assert_called_once()

        mock_movie1.to_dict.assert_called_once_with(request=dummy_request)
        mock_movie2.to_dict.assert_called_once_with(request=dummy_request)
        assert len(response_data) == 2
        assert response_data[0]['title'] == 'Movie Alpha'
        assert response_data[1]['title'] == 'Movie Beta'


    def test_list_movies_empty(self, movie_view_instance, dummy_request):
        # Arrange
        dummy_request.dbsession.query(RealMovieModel).order_by().all.return_value = []

        # Act
        response_data = movie_view_instance.list_movies()

        # Assert
        assert len(response_data) == 0

    # --- GET DETAIL ---
    def test_get_movie_success(self, movie_view_instance, dummy_request):
        # Arrange
        movie_id = 1
        dummy_request.matchdict['id'] = str(movie_id)
        mock_movie = MagicMock(spec=RealMovieModel)
        mock_movie.to_dict.return_value = {'id': movie_id, 'title': 'Specific Movie'}
        dummy_request.dbsession.query(RealMovieModel).get.return_value = mock_movie

        # Act
        response = movie_view_instance.get_movie()

        # Assert
        dummy_request.dbsession.query(RealMovieModel).get.assert_called_once_with(movie_id)
        mock_movie.to_dict.assert_called_once_with(request=dummy_request)
        assert response['title'] == 'Specific Movie'

    def test_get_movie_not_found(self, movie_view_instance, dummy_request):
        # Arrange
        movie_id = 99
        dummy_request.matchdict['id'] = str(movie_id)
        dummy_request.dbsession.query(RealMovieModel).get.return_value = None # Movie tidak ditemukan

        # Act
        response = movie_view_instance.get_movie()

        # Assert
        assert isinstance(response, HTTPNotFound)
        assert response.json_body['error'] == 'Movie not found'

    def test_get_movie_invalid_id_format(self, movie_view_instance, dummy_request):
        # Arrange
        dummy_request.matchdict['id'] = 'abc' # ID tidak valid

        # Act
        response = movie_view_instance.get_movie()

        # Assert
        assert isinstance(response, HTTPBadRequest)
        assert response.json_body['error'] == 'Invalid movie ID format. ID must be an integer.'

    # --- UPDATE ---
    @patch(SAVE_POSTER_PATH)
    @patch(DELETE_POSTER_PATH)
    @patch(CHECK_SESSION_PATH)
    def test_update_movie_success_with_new_poster(self, mock_check_session, mock_delete_poster, mock_save_poster, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1
        movie_id = 1
        dummy_request.matchdict['id'] = str(movie_id)

        # Mock data POST
        dummy_request.POST = {
            'title': 'Updated Title',
            'genre': 'Updated Genre',
            'release_year': '2025',
            'rating': '9',
            'poster': MagicMock(filename="new_poster.jpg", file=BytesIO(b"new_img_data"))
        }

        # Mock movie yang ada di DB
        existing_movie_mock = MagicMock(spec=RealMovieModel)
        existing_movie_mock.id = movie_id
        existing_movie_mock.title = "Old Title"
        existing_movie_mock.genre = "Old Genre"
        existing_movie_mock.release_year = 2022
        existing_movie_mock.rating = 7
        existing_movie_mock.poster_path = "postersMovie/old_poster.jpg" # Poster lama ada
        
        def to_dict_side_effect(request=None): # Side effect untuk to_dict setelah update
            return {
                'id': existing_movie_mock.id, 'title': existing_movie_mock.title,
                'genre': existing_movie_mock.genre, 'release_year': existing_movie_mock.release_year,
                'rating': existing_movie_mock.rating, 'poster_path': existing_movie_mock.poster_path,
                'poster_url': f"{dummy_request.application_url}/static/{existing_movie_mock.poster_path}" if existing_movie_mock.poster_path and request else None
            }
        existing_movie_mock.to_dict.side_effect = to_dict_side_effect

        dummy_request.dbsession.query(RealMovieModel).get.return_value = existing_movie_mock
        
        mock_save_poster.return_value = "postersMovie/new_saved_poster.jpg"
        mock_delete_poster.return_value = True # Anggap delete berhasil

        # Act
        response = movie_view_instance.update_movie()

        # Assert
        mock_check_session.assert_called_once_with(dummy_request)
        dummy_request.dbsession.query(RealMovieModel).get.assert_called_once_with(movie_id)
        
        mock_delete_poster.assert_called_once_with("postersMovie/old_poster.jpg") # Cek poster lama dihapus
        mock_save_poster.assert_called_once_with(dummy_request.POST['poster']) # Cek poster baru disimpan
        
        assert existing_movie_mock.title == 'Updated Title'
        assert existing_movie_mock.genre == 'Updated Genre'
        assert existing_movie_mock.release_year == 2025
        assert existing_movie_mock.rating == 9
        assert existing_movie_mock.poster_path == "postersMovie/new_saved_poster.jpg"
        
        dummy_request.dbsession.flush.assert_called_once()
        assert isinstance(response, HTTPOk)
        assert response.json_body['message'] == 'Movie updated successfully!'
        assert response.json_body['movie']['title'] == 'Updated Title'
        assert response.json_body['movie']['poster_path'] == "postersMovie/new_saved_poster.jpg"

    @patch(CHECK_SESSION_PATH)
    def test_update_movie_not_found(self, mock_check_session, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1
        movie_id = 99
        dummy_request.matchdict['id'] = str(movie_id)
        dummy_request.POST = {'title': 'Does not matter'}
        dummy_request.dbsession.query(RealMovieModel).get.return_value = None # Movie tidak ditemukan

        # Act
        response = movie_view_instance.update_movie()

        # Assert
        assert isinstance(response, HTTPNotFound)
        assert response.json_body['error'] == 'Movie not found'

    @patch(CHECK_SESSION_PATH)
    def test_update_movie_unauthorized(self, mock_check_session, movie_view_instance, dummy_request):
        # Arrange
        dummy_request.matchdict['id'] = '1'
        dummy_request.POST = {'title': 'A Movie'}
        mock_check_session.side_effect = HTTPUnauthorized(json_body={'error': 'Auth required'})

        # Act
        response = movie_view_instance.update_movie()

        # Assert
        assert isinstance(response, HTTPUnauthorized)
        dummy_request.dbsession.flush.assert_not_called()

    # --- DELETE ---
    @patch(DELETE_POSTER_PATH)
    @patch(CHECK_SESSION_PATH)
    def test_delete_movie_success_with_poster(self, mock_check_session, mock_delete_poster, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1
        movie_id = 1
        dummy_request.matchdict['id'] = str(movie_id)

        existing_movie_mock = MagicMock(spec=RealMovieModel)
        existing_movie_mock.id = movie_id
        existing_movie_mock.poster_path = "postersMovie/to_be_deleted.jpg" # Ada poster
        dummy_request.dbsession.query(RealMovieModel).get.return_value = existing_movie_mock
        mock_delete_poster.return_value = True

        # Act
        response = movie_view_instance.delete_movie()

        # Assert
        mock_check_session.assert_called_once_with(dummy_request)
        dummy_request.dbsession.query(RealMovieModel).get.assert_called_once_with(movie_id)
        mock_delete_poster.assert_called_once_with(existing_movie_mock.poster_path)
        dummy_request.dbsession.delete.assert_called_once_with(existing_movie_mock)
        dummy_request.dbsession.flush.assert_called_once()
        assert isinstance(response, HTTPNoContent)

    @patch(DELETE_POSTER_PATH)
    @patch(CHECK_SESSION_PATH)
    def test_delete_movie_success_without_poster(self, mock_check_session, mock_delete_poster, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1
        movie_id = 2
        dummy_request.matchdict['id'] = str(movie_id)

        existing_movie_mock = MagicMock(spec=RealMovieModel)
        existing_movie_mock.id = movie_id
        existing_movie_mock.poster_path = None # Tidak ada poster
        dummy_request.dbsession.query(RealMovieModel).get.return_value = existing_movie_mock

        # Act
        response = movie_view_instance.delete_movie()

        # Assert
        mock_delete_poster.assert_not_called() # Tidak boleh dipanggil jika poster_path None
        dummy_request.dbsession.delete.assert_called_once_with(existing_movie_mock)
        assert isinstance(response, HTTPNoContent)

    @patch(CHECK_SESSION_PATH)
    def test_delete_movie_not_found(self, mock_check_session, movie_view_instance, dummy_request):
        # Arrange
        mock_check_session.return_value = 1
        movie_id = 99
        dummy_request.matchdict['id'] = str(movie_id)
        dummy_request.dbsession.query(RealMovieModel).get.return_value = None

        # Act
        response = movie_view_instance.delete_movie()

        # Assert
        assert isinstance(response, HTTPNotFound)
        assert response.json_body['error'] == 'Movie not found'

    @patch(CHECK_SESSION_PATH)
    def test_delete_movie_unauthorized(self, mock_check_session, movie_view_instance, dummy_request):
        # Arrange
        dummy_request.matchdict['id'] = '1'
        mock_check_session.side_effect = HTTPUnauthorized(json_body={'error': 'Auth required'})

        # Act
        response = movie_view_instance.delete_movie()

        # Assert
        assert isinstance(response, HTTPUnauthorized)
        dummy_request.dbsession.delete.assert_not_called()