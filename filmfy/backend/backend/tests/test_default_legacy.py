# Di filmfy/backend/backend/tests/test_default_legacy.py

import unittest
import transaction
from pyramid import testing

# Impor helper database dari lokasi yang benar
# Asumsi package utama Anda adalah 'backend' (merujuk ke folder filmfy/backend/backend/)
# dan fungsi-fungsi ini ada di dalam backend.models (misalnya, di backend/models/__init__.py)
from backend.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)

# Impor model dan view dari lokasi yang benar
from backend.models.meta import Base # Untuk init_database dan tearDown
# from backend.models.mymodel import MyModel # Jika MyModel digunakan, pastikan path ini benar
# from backend.views.default import my_view # Jika my_view digunakan

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        # Path ini sudah benar dari diskusi sebelumnya
        self.config.include('backend.models') 
        settings = self.config.get_settings()

        # Fungsi-fungsi sudah diimpor di atas dengan path absolut
        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)
        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        # Base sudah diimpor di atas
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        # Base sudah diimpor di atas
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

class TestMyViewSuccessCondition(BaseTest):
    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        # Impor MyModel dari lokasi yang benar
        # Asumsi MyModel ada di backend/models/mymodel.py
        from backend.models.mymodel import MyModel 
        # Jika MyModel di-ekspos di backend/models/__init__.py, maka:
        # from backend.models import MyModel

        model = MyModel(name='one', value=55)
        self.session.add(model)

    def test_passing_view(self):
        # Impor my_view dari lokasi yang benar
        # Asumsi my_view ada di backend/views/default.py
        from backend.views.default import my_view 
        info = my_view(dummy_request(self.session))
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'backend')

class TestMyViewFailureCondition(BaseTest):
    def test_failing_view(self):
        # Impor my_view dari lokasi yang benar
        from backend.views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info.status_int, 500)