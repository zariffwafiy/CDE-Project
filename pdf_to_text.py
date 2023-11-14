import fitz  # PyMuPDF

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

# Example usage
pdf_path = 'data\PETRONAS-Integrated-Report-2022.pdf'
txt_output_path = r"data\PETRONAS-Integrated-Report-2022.txt"

extract_text_from_pdf(pdf_path, txt_output_path)
