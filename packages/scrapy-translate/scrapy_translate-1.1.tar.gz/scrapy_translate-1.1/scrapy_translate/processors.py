import io
from html.parser import HTMLParser
from typing import Iterator, Optional


class HTMLTextExtractor(HTMLParser):
    _buffer: list[str]

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

    def set_buffer(self, new_buffer: list[str]) -> None:
        self._buffer = new_buffer

    def handle_data(self, data: str) -> None:
        self._buffer.append(data)


class HTMLTextInjector(HTMLParser):
    _buffer: io.StringIO
    _text: Iterator[str]

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

    def set_buffer(self, new_buffer: io.StringIO) -> None:
        self._buffer = new_buffer

    def set_text(self, text: list[str]) -> None:
        self._text = iter(text)

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, Optional[str]]],
    ) -> None:
        self._buffer.write(self.get_starttag_text() or "")

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, Optional[str]]],
    ) -> None:
        self._buffer.write(self.get_starttag_text() or "")

    def handle_data(self, data: str) -> None:
        self._buffer.write(next(self._text))

    def handle_endtag(self, tag: str) -> None:
        self._buffer.write(f"</{tag}>")


def extract_text_from_html(html: str) -> list[str]:
    text = []
    extractor = HTMLTextExtractor()
    extractor.set_buffer(text)
    extractor.feed(html)
    return text


def inject_text_into_html(html: str, text: list[str]) -> str:
    buffer = io.StringIO()
    injector = HTMLTextInjector()
    injector.set_buffer(buffer)
    injector.set_text(text)
    injector.feed(html)
    return buffer.getvalue()


def extract_text_from_list(it: list) -> list[str]:
    def walk(it):
        for el in it:
            if isinstance(el, str):
                yield el
            else:
                yield from walk(el)

    return list(walk(it))


def inject_text_into_list(it: list, text: list[str]) -> list:
    def walk(it, text):
        for el in it:
            if isinstance(el, str):
                yield next(text)
            else:
                yield list(walk(el, text))

    return list(walk(it, iter(text)))
