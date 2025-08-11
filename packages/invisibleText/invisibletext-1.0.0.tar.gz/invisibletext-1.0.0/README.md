# invisibleText

---

## Install

Installation is simple. It can be installed from pip using the following command:

`$ pip install invisibleText`

## Usage

invisibleText module can encode your text to invisible chars and turns back. Here is a simple example:

```
>>> import invisibleText
>>> invisibleText.encode("hello")
'\u200b\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u200b\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u200b\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u200b\u200c\u200c\u200c\u200c'
>>> invisibleText.decode('\u200b\u200c\u200c\u200b\u200c\u200b\u200b\u200b\u200b\u200c\u200c\u200b\u200b\u200c\u200b\u200c\u200b\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u200b\u200c\u200c\u200b\u200b\u200b\u200c\u200c\u200b\u200c\u200c\u200c\u200c')
'hello'
```