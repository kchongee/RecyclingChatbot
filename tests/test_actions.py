import json
import pytest

from rasa_sdk.executor import CollectingDispatcher, Tracker
from rasa_sdk.events import SlotSet, ActionExecuted, SessionStarted

from tests.conftest import EMPTY_TRACKER, PAY_CC_CONFIRMED, PAY_CC_NOT_CONFIRMED
from actions import actions

import unittest
import sqlite3

class Test(unittest.TestCase):
    def test_db(self):
        con = sqlite3.connect('database.db')
        self.assertIsNot(con, 0)
        curs = con.cursor()
        curs.execute("select * from item")
        record = curs.fetchall()
        self.assertGreater(len(record), 5)
        curs.close()

if __name__ == '__main__':
    unittest.main()
