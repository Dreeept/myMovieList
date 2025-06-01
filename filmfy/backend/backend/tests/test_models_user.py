import pytest
from unittest.mock import patch, MagicMock # patch untuk bcrypt, MagicMock untuk request

# Sesuaikan path import ini jika struktur proyek Anda berbeda
# Asumsikan User ada di ..models.user relatif terhadap direktori tests
from ..models.user import User # Ini adalah model User yang sebenarnya

# Path untuk mem-patch bcrypt SEPERTI YANG DIGUNAKAN DI DALAM models/user.py
# Jika di models/user.py Anda melakukan 'import bcrypt', maka path ini benar.
BCRYPT_PATH = 'backend.models.user.bcrypt' # <-- Perhatikan path ini!

class TestUserModel:

    def test_user_creation_and_attributes(self):
        # Arrange & Act
        user_data = {
            'id': 1, # Biasanya ID di-generate DB, tapi untuk tes model bisa di-set manual
            'username': "john_doe",
            'email': "john.doe@example.com",
            'bio': "Pengguna baru yang antusias.",
            'profile_photo': "profile_pics/johndoe.jpg"
            # hashed_password akan di-set melalui set_password
        }
        user = User(**user_data)

        # Assert
        assert user.id == user_data['id']
        assert user.username == user_data['username']
        assert user.email == user_data['email']
        assert user.bio == user_data['bio']
        assert user.profile_photo == user_data['profile_photo']
        # Awalnya hashed_password mungkin tidak None jika SQLAlchemy memberikan default,
        # tapi karena kita tidak set, dan tidak ada default eksplisit di model,
        # ini akan bergantung pada bagaimana instance dibuat.
        # Jika Anda selalu memanggil set_password, maka hashed_password akan diisi.
        # Untuk tes ini, kita asumsikan bisa None atau string kosong sebelum set_password.
        # Jika ada default nullable=False, maka harus diisi. Tapi di model Anda nullable=False.
        # Jadi, field ini WAJIB diisi. Mari asumsikan ia diisi oleh set_password.
        # Untuk tes ini, mari kita asumsikan hashed_password belum di-set.
        # Namun, karena nullable=False, ini berarti User() tanpa set_password akan error saat flush ke DB.
        # Untuk unit test model, kita bisa tes set_password secara terpisah.
        # Sebaiknya User dibuat dengan hashed_password atau melalui set_password.

    @patch(f'{BCRYPT_PATH}.gensalt')
    @patch(f'{BCRYPT_PATH}.hashpw')
    def test_user_set_password_hashes_password(self, mock_bcrypt_hashpw, mock_bcrypt_gensalt):
        # Arrange
        user = User(username="testuser", email="test@example.com") # hashed_password belum diset
        plain_password = "SecurePassword123!"
        
        # Konfigurasi mock untuk bcrypt
        mock_salt = b'$2b$12$abcdefghijklmnopqrstuv' # Contoh salt bytes
        mock_hashed_bytes = b'$2b$12$abcdefghijklmnopqrstuv.examplehashedpassword' # Contoh hash bytes
        
        mock_bcrypt_gensalt.return_value = mock_salt
        mock_bcrypt_hashpw.return_value = mock_hashed_bytes

        # Act
        user.set_password(plain_password)

        # Assert
        mock_bcrypt_gensalt.assert_called_once_with()
        mock_bcrypt_hashpw.assert_called_once_with(plain_password.encode('utf-8'), mock_salt)
        assert user.hashed_password == mock_hashed_bytes.decode('utf-8')
        assert user.hashed_password != plain_password # Pastikan bukan plain text

    @patch(f'{BCRYPT_PATH}.checkpw')
    def test_user_check_password_correct(self, mock_bcrypt_checkpw):
        # Arrange
        user = User(username="checkuser", email="check@example.com")
        # Set manual hashed_password untuk tes ini, seolah-olah sudah disimpan
        user.hashed_password = "$2b$12$somevalidsaltandhashcombination" # Contoh hash yang valid
        plain_password = "CorrectPassword"

        mock_bcrypt_checkpw.return_value = True # Simulasikan password cocok

        # Act
        result = user.check_password(plain_password)

        # Assert
        mock_bcrypt_checkpw.assert_called_once_with(
            plain_password.encode('utf-8'),
            user.hashed_password.encode('utf-8')
        )
        assert result is True

    @patch(f'{BCRYPT_PATH}.checkpw')
    def test_user_check_password_incorrect(self, mock_bcrypt_checkpw):
        # Arrange
        user = User(username="checkuser", email="check@example.com")
        user.hashed_password = "$2b$12$somevalidsaltandhashcombination"
        incorrect_password = "WrongPassword"

        mock_bcrypt_checkpw.return_value = False # Simulasikan password tidak cocok

        # Act
        result = user.check_password(incorrect_password)

        # Assert
        mock_bcrypt_checkpw.assert_called_once_with(
            incorrect_password.encode('utf-8'),
            user.hashed_password.encode('utf-8')
        )
        assert result is False

    def test_user_check_password_when_no_hash_stored(self):
        # Arrange
        user = User(username="nohashuser", email="nohash@example.com")
        user.hashed_password = None # Tidak ada hash password yang tersimpan

        # Act
        result = user.check_password("any_password")

        # Assert
        assert result is False # Seharusnya False jika tidak ada hash

    def test_user_to_dict_without_request_and_no_photo(self):
        # Arrange
        user = User(
            id=1,
            username="dictuser",
            email="dict@example.com",
            bio="A simple bio.",
            profile_photo=None # Tidak ada foto profil
            # hashed_password tidak relevan untuk to_dict
        )

        # Act
        user_data = user.to_dict() # Panggil tanpa argumen request

        # Assert
        expected_data = {
            'id': 1,
            'username': "dictuser",
            'email': "dict@example.com",
            'bio': "A simple bio.",
            'profile_photo': None,
            'profile_url': None, # Karena tidak ada request dan tidak ada photo
        }
        assert user_data == expected_data
        assert 'hashed_password' not in user_data # Pastikan hash password tidak ada

    def test_user_to_dict_with_request_and_photo(self):
        # Arrange
        user = User(
            id=2,
            username="photouser",
            email="photo@example.com",
            bio="Loves photography.",
            profile_photo="profile_pics/photo.jpg" # Ada path foto profil
        )
        mock_request = MagicMock()
        mock_request.application_url = "http://localhost:6543" # Contoh URL aplikasi

        # Act
        user_data = user.to_dict(request=mock_request)

        # Assert
        expected_profile_url = "http://localhost:6543/static/profile_pics/photo.jpg"
        expected_data = {
            'id': 2,
            'username': "photouser",
            'email': "photo@example.com",
            'bio': "Loves photography.",
            'profile_photo': "profile_pics/photo.jpg",
            'profile_url': expected_profile_url,
        }
        assert user_data == expected_data
        assert 'hashed_password' not in user_data

    def test_user_to_dict_with_request_but_no_photo(self):
        # Arrange
        user = User(
            id=3,
            username="nophotouser",
            email="nophoto@example.com",
            bio="Prefers no photo.",
            profile_photo=None # Tidak ada path foto profil
        )
        mock_request = MagicMock()
        mock_request.application_url = "http://localhost:6543"

        # Act
        user_data = user.to_dict(request=mock_request)

        # Assert
        expected_data = {
            'id': 3,
            'username': "nophotouser",
            'email': "nophoto@example.com",
            'bio': "Prefers no photo.",
            'profile_photo': None,
            'profile_url': None, # Karena tidak ada profile_photo
        }
        assert user_data == expected_data