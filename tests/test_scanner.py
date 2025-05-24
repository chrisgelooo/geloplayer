import unittest
import os
import shutil
from library import scanner

class TestScanner(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory with dummy files for testing."""
        self.test_dir_base = "temp_test_music_dir_for_scanner"
        os.makedirs(self.test_dir_base, exist_ok=True)

        # Specific subdirectories for different tests
        self.empty_dir = os.path.join(self.test_dir_base, "empty_subdir")
        os.makedirs(self.empty_dir, exist_ok=True)

        self.no_mp3_dir = os.path.join(self.test_dir_base, "no_mp3_subdir")
        os.makedirs(self.no_mp3_dir, exist_ok=True)
        with open(os.path.join(self.no_mp3_dir, "notes.txt"), "w") as f:
            f.write("text")
        with open(os.path.join(self.no_mp3_dir, "image.jpg"), "w") as f:
            f.write("fake image data")

        self.mp3_dir = os.path.join(self.test_dir_base, "mp3_subdir")
        os.makedirs(self.mp3_dir, exist_ok=True)
        self.song1_path = os.path.join(self.mp3_dir, "song1.mp3")
        self.song2_path = os.path.join(self.mp3_dir, "prefix_song2.MP3") # Test case-insensitivity
        self.other_file_path = os.path.join(self.mp3_dir, "document.pdf")
        with open(self.song1_path, "w") as f:
            f.write("dummy mp3 data 1")
        with open(self.song2_path, "w") as f:
            f.write("dummy mp3 data 2")
        with open(self.other_file_path, "w") as f:
            f.write("dummy pdf data")
        
        # For testing non-recursive behavior
        self.nested_dir_parent = os.path.join(self.test_dir_base, "nested_parent")
        self.nested_dir_child = os.path.join(self.nested_dir_parent, "nested_child_with_mp3")
        os.makedirs(self.nested_dir_child, exist_ok=True)
        self.outer_mp3_path = os.path.join(self.nested_dir_parent, "outer_song.mp3")
        self.inner_mp3_path = os.path.join(self.nested_dir_child, "inner_song.mp3")
        with open(self.outer_mp3_path, "w") as f:
            f.write("outer dummy mp3")
        with open(self.inner_mp3_path, "w") as f:
            f.write("inner dummy mp3")


    def tearDown(self):
        """Remove the temporary directory after tests."""
        if os.path.exists(self.test_dir_base):
            shutil.rmtree(self.test_dir_base)

    def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        result = scanner.scan_directory(self.empty_dir)
        self.assertEqual(result, [])

    def test_scan_no_mp3_files(self):
        """Test scanning a directory with no MP3 files."""
        result = scanner.scan_directory(self.no_mp3_dir)
        self.assertEqual(result, [])

    def test_scan_with_mp3_files(self):
        """Test scanning a directory with MP3 files and other files."""
        result = scanner.scan_directory(self.mp3_dir)
        self.assertEqual(len(result), 2)
        # Convert to set for order-independent comparison
        self.assertSetEqual(set(result), {os.path.abspath(self.song1_path), os.path.abspath(self.song2_path)})

    def test_scan_non_existent_directory(self):
        """Test scanning a directory that does not exist."""
        non_existent_path = os.path.join(self.test_dir_base, "this_does_not_exist")
        result = scanner.scan_directory(non_existent_path)
        self.assertEqual(result, [])

    def test_scan_is_not_recursive(self):
        """Test that scanning is not recursive (as per current design)."""
        result = scanner.scan_directory(self.nested_dir_parent)
        self.assertEqual(len(result), 1)
        self.assertIn(os.path.abspath(self.outer_mp3_path), result)
        self.assertNotIn(os.path.abspath(self.inner_mp3_path), result)

    def test_file_instead_of_directory(self):
        """Test scanning a file path instead of a directory path."""
        # Create a dummy file to pass as a directory
        file_path = os.path.join(self.test_dir_base, "a_file.txt")
        with open(file_path, "w") as f:
            f.write("I am a file, not a directory.")
        result = scanner.scan_directory(file_path)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
