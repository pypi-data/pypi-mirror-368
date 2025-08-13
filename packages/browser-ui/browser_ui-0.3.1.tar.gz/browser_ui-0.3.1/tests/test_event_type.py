import unittest
import _import_package
from browser_ui import EventType

class TestEventType(unittest.TestCase):
    def test_from_str_valid(self):
        """
        Tests that from_str returns the correct enum member for a valid event name.
        """
        self.assertEqual(EventType.from_str("page_closed"), EventType.page_closed)

    def test_from_str_invalid(self):
        """
        Tests that from_str raises a ValueError for an invalid event name.
        """
        with self.assertRaises(ValueError):
            EventType.from_str("invalid_event")

if __name__ == '__main__':
    unittest.main()
