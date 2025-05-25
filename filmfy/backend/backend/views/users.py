import os
import uuid
import shutil
import sqlalchemy.exc
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPOk, HTTPCreated, HTTPNotFound, HTTPBadRequest,
    HTTPConflict, HTTPUnauthorized, HTTPNoContent
)
from ..models.user import User

# --- Konfigurasi Direktori Upload Foto Profil ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Asumsi views/ ada di backend/backend/
BACKEND_BACKEND_DIR = os.path.dirname(CURRENT_DIR) 
PROFILE_PIC_UPLOAD_DIR = os.path.join(BACKEND_BACKEND_DIR, 'static', 'profile_pics')
os.makedirs(PROFILE_PIC_UPLOAD_DIR, exist_ok=True)

def _save_profile_photo(photo_file_storage):
    """Helper function untuk menyimpan foto profil."""
    if (photo_file_storage is not None and 
        hasattr(photo_file_storage, 'filename') and 
        photo_file_storage.filename):
        _, ext = os.path.splitext(photo_file_storage.filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        output_path = os.path.join(PROFILE_PIC_UPLOAD_DIR, unique_filename)
        photo_file_storage.file.seek(0)
        with open(output_path, 'wb') as output_f:
            shutil.copyfileobj(photo_file_storage.file, output_f)
        return 'profile_pics/' + unique_filename # Simpan path relatif
    return None

def _delete_profile_photo(photo_path):
    """Helper function untuk menghapus foto profil."""
    if photo_path:
        actual_filename = photo_path.replace('profile_pics/', '', 1)
        full_path = os.path.join(PROFILE_PIC_UPLOAD_DIR, actual_filename)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except OSError as e:
                print(f"Error deleting profile photo {full_path}: {e}")
                return False
    return False

@view_defaults(renderer='json')
class UserViews:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession

    # --- SIGNUP (Diperbarui untuk FormData) ---
    @view_config(route_name='api_signup', request_method='POST')
    def signup_view(self):
        try:
            # Ambil data dari FormData
            username = self.request.POST.get('username')
            email = self.request.POST.get('email')
            password = self.request.POST.get('password')
            confirm_password = self.request.POST.get('confirm_password')
            bio = self.request.POST.get('bio', None) # Bio opsional
            foto_profil = self.request.POST.get('foto_profil') # Nama field dari frontend

            # Validasi input
            if not all([username, email, password, confirm_password]):
                return HTTPBadRequest(json_body={'error': 'Username, email, password, and confirm password are required.'})

            if password != confirm_password:
                return HTTPBadRequest(json_body={'error': 'Passwords do not match.'})

            # Simpan foto profil jika ada
            profile_photo_path = _save_profile_photo(foto_profil)

            # Buat instance user baru
            new_user = User(
                username=username, 
                email=email, 
                bio=bio, 
                profile_photo=profile_photo_path
            )
            new_user.set_password(password)

            self.dbsession.add(new_user)
            self.dbsession.flush()

            return HTTPCreated(json_body={
                'message': 'User created successfully!',
                'user': new_user.to_dict(request=self.request)
            })

        except sqlalchemy.exc.IntegrityError:
            self.dbsession.rollback()
            return HTTPConflict(json_body={'error': 'Username or email already exists.'})
        
        except Exception as e:
            self.dbsession.rollback()
            print(f"Error during signup: {e}")
            import traceback
            traceback.print_exc()
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})

    # --- LOGIN (Tetap sama) ---
    @view_config(route_name='api_login', request_method='POST')
    def login_view(self):
        # ... (Kode login Anda dari sebelumnya, sudah benar) ...
        try:
            json_data = self.request.json_body
            email = json_data.get('email') # Asumsi login pakai email
            password = json_data.get('password')

            if not all([email, password]):
                return HTTPBadRequest(json_body={'error': 'Email and password are required.'})

            user = self.dbsession.query(User).filter_by(email=email).first()

            if not user or not user.check_password(password):
                return HTTPUnauthorized(json_body={'error': 'Invalid email or password.'})
            
            return HTTPOk(json_body={
                'message': 'Login successful!',
                'user': user.to_dict(request=self.request)
            })
        except Exception as e:
            print(f"Error during login: {e}")
            import traceback
            traceback.print_exc()
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})


    # --- GET PROFILE (Tetap sama) ---
    @view_config(route_name='api_user_profile', request_method='GET')
    def get_profile_view(self):
        # ... (Kode get profile Anda dari sebelumnya, sudah benar) ...
        try:
            user_id = int(self.request.matchdict['id'])
            user = self.dbsession.query(User).get(user_id)

            if not user:
                return HTTPNotFound(json_body={'error': 'User not found'})

            return HTTPOk(json_body=user.to_dict(request=self.request))
        except ValueError:
            return HTTPBadRequest(json_body={'error': 'Invalid user ID format'})
        except Exception as e:
            print(f"Error getting profile: {e}")
            import traceback
            traceback.print_exc()
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})

    # --- UPDATE PROFILE ---
    @view_config(route_name='api_user_update', request_method='POST') # Pakai POST untuk FormData
    def update_profile_view(self):
        # !!! PERINGATAN KERAS: KODE INI BELUM AMAN !!!
        # !!! IA TIDAK MEMERIKSA APAKAH USER YANG LOGIN BOLEH MENGEDIT PROFIL INI !!!
        # !!! ANDA HARUS MENAMBAHKAN LOGIKA OTORISASI NANTI !!!
        try:
            user_id = int(self.request.matchdict['id'])
            user = self.dbsession.query(User).get(user_id)

            if not user:
                return HTTPNotFound(json_body={'error': 'User not found'})
            
            # --- Cek Otorisasi (Contoh Sederhana - HARUS DIPERBAIKI NANTI) ---
            # logged_in_user_id = ... # Anda perlu cara mendapatkan ID user yang login (dari sesi/token)
            # if logged_in_user_id != user_id:
            #     return HTTPForbidden(json_body={'error': 'You are not authorized to edit this profile.'})
            # -------------------------------------------------------------------

            # Update fields jika ada di FormData
            user.username = self.request.POST.get('username', user.username)
            user.email = self.request.POST.get('email', user.email)
            user.bio = self.request.POST.get('bio', user.bio)

            # Handle update foto profil
            foto_profil = self.request.POST.get('foto_profil')
            if (foto_profil is not None and 
                hasattr(foto_profil, 'filename') and 
                foto_profil.filename):
                if user.profile_photo:
                    _delete_profile_photo(user.profile_photo)
                user.profile_photo = _save_profile_photo(foto_profil)

            # Cek unique constraint lagi (opsional, bisa lebih kompleks)
            self.dbsession.flush() 

            return HTTPOk(json_body={
                'message': 'Profile updated successfully!',
                'user': user.to_dict(request=self.request)
            })
        except sqlalchemy.exc.IntegrityError:
             self.dbsession.rollback()
             return HTTPConflict(json_body={'error': 'Username or email might already exist.'})
        except Exception as e:
            self.dbsession.rollback()
            print(f"Error updating profile: {e}")
            import traceback
            traceback.print_exc()
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})

    # --- DELETE USER ---
    @view_config(route_name='api_user_delete', request_method='DELETE')
    def delete_user_view(self):
        # !!! PERINGATAN KERAS: KODE INI BELUM AMAN !!!
        # !!! IA TIDAK MEMERIKSA APAKAH USER YANG LOGIN BOLEH MENGHAPUS AKUN INI !!!
        # !!! ANDA HARUS MENAMBAHKAN LOGIKA OTORISASI NANTI !!!
        try:
            user_id = int(self.request.matchdict['id'])
            user = self.dbsession.query(User).get(user_id)

            if not user:
                return HTTPNotFound(json_body={'error': 'User not found'})

            # --- Cek Otorisasi (Contoh Sederhana - HARUS DIPERBAIKI NANTI) ---
            # logged_in_user_id = ... 
            # if logged_in_user_id != user_id:
            #     return HTTPForbidden(json_body={'error': 'You are not authorized to delete this profile.'})
            # -------------------------------------------------------------------

            # Hapus foto profil jika ada
            if user.profile_photo:
                _delete_profile_photo(user.profile_photo)

            self.dbsession.delete(user)
            self.dbsession.flush()
            
            return HTTPNoContent() 
        except Exception as e:
            self.dbsession.rollback()
            print(f"Error deleting user: {e}")
            import traceback
            traceback.print_exc()
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})