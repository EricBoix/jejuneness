from Model import Document
from Converter import Converter

converter = Converter()
document = Document()
for chapter in converter.build_chapters():
    document.add_chapter(chapter)

for chapter in document.chapters:
    print("###################################################################")
    print("################## Chapter name: ", chapter.name)
    print("###################################################################")
    for page in chapter.pages:
        print("Python page number :", page.page_number)
        print(
            "Reader page number (starting from 1 in a pdf viewer):",
            page.reader_page_number,
        )
        print(
            "Original Text: ",
            repr(page.original_pdf_page.extract_text(extraction_mode="layout")),
        )
        print("Header to remove: ", converter.headers[page.page_number])
        print("Tokenized Text: ", repr(page.text))
        print("##########################################################\n\n")
