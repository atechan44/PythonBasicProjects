from pdf2docx import Converter

pdf_path = "sampleTry.pdf"
docx_path = "yourWordFile.docx"

cv = Converter(pdf_file = pdf_path)
cv.convert(docx_filename=docx_path)
cv.close()


