import unittest
import tempfile
import pathlib
import shutil
import sys
import re

from main import (
    get_all_files,
    select_diverse_files,
)


# mock the exit function to test sys.exit calls
class MockExit(Exception):
    def __init__(self, code):
        self.code = code


def mock_sys_exit(code):
    raise MockExit(code)


class TestBookSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a temporary directory structure ONCE for all tests
        cls.test_dir = pathlib.Path(tempfile.mkdtemp())
        print(f"created test dir: {cls.test_dir}")
        (cls.test_dir / "CollectionA").mkdir()
        (cls.test_dir / "CollectionB").mkdir()
        (cls.test_dir / "CollectionC_empty").mkdir()
        (cls.test_dir / ".hidden_folder").mkdir()

        # files
        (cls.test_dir / "root_book1.txt").write_text("content1")
        (cls.test_dir / "root_book2.epub").write_text("content2")
        (cls.test_dir / ".hidden_file.txt").write_text("hidden")

        (cls.test_dir / "CollectionA" / "a_book1.pdf").write_text("contentA1")
        (cls.test_dir / "CollectionA" / "a_book2.mobi").write_text("contentA2")
        (cls.test_dir / "CollectionA" / ".a_hidden.txt").write_text("hiddenA")

        (cls.test_dir / "CollectionB" / "b_book1.azw3").write_text("contentB1")
        (cls.test_dir / "CollectionB" / "SubfolderB").mkdir()
        (cls.test_dir / "CollectionB" / "SubfolderB" / "sub_b_book.txt").write_text(
            "contentBsub"
        )

        # store expected non-hidden files and their top-level origins
        cls.expected_files = {
            cls.test_dir / "root_book1.txt": cls.test_dir / "root_book1.txt",
            cls.test_dir / "root_book2.epub": cls.test_dir / "root_book2.epub",
            cls.test_dir / "CollectionA" / "a_book1.pdf": cls.test_dir / "CollectionA",
            cls.test_dir / "CollectionA" / "a_book2.mobi": cls.test_dir / "CollectionA",
            cls.test_dir / "CollectionB" / "b_book1.azw3": cls.test_dir / "CollectionB",
            cls.test_dir / "CollectionB" / "SubfolderB" / "sub_b_book.txt": cls.test_dir
            / "CollectionB",
        }
        cls.expected_top_level_items = {
            cls.test_dir / "root_book1.txt",
            cls.test_dir / "root_book2.epub",
            cls.test_dir / "CollectionA",
            cls.test_dir / "CollectionB",
            # CollectionC_empty is technically top-level but will have no files
        }
        cls.expected_eligible_origins = {  # items expected to contain non-hidden files
            cls.test_dir / "root_book1.txt",
            cls.test_dir / "root_book2.epub",
            cls.test_dir / "CollectionA",
            cls.test_dir / "CollectionB",
        }

        # patch sys.exit for testing exit conditions
        cls.original_exit = sys.exit
        sys.exit = mock_sys_exit

    @classmethod
    def tearDownClass(cls):
        # clean up the temporary directory ONCE after all tests
        print(f"removing test dir: {cls.test_dir}")
        shutil.rmtree(cls.test_dir)
        # restore original sys.exit
        sys.exit = cls.original_exit

    def test_get_all_files_no_pattern(self):
        """verify get_all_files finds all non-hidden files."""
        files = get_all_files(self.test_dir)
        self.assertCountEqual(files, list(self.expected_files.keys()))

    def test_get_all_files_with_pattern(self):
        """verify get_all_files filters correctly."""
        pattern = re.compile(r"\.txt$", re.IGNORECASE)
        files = get_all_files(self.test_dir, pattern)
        expected_txt = [
            self.test_dir / "root_book1.txt",
            self.test_dir / "CollectionB" / "SubfolderB" / "sub_b_book.txt",
        ]
        self.assertCountEqual(files, expected_txt)

    def test_basic_selection_no_pattern(self):
        """test selecting 3 files, should get 3 from distinct origins."""
        n_select = 3
        # --- Mock random.sample and random.choice if needed for deterministic tests ---
        # For now, just check properties
        selected = select_diverse_files(self.test_dir, n_select, "")

        self.assertEqual(len(selected), n_select)

        # check that selected files are from our expected list
        self.assertTrue(all(f in self.expected_files for f in selected))

        # check they come from distinct top-level origins
        origins = set()
        for f in selected:
            origins.add(self.expected_files[f])  # use precomputed origin map

        self.assertEqual(len(origins), n_select)
        self.assertTrue(origins.issubset(self.expected_eligible_origins))

    def test_selection_with_pattern(self):
        """test selection with a pattern yielding fewer origins."""
        n_select = 2
        pattern_str = r"\.txt$"  # matches root_book1.txt and sub_b_book.txt
        selected = select_diverse_files(self.test_dir, n_select, pattern_str)

        expected_origins = {
            self.test_dir / "root_book1.txt",
            self.test_dir / "CollectionB",
        }
        self.assertEqual(len(selected), n_select)  # request 2, 2 origins available
        self.assertTrue(all(f.name.endswith(".txt") for f in selected))

        origins = set(self.expected_files[f] for f in selected)
        self.assertEqual(origins, expected_origins)

    def test_requesting_more_than_available_origins(self):
        """test requesting 5 files when only 4 origins have files."""
        n_select = 5
        selected = select_diverse_files(self.test_dir, n_select, "")

        # should only select 4 files, one from each eligible origin
        self.assertEqual(len(selected), len(self.expected_eligible_origins))

        origins = set(self.expected_files[f] for f in selected)
        self.assertEqual(origins, self.expected_eligible_origins)

    def test_pattern_matches_nothing(self):
        """test pattern that results in no candidate files."""
        with self.assertRaises(MockExit) as cm:
            select_diverse_files(self.test_dir, 3, "PATTERN_THAT_MATCHES_NOTHING_XYZ")
        # check exit code or message if desired
        # print(cm.exception.code) # for debugging if needed

    def test_invalid_regex_pattern(self):
        """test providing an invalid regex pattern."""
        with self.assertRaises(MockExit) as cm:
            select_diverse_files(self.test_dir, 3, "*invalid_regex[")
        # check exit code or message


if __name__ == "__main__":
    unittest.main()
