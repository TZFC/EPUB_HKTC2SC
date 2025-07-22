from google.colab import files
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from opencc import OpenCC

# Upload EPUB file
print("Please upload an EPUB file...")
uploaded = files.upload()
if not uploaded:
    raise ValueError("No file uploaded.")

input_filename = next(iter(uploaded))
output_filename = os.path.splitext(input_filename)[0] + "_simplified.epub"

# Conversion setup
converter = OpenCC('hk2s')
punctuation_map = {
    '「': '“', '」': '”', '『': '‘', '』': '’',
    '﹁': '“', '﹂': '”', '﹃': '“', '﹄': '”',
    '︵': '（', '︶': '）', '︷': '{', '︸': '}',
    '︹': '〔', '︺': '〕', '︻': '【', '︼': '】',
    '︽': '《', '︾': '》', '︿': '〈', '﹀': '〉',
    '、': '，', '。': '。', '．': '。', '‧': '·',
    '～': '〜', '—': '——', '─': '—', '━': '—',
    '－': '-', '﹣': '-', '﹏': '_',
}

def convert_punctuation(text):
    for k, v in punctuation_map.items():
        text = text.replace(k, v)
    return text

# Load and modify EPUB
book = epub.read_epub(input_filename)

for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        for tag in soup.find_all(string=True):
            simplified = converter.convert(tag)
            tag.replace_with(convert_punctuation(simplified))
        body = soup.body
        content = body.decode_contents(formatter="html")
        xhtml = f'''<html xmlns="http://www.w3.org/1999/xhtml">
          <head>
            <meta charset="utf-8"/>
          </head>
          <body>
            {content}
          </body>
        </html>'''
        item.set_content(xhtml)

# Save and download
epub.write_epub(output_filename, book)
print(f"Saved: {output_filename}")
files.download(output_filename)
