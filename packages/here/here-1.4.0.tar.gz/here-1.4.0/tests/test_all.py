import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.here import get_file_working_directory, here


class TestHereFunctions(unittest.TestCase):
    @patch("src.here.get_ipython")
    def test_get_file_working_directory_jupyter(self, mock_get_ipython):
        mock_get_ipython.return_value = MagicMock(config=True)
        expected = Path.cwd()
        self.assertEqual(get_file_working_directory(), expected)

    @patch("src.here.__file__", "dummy_path")
    def test_get_file_working_directory_script(self):
        expected = Path(__file__).resolve().parent.parent
        self.assertEqual(get_file_working_directory(), expected)

    @patch("src.here.__file__", new_callable=lambda: NameError)
    def test_get_file_working_directory_interactive(self, mock_name_error):
        expected = Path.cwd()
        self.assertEqual(get_file_working_directory(), expected)

    def test_here_resolve_relative_path(self):
        with patch(
            "src.here.get_file_working_directory",
            return_value=Path("/Users/username/my_workspace"),
        ):
            expected = Path("/Users/username/my_workspace/data/output")
            self.assertEqual(here("data/output"), expected)

    def test_here_resolve_parent_path(self):
        with patch(
            "src.here.get_file_working_directory",
            return_value=Path("/Users/username/my_workspace"),
        ):
            expected = Path("/Users/username/config")
            self.assertEqual(here("../config"), expected)

    def test_here_resolve_empty_path(self):
        with patch(
            "src.here.get_file_working_directory",
            return_value=Path("/Users/username/my_workspace"),
        ):
            expected = Path("/Users/username/my_workspace")
            self.assertEqual(here(""), expected)


if __name__ == "__main__":
    unittest.main()
