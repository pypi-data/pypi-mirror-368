import unittest

from scrapy_translate.processors import (
    extract_text_from_html,
    extract_text_from_list,
    inject_text_into_html,
    inject_text_into_list,
)


class TestProcessors(unittest.TestCase):
    def test_html_processor(self):
        html = '<p>Hello, <strong>World!</strong><br><img src="img.png"></p>'
        result = inject_text_into_html(html, extract_text_from_html(html))
        self.assertEqual(html, result)

    def test_list_processor(self):
        checks = ([], ["foo"], ["foo", "bar"], [["foo", "bar"], "baz"])
        for value in checks:
            with self.subTest(value=value):
                result = inject_text_into_list(value, extract_text_from_list(value))
                self.assertEqual(value, result)
