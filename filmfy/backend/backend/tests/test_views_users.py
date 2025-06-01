import pytest
import os
from unittest.mock import MagicMock, patch, mock_open
from io import BytesIO
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import (
    HTTPCreated, HTTPNotFound, HTTPBadRequest, HTTPConflict,
    HTTPUnauthorized, HTTPOk, HTTPNoContent, HTTPForbidden
)
import sqlalchemy.exc # Untuk mock IntegrityError

# Sesuaikan path import ini jika berbeda
from ..views.users import UserViews, _save_profile_photo, _delete_profile_photo, check_authorization
from ..models.user import User as RealUserModel # Model User yang asli

# --- PATH PENTING UNTUK PATCHING (Sesuaikan dengan struktur Anda) ---
VIEWS_USERS_MODULE_PATH = 'backend.views.users'
USER_MODEL_PATH_IN_VIEWS = f'{VIEWS_USERS_MODULE_PATH}.User' # User model seperti yang diimpor di views.users
CHECK_AUTH_PATH_IN_VIEWS = f'{VIEWS_USERS_MODULE_PATH}.check_authorization'
SAVE_PHOTO_PATH_IN_VIEWS = f'{VIEWS_USERS_MODULE_PATH}._save_profile_photo'
DELETE_PHOTO_PATH_IN_VIEWS = f'{VIEWS_USERS_MODULE_PATH}._delete_profile_photo'
# Untuk mock modul bawaan yang digunakan di views.users
OS_PATH_VIEWS_USERS = f'{VIEWS_USERS_MODULE_PATH}.os'
SHUTIL_PATH_VIEWS_USERS = f'{VIEWS_USERS_MODULE_PATH}.shutil'
UUID_PATH_VIEWS_USERS = f'{VIEWS_USERS_MODULE_PATH}.uuid'
OPEN_PATH_VIEWS_USERS = f'{VIEWS_USERS_MODULE_PATH}.open'


@pytest.fixture
def dummy_user_request(tmp_path): # Menggunakan tmp_path untuk isolasi file system
    request = DummyRequest()
    request.dbsession = MagicMock()
    request.session = MagicMock() # Mock Pyramid session
    request.POST = {} # Untuk form data
    request.json_body = {} # Untuk JSON body
    request.matchdict = {}
    request.registry = MagicMock() # Mock registry
    request.registry.settings = {} # Mock settings di dalam registry
    request.application_url = "http://example.com"
    
    # Override PROFILE_PIC_UPLOAD_DIR untuk tes, arahkan ke tmp_path
    # Ini perlu di-patch di mana PROFILE_PIC_UPLOAD_DIR didefinisikan atau digunakan oleh _save/_delete
    global PROFILE_PIC_UPLOAD_DIR_TEST_USERS
    PROFILE_PIC_UPLOAD_DIR_TEST_USERS = tmp_path / "static_test" / "profile_pics"
    os.makedirs(PROFILE_PIC_UPLOAD_DIR_TEST_USERS, exist_ok=True)
    return request

@pytest.fixture
def user_view_instance(dummy_user_request):
    return UserViews(dummy_user_request)

# --- Tes untuk Helper Functions di views/users.py (jika belum dicakup di test_views_movies) ---
# Jika _save_profile_photo dan _delete_profile_photo identik dengan _save_poster,
# Anda mungkin tidak perlu mengulang tesnya jika sudah dicakup dengan baik.
# Namun, jika ada perbedaan, tes di sini. Untuk contoh, saya akan buat kerangka singkat.

class TestUserViewHelperFunctions:
    @patch(f'{VIEWS_USERS_MODULE_PATH}.shutil.copyfileobj')
    @patch(f'{VIEWS_USERS_MODULE_PATH}.open', new_callable=mock_open)
    @patch(f'{VIEWS_USERS_MODULE_PATH}.uuid.uuid4')
    @patch(f'{VIEWS_USERS_MODULE_PATH}.os.path.splitext')
    def test_save_profile_photo_success(self, mock_splitext, mock_uuid4, mock_file_open, mock_copyfileobj, tmp_path):
        # Mirip dengan test_save_poster_success, sesuaikan nama file dan path
        # Pastikan Anda mem-patch PROFILE_PIC_UPLOAD_DIR di dalam views.users jika digunakan oleh helper ini
        with patch(f'{VIEWS_USERS_MODULE_PATH}.PROFILE_PIC_UPLOAD_DIR', str(tmp_path)):
            mock_photo_file = MagicMock(filename="profile.png", file=BytesIO(b"imgdata"))
            mock_photo_file.file.seek = MagicMock()
            mock_uuid4.return_value = "user-photo-uuid"
            mock_splitext.return_value = ('profile', '.png')
            
            saved_path = _save_profile_photo(mock_photo_file)
            
            assert saved_path == 'profile_pics/user-photo-uuid.png'
            mock_file_open.assert_called_once_with(os.path.join(str(tmp_path), "user-photo-uuid.png"), 'wb')
            mock_copyfileobj.assert_called_once()
            mock_photo_file.file.seek.assert_called_once_with(0) 


    def test_check_authorization_success(self, dummy_user_request):
        dummy_user_request.session = {'user_id': 10}
        result = check_authorization(dummy_user_request, required_user_id=10)
        assert result is True

    def test_check_authorization_unauthorized_no_session(self, dummy_user_request):
        dummy_user_request.session = {} # Tidak ada user_id
        with pytest.raises(HTTPUnauthorized) as excinfo:
            check_authorization(dummy_user_request, required_user_id=10)
        assert 'Authentication required' in excinfo.value.json_body['error']
        
    def test_check_authorization_forbidden_wrong_user(self, dummy_user_request):
        dummy_user_request.session = {'user_id': 10} # User login ID 10
        with pytest.raises(HTTPForbidden) as excinfo:
            check_authorization(dummy_user_request, required_user_id=20) # Mencoba akses resource user ID 20
        assert 'You are not authorized' in excinfo.value.json_body['error']


class TestUserViewsIntegration: # Ganti nama jika perlu, ini untuk view methods

    # --- SIGNUP ---
    @patch(SAVE_PHOTO_PATH_IN_VIEWS) # Patch helper _save_profile_photo
    @patch(USER_MODEL_PATH_IN_VIEWS)  # Patch model User
    def test_signup_view_success(self, MockUserClass, mock_save_photo, user_view_instance, dummy_user_request):
        # Arrange
        dummy_user_request.POST = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'bio': 'A new bio',
            'foto_profil': MagicMock(filename="avatar.jpg", file=BytesIO(b"pic")) # Mock file
        }
        mock_save_photo.return_value = "profile_pics/saved_avatar.jpg"
        
        # Mock instance User yang akan dibuat
        mock_created_user_instance = MagicMock(spec=RealUserModel)
        mock_created_user_instance.id = 1 # Harus di-set karena digunakan untuk session
        mock_created_user_instance.to_dict.return_value = {
            'id': 1, 'username': 'newuser', 'email': 'new@example.com', 'bio': 'A new bio',
            'profile_photo': "profile_pics/saved_avatar.jpg", 
            'profile_url': f"{dummy_user_request.application_url}/static/profile_pics/saved_avatar.jpg"
        }
        MockUserClass.return_value = mock_created_user_instance

        # Act
        response = user_view_instance.signup_view()

        # Assert
        mock_save_photo.assert_called_once_with(dummy_user_request.POST['foto_profil'])
        MockUserClass.assert_called_once_with(
            username='newuser', email='new@example.com', bio='A new bio',
            profile_photo="profile_pics/saved_avatar.jpg"
        )
        mock_created_user_instance.set_password.assert_called_once_with('Password123!')
        dummy_user_request.dbsession.add.assert_called_once_with(mock_created_user_instance)
        dummy_user_request.dbsession.flush.assert_called_once()
        
        # Cek session
        dummy_user_request.session.__setitem__.assert_any_call('user_id', 1) # user_id diset ke ID user baru
        dummy_user_request.session.save.assert_called_once()

        assert isinstance(response, HTTPCreated)
        assert response.json_body['message'] == 'User created and logged in successfully!'
        assert response.json_body['user']['username'] == 'newuser'

    @patch(USER_MODEL_PATH_IN_VIEWS)
    def test_signup_view_username_exists(self, MockUserClass, user_view_instance, dummy_user_request):
        # Arrange
        dummy_user_request.POST = { # Data valid minimal
            'username': 'existinguser', 'email': 'unique@example.com',
            'password': 'Password123!', 'confirm_password': 'Password123!'
        }
        # Simulasikan IntegrityError saat dbsession.flush() atau .add()
        dummy_user_request.dbsession.flush.side_effect = sqlalchemy.exc.IntegrityError("mock", "mock", "mock")

        # Act
        response = user_view_instance.signup_view()

        # Assert
        assert isinstance(response, HTTPConflict)
        assert response.json_body['error'] == 'Username or email already exists.'
        dummy_user_request.dbsession.rollback.assert_called_once()

    def test_signup_view_passwords_do_not_match(self, user_view_instance, dummy_user_request):
        # Arrange
        dummy_user_request.POST = {
            'username': 'user', 'email': 'match@example.com',
            'password': 'Password123!', 'confirm_password': 'PasswordMISMATCH'
        }
        # Act
        response = user_view_instance.signup_view()
        # Assert
        assert isinstance(response, HTTPBadRequest)
        assert response.json_body['error'] == 'Passwords do not match.'

    def test_signup_view_missing_fields(self, user_view_instance, dummy_user_request):
        # Arrange
        dummy_user_request.POST = {'username': 'user'} # Field lain hilang
        # Act
        response = user_view_instance.signup_view()
        # Assert
        assert isinstance(response, HTTPBadRequest)
        assert 'Username, email, password, and confirm password are required.' in response.json_body['error']


    # --- LOGIN ---
    @patch(USER_MODEL_PATH_IN_VIEWS) # Patch User model
    def test_login_view_success(self, MockUserClass, user_view_instance, dummy_user_request):
        dummy_user_request.json_body = {'email': 'login@example.com', 'password': 'Password123!'}

        mock_user_instance = MagicMock(spec=RealUserModel) # Ganti nama variabel agar lebih jelas
        mock_user_instance.id = 5
        mock_user_instance.check_password.return_value = True
        mock_user_instance.to_dict.return_value = {'id': 5, 'email': 'login@example.com', 'username': 'loginuser'}

        # --- PERBAIKAN CARA MOCKING ---
        mock_query_method = dummy_user_request.dbsession.query  # Dapatkan mock untuk method query
        query_result_mock = mock_query_method.return_value      # Ini adalah mock yang dikembalikan oleh query()
        filter_by_result_mock = query_result_mock.filter_by.return_value # Ini dari filter_by()
        filter_by_result_mock.first.return_value = mock_user_instance # Ini dari first()
        # -----------------------------

        response = user_view_instance.login_view()

        # Assert
        mock_query_method.assert_called_once_with(MockUserClass) # Assert pada mock_query_method
        query_result_mock.filter_by.assert_called_once_with(email='login@example.com')
        filter_by_result_mock.first.assert_called_once_with()
        mock_user_instance.check_password.assert_called_once_with('Password123!')

        dummy_user_request.session.__setitem__.assert_any_call('user_id', 5)
        dummy_user_request.session.save.assert_called_once()

        assert isinstance(response, HTTPOk)
        assert response.json_body['message'] == 'Login successful!'
        assert response.json_body['user']['id'] == 5

    def test_login_view_invalid_credentials_user_not_found(self, user_view_instance, dummy_user_request):
        # Arrange
        dummy_user_request.json_body = {'email': 'nonexistent@example.com', 'password': 'Password123!'}
        # Simulasikan query tidak menemukan user
        dummy_user_request.dbsession.query(RealUserModel).filter_by().first.return_value = None

        # Act
        response = user_view_instance.login_view()

        # Assert
        assert isinstance(response, HTTPUnauthorized)
        assert response.json_body['error'] == 'Invalid email or password.'

    @patch(USER_MODEL_PATH_IN_VIEWS)
    def test_login_view_invalid_credentials_wrong_password(self, MockUserClass, user_view_instance, dummy_user_request):
        # Arrange
        dummy_user_request.json_body = {'email': 'user@example.com', 'password': 'WrongPassword'}
        mock_user = MagicMock(spec=RealUserModel)
        mock_user.check_password.return_value = False # Password salah
        dummy_user_request.dbsession.query(MockUserClass).filter_by().first.return_value = mock_user

        # Act
        response = user_view_instance.login_view()
        # Assert
        assert isinstance(response, HTTPUnauthorized)
        assert response.json_body['error'] == 'Invalid email or password.'

    # --- LOGOUT ---
    def test_logout_view_success(self, user_view_instance, dummy_user_request):
        # Arrange
        # Mock settings untuk session key
        dummy_user_request.registry.settings = {'session.key': 'my_session_cookie'}
        dummy_user_request.response = MagicMock() # Mock response object untuk delete_cookie

        # Act
        response = user_view_instance.logout_view()

        # Assert
        dummy_user_request.session.invalidate.assert_called_once()
        dummy_user_request.response.delete_cookie.assert_called_once_with(
            'my_session_cookie', path='/', domain=None # Sesuaikan jika Anda punya path/domain custom
        )
        assert isinstance(response, HTTPOk)
        assert response.json_body['message'] == 'Logout successful!'

    # --- CHECK AUTH ---
    @patch(USER_MODEL_PATH_IN_VIEWS)
    def test_check_auth_view_authenticated(self, MockUserClassInView, user_view_instance, dummy_user_request): # Ganti nama argumen patch
        # Arrange
        # Konfigurasi mock session agar 'in' operator bekerja
        dummy_user_request.session.__contains__ = MagicMock(return_value=True) # <--- TAMBAHAN PENTING
        dummy_user_request.session.__getitem__ = MagicMock(return_value=10)    # <--- TAMBAHAN PENTING (untuk session['user_id'])
        # Atau Anda bisa membuat session menjadi dictionary sungguhan jika lebih mudah:
        # dummy_user_request.session = {'user_id': 10} # Jika session adalah dict-like yang sebenarnya

        # Jika Anda tetap menggunakan MagicMock untuk session, maka assignment user_id juga perlu dimock jika diakses via __getitem__
        # dummy_user_request.session['user_id'] = 10 # Ini akan memanggil __setitem__ pada mock,
                                                    # yang mungkin tidak cukup untuk __getitem__ atau __contains__
                                                    # kecuali __getitem__ juga di-mock.

        mock_user_to_return = MagicMock(spec=RealUserModel)
        mock_user_to_return.to_dict.return_value = {'id': 10, 'username': 'authed_user'}
        
        mock_query_method = dummy_user_request.dbsession.query
        query_result_mock = mock_query_method.return_value 
        query_result_mock.get.return_value = mock_user_to_return

        # Act
        response = user_view_instance.check_auth_view()

        # Assert
        dummy_user_request.session.__contains__.assert_called_with('user_id') # Pastikan 'in' dicek
        dummy_user_request.session.__getitem__.assert_called_with('user_id') # Pastikan 'user_id' diambil
        
        assert isinstance(response, HTTPOk)
        mock_query_method.assert_called_once_with(MockUserClassInView) 
        query_result_mock.get.assert_called_once_with(10)
        
        assert response.json_body['isAuthenticated'] is True
        assert response.json_body['user']['id'] == 10
        
    def test_check_auth_view_not_authenticated_no_session_id(self, user_view_instance, dummy_user_request):
        # Arrange
        dummy_user_request.session = {} # Tidak ada user_id
        # Act
        response = user_view_instance.check_auth_view()
        # Assert
        assert isinstance(response, HTTPOk)
        assert response.json_body['isAuthenticated'] is False
        assert response.json_body['user'] is None
        
    @patch(USER_MODEL_PATH_IN_VIEWS)
    def test_check_auth_view_session_id_user_not_found(self, MockUserClassInView, user_view_instance, dummy_user_request):
        # Arrange
        # Konfigurasi mock session
        dummy_user_request.session.__contains__ = MagicMock(return_value=True) # <--- TAMBAHAN PENTING
        dummy_user_request.session.__getitem__ = MagicMock(return_value=99)    # <--- TAMBAHAN PENTING

        mock_query_method = dummy_user_request.dbsession.query
        query_result_mock = mock_query_method.return_value
        query_result_mock.get.return_value = None # User tidak ditemukan

        # Act
        response = user_view_instance.check_auth_view()

        # Assert
        dummy_user_request.session.__contains__.assert_called_with('user_id')
        dummy_user_request.session.__getitem__.assert_called_with('user_id')

        assert isinstance(response, HTTPOk)
        assert response.json_body['isAuthenticated'] is False
        assert response.json_body['user'] is None
        
        mock_query_method.assert_called_once_with(MockUserClassInView) 
        query_result_mock.get.assert_called_once_with(99)


    # --- GET PROFILE ---
    @patch(USER_MODEL_PATH_IN_VIEWS)
    def test_get_profile_view_success(self, MockUserClass, user_view_instance, dummy_user_request):
        # Arrange
        user_id = 1
        dummy_user_request.matchdict['id'] = str(user_id)
        mock_user_profile = MagicMock(spec=RealUserModel)
        mock_user_profile.to_dict.return_value = {'id': user_id, 'username': 'profile_user'}
        dummy_user_request.dbsession.query(MockUserClass).get.return_value = mock_user_profile

        # Act
        response = user_view_instance.get_profile_view()

        # Assert
        assert isinstance(response, HTTPOk)
        assert response.json_body['username'] == 'profile_user'
        dummy_user_request.dbsession.query(MockUserClass).get.assert_called_once_with(user_id)

    def test_get_profile_view_user_not_found(self, user_view_instance, dummy_user_request):
        # Arrange
        user_id = 99
        dummy_user_request.matchdict['id'] = str(user_id)
        dummy_user_request.dbsession.query(RealUserModel).get.return_value = None

        # Act
        response = user_view_instance.get_profile_view()
        # Assert
        assert isinstance(response, HTTPNotFound)
        assert response.json_body['error'] == 'User not found'

    # --- UPDATE PROFILE ---
    @patch(CHECK_AUTH_PATH_IN_VIEWS) # Patch helper check_authorization
    @patch(SAVE_PHOTO_PATH_IN_VIEWS) # Patch helper _save_profile_photo
    @patch(DELETE_PHOTO_PATH_IN_VIEWS) # Patch helper _delete_profile_photo
    @patch(USER_MODEL_PATH_IN_VIEWS)   # Patch model User
    def test_update_profile_view_success_with_new_photo(
        self, MockUserClass, mock_delete_photo, mock_save_photo, mock_check_auth, 
        user_view_instance, dummy_user_request
    ):
        # Arrange
        user_id_to_update = 10
        dummy_user_request.matchdict['id'] = str(user_id_to_update)
        mock_check_auth.return_value = True # Pengguna terotorisasi

        dummy_user_request.POST = {
            'username': 'updated_username',
            'email': 'updated@example.com',
            'bio': 'Updated bio here.',
            'foto_profil': MagicMock(filename="new_avatar.png", file=BytesIO(b"newpic"))
        }

        existing_user_mock = MagicMock(spec=RealUserModel)
        existing_user_mock.id = user_id_to_update
        existing_user_mock.username = "old_username"
        existing_user_mock.email = "old@example.com"
        existing_user_mock.bio = "Old bio"
        existing_user_mock.profile_photo = "profile_pics/old_avatar.png" # Foto lama ada

        def to_dict_side_effect_update(request=None): # Untuk memastikan data terbaru di to_dict
            return {
                'id': existing_user_mock.id, 'username': existing_user_mock.username,
                'email': existing_user_mock.email, 'bio': existing_user_mock.bio,
                'profile_photo': existing_user_mock.profile_photo,
                'profile_url': f"{dummy_user_request.application_url}/static/{existing_user_mock.profile_photo}" if existing_user_mock.profile_photo and request else None
            }
        existing_user_mock.to_dict.side_effect = to_dict_side_effect_update
        
        dummy_user_request.dbsession.query(MockUserClass).get.return_value = existing_user_mock
        mock_save_photo.return_value = "profile_pics/new_saved_avatar.png"
        mock_delete_photo.return_value = True

        # Act
        response = user_view_instance.update_profile_view()

        # Assert
        mock_check_auth.assert_called_once_with(dummy_user_request, user_id_to_update)
        dummy_user_request.dbsession.query(MockUserClass).get.assert_called_once_with(user_id_to_update)
        
        mock_delete_photo.assert_called_once_with("profile_pics/old_avatar.png")
        mock_save_photo.assert_called_once_with(dummy_user_request.POST['foto_profil'])
        
        assert existing_user_mock.username == 'updated_username'
        assert existing_user_mock.email == 'updated@example.com'
        assert existing_user_mock.bio == 'Updated bio here.'
        assert existing_user_mock.profile_photo == "profile_pics/new_saved_avatar.png"
        
        dummy_user_request.dbsession.flush.assert_called_once()
        assert isinstance(response, HTTPOk)
        assert response.json_body['message'] == 'Profile updated successfully!'
        assert response.json_body['user']['username'] == 'updated_username'

    @patch(CHECK_AUTH_PATH_IN_VIEWS)
    def test_update_profile_view_forbidden(self, mock_check_auth, user_view_instance, dummy_user_request):
        # Arrange
        user_id_to_update = 10
        dummy_user_request.matchdict['id'] = str(user_id_to_update)
        # Simulasikan check_authorization melempar HTTPForbidden
        mock_check_auth.side_effect = HTTPForbidden(json_body={'error': 'Forbidden'})
        dummy_user_request.POST = {'username': 'any_update'} # Data minimal

        # Act
        response = user_view_instance.update_profile_view()

        # Assert
        assert isinstance(response, HTTPForbidden)
        assert response.json_body['error'] == 'Forbidden'
        dummy_user_request.dbsession.flush.assert_not_called()

    # --- DELETE USER ---
    @patch(CHECK_AUTH_PATH_IN_VIEWS)
    @patch(DELETE_PHOTO_PATH_IN_VIEWS)
    @patch(USER_MODEL_PATH_IN_VIEWS)
    def test_delete_user_view_success(
        self, MockUserClass, mock_delete_photo, mock_check_auth,
        user_view_instance, dummy_user_request
    ):
        # Arrange
        user_id_to_delete = 10
        dummy_user_request.matchdict['id'] = str(user_id_to_delete)
        mock_check_auth.return_value = True

        existing_user_mock = MagicMock(spec=RealUserModel)
        existing_user_mock.id = user_id_to_delete
        existing_user_mock.profile_photo = "profile_pics/some_photo.jpg"
        dummy_user_request.dbsession.query(MockUserClass).get.return_value = existing_user_mock
        mock_delete_photo.return_value = True

        # Act
        response = user_view_instance.delete_user_view()

        # Assert
        mock_check_auth.assert_called_once_with(dummy_user_request, user_id_to_delete)
        dummy_user_request.dbsession.query(MockUserClass).get.assert_called_once_with(user_id_to_delete)
        mock_delete_photo.assert_called_once_with(existing_user_mock.profile_photo)
        dummy_user_request.dbsession.delete.assert_called_once_with(existing_user_mock)
        dummy_user_request.dbsession.flush.assert_called_once()
        dummy_user_request.session.invalidate.assert_called_once() # Cek session dihapus
        assert isinstance(response, HTTPNoContent)

    # Tambahkan tes lain untuk kasus:
    # - update_profile_view: user not found, username/email conflict (IntegrityError)
    # - delete_user_view: user not found, forbidden