from collections import UserString
from typing import Any, Iterator, TypedDict

from itemadapter.adapter import ItemAdapter
from itemadapter.utils import is_item
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.spiders import Spider
from scrapy.utils.misc import build_from_crawler, load_object

from scrapy_translate.processors import (
    extract_text_from_html,
    extract_text_from_list,
    inject_text_into_html,
    inject_text_into_list,
)
from scrapy_translate.providers import (
    CacheProvider,
    NullCacheProvider,
    TranslationProvider,
)


class TranslatedString(UserString):
    cache: bool

    def __init__(self, *args, cache: bool = False) -> None:
        super().__init__(*args)
        self.cache = cache


class TranslatedFieldMeta(TypedDict):
    html: bool
    cache: bool


class TranslatePipeline:
    _cache_provider: CacheProvider
    _translation_provider: TranslationProvider

    def __init__(
        self,
        *,
        cache_provider: CacheProvider,
        translation_provider: TranslationProvider,
    ):
        self._cache_provider = cache_provider
        self._translation_provider = translation_provider

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "TranslatePipeline":
        if crawler.settings.getbool("TRANSLATION_DISABLED"):
            raise NotConfigured

        if not (translation_provider := crawler.settings.get("TRANSLATION_PROVIDER")):
            raise NotConfigured("TRANSLATION_PROVIDER must be set")
        cache_provider = crawler.settings.setdefault(
            "TRANSLATION_CACHE_PROVIDER",
            NullCacheProvider,
        )

        return cls(
            cache_provider=build_from_crawler(load_object(cache_provider), crawler),
            translation_provider=build_from_crawler(
                load_object(translation_provider),
                crawler,
            ),
        )

    async def process_item(self, item: Any, spider: Spider) -> Any:
        if not is_item(item):
            return item

        item_adapter = ItemAdapter(item)
        translated_strings = self._get_translated_strings(item_adapter)
        translations = await self._translate(translated_strings)
        self._set_translated_strings(item_adapter, translations)
        return item_adapter.item

    def _translated_fields_meta(
        self,
        item_adapter: ItemAdapter,
    ) -> Iterator[tuple[str, TranslatedFieldMeta]]:
        for field_name in item_adapter.field_names():
            field_meta = item_adapter.get_field_meta(field_name)
            if field_meta.get("translate"):
                yield (
                    field_name,
                    TranslatedFieldMeta(
                        html=field_meta.get("translate_html", False),
                        cache=field_meta.get("translate_cache", False),
                    ),
                )

    def _get_translated_strings(
        self,
        item_adapter: ItemAdapter,
    ) -> list[TranslatedString]:
        translated_strings: list[TranslatedString] = []
        for field_name, field_meta in self._translated_fields_meta(item_adapter):
            if field_meta["html"]:
                strings = extract_text_from_html(item_adapter[field_name])
            elif isinstance(item_adapter[field_name], list):
                strings = extract_text_from_list(item_adapter[field_name])
            else:
                strings = [item_adapter[field_name]]

            translated_strings.extend(
                TranslatedString(string, cache=field_meta.get("cache", False))
                for string in strings
                if string
            )

        return translated_strings

    def _set_translated_strings(
        self,
        item_adapter: ItemAdapter,
        translations: dict[str, str],
    ) -> None:
        for field_name, field_meta in self._translated_fields_meta(item_adapter):
            if field_meta.get("html"):
                item_adapter[field_name] = inject_text_into_html(
                    item_adapter[field_name],
                    [
                        translations.get(string, string)
                        for string in extract_text_from_html(item_adapter[field_name])
                    ],
                )
            elif isinstance(item_adapter[field_name], list):
                item_adapter[field_name] = inject_text_into_list(
                    item_adapter[field_name],
                    [
                        translations.get(string, string)
                        for string in extract_text_from_list(item_adapter[field_name])
                    ],
                )
            else:
                item_adapter[field_name] = translations.get(
                    item_adapter[field_name], item_adapter[field_name]
                )

    async def _translate(self, strings: list[TranslatedString]) -> dict[str, str]:
        cached_translations: dict[str, str] = {}
        from_cache = set(s.data for s in strings if s.cache)
        if from_cache:
            cached_translations = await self._cache_provider.get(from_cache)

        translations: dict[str, str] = {}
        to_translate = set(s.data for s in strings if s.data not in cached_translations)
        if to_translate:
            translations = await self._translation_provider.translate(to_translate)
            to_cache = {
                k: v
                for k, v in translations.items()
                if k in from_cache and k not in cached_translations
            }
            if to_cache:
                await self._cache_provider.set(to_cache)

        translations.update(cached_translations)
        return translations
