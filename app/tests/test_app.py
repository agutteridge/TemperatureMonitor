import app
from app import view
import tempfile
import os
import unittest


class AppTest(unittest.TestCase):

    def setUp(self):
        None
    #     self.db_fd, view.app.config['DATABASE'] = tempfile.mkstemp()
    #     view.app.config['TESTING'] = True
    #     self.app = view.app.test_client()
    #     with view.app.app_context():
    #         app.init_db()

    # def test_empty_db(self):
    #     rv = self.app.get('/')
    #     assert b'No entries here so far' in rv.data

    # def tearDown(self):
    #     os.close(self.db_fd)
    #     os.unlink(view.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
