import fitz  # PyMuPDF
import glob
import os

def extract_text_from_pdf(pdf_path, txt_output_path):
    # Open the PDF file in binary mode
    pdf_document = fitz.open(pdf_path)

    # Iterate through each page
    for page_number in range(pdf_document.page_count):
        # Select the page
        page = pdf_document[page_number]

        # Extract text from the page
        text = page.get_text()

        # Write the extracted text to a text file
        with open(txt_output_path, "a", encoding="utf-8") as text_file:
            text_file.write(text + '\n\n')

    # Close the PDF file
    pdf_document.close()

if __name__ == "__main__":
    input_dir = "corpus/"
    txt_output_path = r"corpus\Corpus.txt"

    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    for pdf_file in pdf_files:
        # extract
        extract_text_from_pdf(pdf_file, txt_output_path)
