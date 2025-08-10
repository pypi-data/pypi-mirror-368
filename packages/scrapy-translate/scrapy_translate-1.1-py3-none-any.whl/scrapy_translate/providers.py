from typing import Collection, Protocol


class CacheProvider(Protocol):
    async def get(self, strings: Collection[str], /) -> dict[str, str]: ...

    async def set(self, strings: dict[str, str], /) -> None: ...


class NullCacheProvider(CacheProvider):
    async def get(self, _: Collection[str]) -> dict[str, str]:
        return {}

    async def set(self, _: dict[str, str]) -> None:
        pass


class TranslationProvider(Protocol):
    async def translate(self, strings: Collection[str], /) -> dict[str, str]: ...


class IdentityTranslationProdiver(TranslationProvider):
    async def translate(self, strings: Collection[str]) -> dict[str, str]:
        return {string: string for string in strings}
