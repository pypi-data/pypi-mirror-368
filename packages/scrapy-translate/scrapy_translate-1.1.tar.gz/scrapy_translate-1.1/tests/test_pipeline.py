import unittest
from unittest import mock

from itemadapter.adapter import ItemAdapter
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.item import Field, Item
from scrapy.settings import Settings
from scrapy.spiders import Spider

from scrapy_translate.pipeline import (
    TranslatedFieldMeta,
    TranslatedString,
    TranslatePipeline,
)
from scrapy_translate.providers import (
    CacheProvider,
    IdentityTranslationProdiver,
    NullCacheProvider,
    TranslationProvider,
)


class TestTranslatePipeline(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.cache_mock = mock.create_autospec(CacheProvider, instance=True)
        self.translation_mock = mock.create_autospec(TranslationProvider, instance=True)

    def test_from_crawler(self):
        crawler_mock = mock.create_autospec(Crawler, instance=True)
        translation_provider = "scrapy_translate.providers.IdentityTranslationProdiver"
        type(crawler_mock).settings = mock.PropertyMock(
            return_value=Settings({"TRANSLATION_PROVIDER": translation_provider})
        )

        instance = TranslatePipeline.from_crawler(crawler_mock)

        self.assertIsInstance(instance, TranslatePipeline)
        self.assertIsInstance(instance._cache_provider, NullCacheProvider)
        self.assertIsInstance(
            instance._translation_provider,
            IdentityTranslationProdiver,
        )

    def test_from_crawler__translation_disabled__raise_not_configured(self):
        crawler_mock = mock.create_autospec(Crawler, instance=True)
        type(crawler_mock).settings = mock.PropertyMock(
            return_value=Settings({"TRANSLATION_DISABLED": True})
        )

        with self.assertRaises(NotConfigured):
            TranslatePipeline.from_crawler(crawler_mock)

    def test_from_crawler__provider_not_set__raise_not_configured(self):
        crawler_mock = mock.create_autospec(Crawler, instance=True)
        type(crawler_mock).settings = mock.PropertyMock()

        with self.assertRaises(NotConfigured):
            TranslatePipeline.from_crawler(crawler_mock)

    async def test_process_item(self):
        class TestItem(Item):
            field1 = Field(translate=True)
            field2 = Field(translate=True, translate_cache=True)
            field3 = Field(translate=True, translate_html=True, translate_cache=True)

        spider_mock = mock.create_autospec(Spider, instance=True)
        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )
        self.cache_mock.get.return_value = {
            "dolor": "rolod",
            "consectetur": "rutetcesnoc",
        }
        self.translation_mock.translate.return_value = {
            "lorem": "merol",
            "ipsum": "muspi",
        }

        item = TestItem(
            field1="lorem",
            field2=["ipsum", "dolor"],
            field3="<p>sit amet, <strong>consectetur</strong></p>",
        )
        expected = TestItem(
            field1="merol",
            field2=["muspi", "rolod"],
            field3="<p>sit amet, <strong>rutetcesnoc</strong></p>",
        )

        actual = await pipeline.process_item(item, spider_mock)

        self.assertEqual(actual, expected)

    async def test_process_item__skip_not_items(self):
        spider_mock = mock.create_autospec(Spider, instance=True)
        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )

        actual = await pipeline.process_item(..., spider_mock)

        self.assertIs(actual, ...)

    def test_translated_fields_meta(self):
        class TestItem(Item):
            field1 = Field()
            field2 = Field(translate=False)
            field3 = Field(translate=True)
            field4 = Field(translate=True, translate_html=True)
            field5 = Field(translate=True, translate_cache=True)
            field6 = Field(
                translate=False,
                translate_html=True,
                translate_cache=True,
            )

        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )

        item = TestItem()
        expected = [
            ("field3", TranslatedFieldMeta(html=False, cache=False)),
            ("field4", TranslatedFieldMeta(html=True, cache=False)),
            ("field5", TranslatedFieldMeta(html=False, cache=True)),
        ]

        actual = list(pipeline._translated_fields_meta(ItemAdapter(item)))

        self.assertEqual(actual, expected)

    def test_get_translated_strings(self):
        checks = (
            (Field(), "foobar", []),
            (Field(translate=True), "", []),
            (Field(translate=True), "foobar", ["foobar"]),
            (Field(translate=True), ["foo", "bar"], ["foo", "bar"]),
            (
                Field(translate=True, translate_html=True),
                "<p>foo<i>bar</i></p>",
                ["foo", "bar"],
            ),
        )
        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )

        for field, value, expected in checks:
            with self.subTest(field=field, value=value):
                TestItem = type("TestItem", (Item,), {"field": field})
                item = TestItem(field=value)

                actual = pipeline._get_translated_strings(ItemAdapter(item))

                self.assertEqual(actual, expected)

    def test_get_translated_strings__set_string_meta(self):
        class TestItem(Item):
            field1 = Field(translate=True)
            field2 = Field(translate=True, translate_cache=True)

        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )

        item = TestItem(field1="foobar", field2=["foo", "bar"])

        strings = pipeline._get_translated_strings(ItemAdapter(item))

        self.assertEqual(strings, ["foobar", "foo", "bar"])
        cache_meta = [string.cache for string in strings]
        self.assertEqual(cache_meta, [False, True, True])

    def test_set_translated_strings(self):
        checks = (
            (Field(), "foo", "foo"),
            (Field(translate=True), "foo", "bar"),
            (Field(translate=True), ["foo", "baz"], ["bar", "qux"]),
            (
                Field(translate=True, translate_html=True),
                "<p>foo<i>baz</i></p>",
                "<p>bar<i>qux</i></p>",
            ),
        )

        translations = {"foo": "bar", "baz": "qux"}

        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )

        for field, value, expected in checks:
            with self.subTest(field=field, value=value):
                TestItem = type("TestItem", (Item,), {"field": field})
                item = TestItem(field=value)

                pipeline._set_translated_strings(
                    ItemAdapter(item),
                    translations,
                )

                self.assertEqual(item["field"], expected)

    def test_set_translated_strings__fallback_to_original(self):
        checks = (
            (Field(translate=True), "foo"),
            (Field(translate=True), ["foo", "baz"]),
            (Field(translate=True, translate_html=True), "<p>foo<i>baz</i></p>"),
        )

        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )

        for field, value in checks:
            with self.subTest(field=field, value=value):
                TestItem = type("TestItem", (Item,), {"field": field})
                item = TestItem(field=value)

                pipeline._set_translated_strings(ItemAdapter(item), {})

                self.assertEqual(item["field"], item["field"])

    async def test_translate(self):
        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )
        self.cache_mock.get.return_value = {}
        self.translation_mock.translate.return_value = {"lorem": "merol"}

        strings = [TranslatedString("lorem")]
        expected = {"lorem": "merol"}

        actual = await pipeline._translate(strings)

        self.assertEqual(actual, expected)
        self.translation_mock.translate.assert_called_once_with({"lorem"})

    async def test_translate__get_from_cache(self):
        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )
        self.cache_mock.get.return_value = {"lorem": "merol"}
        self.translation_mock.translate.return_value = {}

        strings = [TranslatedString("lorem", cache=True)]
        expected = {"lorem": "merol"}

        actual = await pipeline._translate(strings)

        self.assertEqual(actual, expected)
        self.cache_mock.get.assert_called_once_with({"lorem"})
        self.translation_mock.translate.assert_not_called()
        self.cache_mock.set.assert_not_called()

    async def test_translate__set_cache(self):
        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )
        self.cache_mock.get.return_value = {}
        self.translation_mock.translate.return_value = {"lorem": "merol"}

        strings = [TranslatedString("lorem", cache=True)]
        expected = {"lorem": "merol"}

        actual = await pipeline._translate(strings)

        self.assertEqual(actual, expected)
        self.cache_mock.set.assert_called_once_with({"lorem": "merol"})

    async def test_translate__skip_cache(self):
        pipeline = TranslatePipeline(
            cache_provider=self.cache_mock,
            translation_provider=self.translation_mock,
        )
        self.cache_mock.get.return_value = {}
        self.translation_mock.translate.return_value = {"lorem": "merol"}

        strings = [TranslatedString("lorem")]
        expected = {"lorem": "merol"}

        actual = await pipeline._translate(strings)

        self.assertEqual(actual, expected)
        self.cache_mock.get.assert_not_called()
        self.translation_mock.translate.assert_called_once_with({"lorem"})
        self.cache_mock.set.assert_not_called()
