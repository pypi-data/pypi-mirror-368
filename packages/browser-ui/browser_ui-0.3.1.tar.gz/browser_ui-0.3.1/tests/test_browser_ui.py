import unittest
from unittest.mock import patch
from pathlib import Path
import os
import _import_package

from browser_ui import BrowserUI

class TestBrowserUI(unittest.TestCase):

    @patch('browser_ui.BrowserUI.get_caller_file_abs_path')
    def test_relative_static_dir(self, mock_get_caller):
        # Arrange
        # Simulate the caller file is /fake/path/to/caller.py
        fake_caller_path = os.path.abspath('/fake/path/to/caller.py')
        mock_get_caller.return_value = fake_caller_path
        
        # Act
        ui = BrowserUI(static_dir='static')
        
        # Assert
        expected_path = Path(fake_caller_path).parent.joinpath('static')
        self.assertEqual(ui._static_dir, expected_path)

    @patch('browser_ui.BrowserUI.get_caller_file_abs_path')
    def test_absolute_static_dir(self, mock_get_caller):
        # Arrange
        absolute_path_str = os.path.abspath('/absolute/path/to/static')

        # Act
        ui = BrowserUI(static_dir=absolute_path_str)
        
        # Assert
        self.assertEqual(ui._static_dir, Path(absolute_path_str))
        # Ensure get_caller_file_abs_path was not called
        mock_get_caller.assert_not_called()

if __name__ == '__main__':
    unittest.main()