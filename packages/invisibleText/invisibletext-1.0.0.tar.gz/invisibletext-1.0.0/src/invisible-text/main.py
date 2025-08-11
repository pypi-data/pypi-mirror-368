"""
Encode text to invisible chars
Decode invisible chars to text
"""

def encode(text) -> str:
    """Encode text to invisible chars"""
    bin_text = ''.join(format(ord(char),'08b') for char in text)
    bin_text = bin_text.replace('0', '​') # Here is U+200B
    bin_text = bin_text.replace('1', '‌') # Here is U+200C
    return bin_text

def decode(bin_text):
    """Decode invisible chars to text"""
    bin_text = bin_text.replace('​', '0') # Here is U+200B
    bin_text = bin_text.replace('‌', '1') # Here is U+200C
    text = ''.join(chr(int(bin_text[i:i+8],2)) for i in range(0,len(bin_text),8))
    return text
