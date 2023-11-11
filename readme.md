# GPT PDF Translator

This script extracts text from OCRed PDFs, translate it, and generate new PDFs with the translated content. The script uses the GPT-3.5 Turbo API for translation.

## Prerequisites

Before using this script, make sure you have the following prerequisites installed:

- Python 3.x
- PyPDF2
- reportlab
- tqdm
- requests
- GPT-3.5 Turbo API key (You can obtain this from OpenAI)
- TrueType font file (.ttf) with support for Chinese characters (You can replace './font.ttf' with the path to your font file)

## Usage

1. First, provide your GPT-3.5 Turbo API key in the `api_key` variable.

2. Modify the `source_pdf` variable to specify the path to your source PDF file that you want to translate.

3. Adjust the `start_page` and `end_page` variables to define the range of pages you want to translate within the source PDF.

4. Run the script using the following command:

   ```shell
   python script.py
   ```

   This will initiate the translation process and create individual PDF files with translated content for each specified page.

5. If you want to retranslate specific pages, you can use the `retranslate_and_merge_pages` function by uncommenting it in the `main` function and providing the list of page numbers you want to retranslate.

6. The translated PDFs will be stored in the `./pages/` directory, and the final merged translated document will be named `final_translated_document.pdf`.

## Notes

- The script takes care of handling previous and next page content to ensure coherent translations.

- Make sure you have a valid API key and an internet connection for the translation process.

- You can replace the './font.ttf' font path with the path to your own TrueType font file if needed.

Feel free to customize the script according to your specific needs and enjoy automated translation and PDF processing!