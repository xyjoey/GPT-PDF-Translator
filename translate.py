import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
import requests
from tqdm import tqdm
import json
import os

def translate_text(text):
    """
    Translates the given text using an external API.

    :param text: String to be translated.
    :return: Translated text as a string.
    """
    api_key = 'YOUR OPENAI API KEY'
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
          {
            "role": "system",
            "content": "仔细遵照指示。我要你充当一名从英文到中文的专业翻译。我将提供一页书籍中的OCR文本，你的任务是将其从英文翻译成中文。请只输出翻译，不要输出任何多余的无关内容。如果有乱码等非标准文字的内容，将乱码删除。请确保标题、角注和文本保持正确的格式，你可以自己排版、换行输出，用\n进行换行。你将被提供Previous Page: 前一页最后50个字符。Current Page: 当前页的ocr字符。Next Page: 下一页的前50个字符。只输出Current Page的中文翻译，参照前一页和下一页的内容来保持连贯但不输出。"
          },
          {
            "role": "user",
            "content": '只输出Current Page的中文翻译，不要输出除此之外的任何内容，不要输出有关Previous和Next Page的内容。不要提示用户，例如：这是当前页的翻译：'+ text
          }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = json.loads(response.text)
    content = response_data["choices"][0]["message"]["content"]

    return content

def extract_text_from_pdf(pdf_path, start_page, end_page):
    """
    Extracts text from specified pages of a PDF file.

    :param pdf_path: Path to the PDF file.
    :param start_page: Start page number (zero-indexed).
    :param end_page: End page number (zero-indexed).
    :return: Yields combined text of previous, current, and next page contents.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        previous_text = ''
        for i, page in enumerate(reader.pages[start_page:end_page+1], start_page):
            current_text = page.extract_text()
            next_text = reader.pages[i + 1].extract_text()[:50] if i < len(reader.pages) - 1 else ''
            combined_text = f"Previous Page: {previous_text[-50:]}\nCurrent Page: {current_text}\nNext Page: {next_text}"
            previous_text = current_text
            yield combined_text

def create_pdf_with_text(text, filename, font_path='./font.ttf'):
    """
    Creates a PDF file with the given text.

    :param text: Text to be included in the PDF.
    :param filename: Name of the output PDF file.
    :param font_path: Path to the TTF font file.
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
    text = text.replace('\n', '<br/>')

    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontName = 'ChineseFont'
    style.fontSize = 12
    style.leading = 15

    para = Paragraph(text, style=style)
    text_width = letter[0] - 2 * inch
    text_height = letter[1] - 2 * inch

    w, h = para.wrap(text_width, text_height)
    para.drawOn(can, inch, letter[1] - inch - h)

    can.save()
    packet.seek(0)
    with open(filename, 'wb') as file:
        file.write(packet.getvalue())

def merge_pdfs(pdf_list, output_filename):
    """
    Merges multiple PDF files into one.

    :param pdf_list: List of paths to PDF files to be merged.
    :param output_filename: Path for the output merged PDF file.
    """
    pdf_writer = PyPDF2.PdfWriter()
    for pdf in pdf_list:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    with open(output_filename, 'wb') as out:
        pdf_writer.write(out)


def retranslate_and_merge_pages(page_numbers, source_pdf, output_pdf, font_path='./font.ttf'):
    """
    Retranslates specified pages and merges them into a new PDF.

    :param page_numbers: List of page numbers to retranslate.
    :param source_pdf: Path to the source PDF file.
    :param output_pdf: Path for the output merged PDF file.
    :param font_path: Path to the .ttf font file supporting Chinese characters.
    """
    translated_pdfs = []
    reader = PyPDF2.PdfReader(source_pdf)

    for page_number in tqdm(page_numbers):
        page_index = page_number - 1  # Convert page number to 0-index
        page_text = reader.pages[page_index].extract_text()
        translated_text = translate_text(page_text)
        pdf_filename = f'./pages/translated_page_{page_number}.pdf'
        create_pdf_with_text(translated_text, pdf_filename, font_path)
        translated_pdfs.append(pdf_filename)

    merge_pdfs(translated_pdfs, output_pdf)

def main():
    """
    Main function to execute the translation and PDF creation process.
    """
    source_pdf = 'source.pdf'
    translated_pdfs = []
    start_page = 0
    end_page = len(PyPDF2.PdfReader(source_pdf).pages) - 1

    for i, combined_text in enumerate(tqdm(extract_text_from_pdf(source_pdf, start_page, end_page)), start_page):
        translated_text = translate_text(combined_text)
        pdf_filename = f'./pages/translated_page_{i+1}.pdf'
        create_pdf_with_text(translated_text, pdf_filename, font_path='./font.ttf')
        translated_pdfs.append(pdf_filename)

    merge_pdfs(translated_pdfs, 'final_translated_document.pdf')

if __name__ == '__main__':
    if not os.path.exists('pages'):
        os.makedirs('pages')

    main()
    # retranslate_and_merge_pages([5, 6], 'source.pdf', 'retranslated_document.pdf')