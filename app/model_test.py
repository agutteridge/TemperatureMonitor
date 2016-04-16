import unittest
from unittest import TestCase
import model
import datetime
from datetime import timedelta

current_time = datetime.datetime.now()


class Test(TestCase):

    def setUp(self):
        self.test_db = model.init_db('test_db')

    def test_store_temp(self):
        model.store_temp(self.test_db, [22.2, current_time])
        c = self.test_db.cursor()
        c.execute('''SELECT * FROM Readings as "DateAndTime [TIMESTAMP]"''')
        self.test_db.commit()
        result = c.fetchone()
        assert(result == (22.2, current_time))

    def test_fetch_24hrs(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        result = model.fetch_24hrs(self.test_db)
        for r in result:
            assert(result == [(22.2, current_time)])

    def test_fetch_24hrs_empty(self):
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        result = model.fetch_24hrs(self.test_db)
        assert(result == [])

    def tearDown(self):
        c = self.test_db.cursor()
        c.execute('''DROP TABLE IF EXISTS Readings''')
        self.test_db.commit()
        self.test_db.close()


if __name__ == '__main__':
    unittest.main()
