import unittest
import datetime
from pytz import timezone
from alerts_in_ua.alert import Alert
import pytz

class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.alert_data = {
            "id": 8757,
            "location_title": "Луганська область",
            "location_type": "oblast",
            "started_at": "2022-04-04T16:45:39.000Z",
            "finished_at": None,
            "updated_at": "2022-04-08T08:04:26.316Z",
            "alert_type": "air_raid",
            "location_oblast": "Луганська область",
            "location_uid": "16",
            "notes": None,
            "calculated": None
        }

    def test_alert_init(self):
        alert = Alert(self.alert_data)
        self.assertEqual(alert.id, 8757)
        self.assertEqual(alert.location_title, "Луганська область")
        self.assertEqual(str(alert.started_at), '2022-04-04 19:45:39+03:00')
        self.assertIsNone(alert.finished_at)

    def test_alert_is_finished(self):
        alert = Alert(self.alert_data)
        self.assertFalse(alert.is_finished())
        alert.finished_at = datetime.datetime.now(timezone('Europe/Kiev'))
        self.assertTrue(alert.is_finished())

    def test_alert_repr(self):
        alert = Alert(self.alert_data)
        expected_repr = "Alert({'id': 8757, 'location_title': 'Луганська область', 'location_type': 'oblast', 'started_at': datetime.datetime(2022, 4, 4, 19, 45, 39, tzinfo=<DstTzInfo 'Europe/Kyiv' EEST+3:00:00 DST>), 'finished_at': None, 'updated_at': datetime.datetime(2022, 4, 8, 11, 4, 26, 316000, tzinfo=<DstTzInfo 'Europe/Kyiv' EEST+3:00:00 DST>), 'alert_type': 'air_raid', 'location_uid': '16', 'location_oblast': 'Луганська область', 'location_raion': None, 'notes': None, 'calculated': None}"
        self.assertEqual(repr(alert), expected_repr)


if __name__ == '__main__':
    unittest.main()