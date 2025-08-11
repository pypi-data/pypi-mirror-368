import pytest
from markdown_normalization import (
    extract_codeblocks,
    omit_codeblocks,
    strip_markdown_formatting,
    omit_urls,
    normalize_markdown,
    extract_urls,
)

def test_extract_codeblocks():
    md = """Here is a code block:
```python
print("Hello, world!")
```
And another:
```js
console.log("Hello");
```
"""
    result = extract_codeblocks(md)
    assert result.strip() == 'print("Hello, world!")\nconsole.log("Hello");'

def test_omit_codeblocks():
    md = """This is before.
```python
print("Hello")
```
And after."""
    result = omit_codeblocks(md)
    assert "[code omitted]" in result
    assert "print" not in result

def test_strip_markdown_formatting():
    md = "This is *italic* and **bold** and `inline`.\n# Heading"
    result = strip_markdown_formatting(md)
    assert "italic" in result
    assert "bold" in result
    assert "`" in result
    assert "*" not in result
    assert "#" not in result

def test_omit_urls():
    md = "Here is a link: [example](https://example.com) and https://google.com and www.foo.com"
    result = omit_urls(md)
    assert "[url omitted]" in result
    assert "https://example.com" not in result
    assert "www.foo.com" not in result

def test_normalize_markdown():
    md = """
Here is *formatted* markdown with a link: [text](http://link.com)

```python
print("code")
```

and a raw url: https://site.org
"""
    result = normalize_markdown(md)
    assert "[url omitted]" in result
    assert "[code omitted]" in result
    assert "*" not in result
    assert "http" not in result
    assert "print" not in result


def test_extract_urls():
    md = """Here is a link: [example](https://example.com) and https://google.com and www.foo.com"""
    result = extract_urls(md)
    assert "https://example.com" in result
    assert "http://www.foo.com" in result
    assert "https://google.com" in result
    assert len(result) == 3
