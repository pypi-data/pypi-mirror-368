import unittest
from book import Book
import os


class Testbook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Book.filepath = "test_books.jsonl"

    def tearDown(self):
        if os.path.exists(Book.filepath):
            os.remove(Book.filepath)

    def test_save_and_read(self):
        book = Book("Test Book", "Test Author", "Test Publisher", 2023)
        book.save()
        read_book = Book.read(book.bid)
        self.assertIsNotNone(read_book)
        self.assertEqual(read_book.name, "Test Book")
        self.assertEqual(read_book.auther, "Test Author")
        self.assertEqual(read_book.publisher, "Test Publisher")
        self.assertEqual(read_book.year, 2023)
        self.assertEqual(read_book.bid, book.bid)

    def test_search(self):
        book = Book("Test Book", "Test Author", "Test Publisher", 2023)
        book.save()
        bookss = Book.search(name="Test Book")
        self.assertIsNotNone(bookss)
        self.assertEqual(len(bookss), 1)
        self.assertIsInstance(bookss, list)
        self.assertTrue(all(isinstance(b, Book) for b in bookss))
        self.assertTrue(all("Test Book" in b.name for b in bookss))

    # end def
