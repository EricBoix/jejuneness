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
        print("##########################################################")
        print(repr(page))
        print("##########################################################")


print("##########################################################")
print("##########################################################")
print("#################### OTHER ###############################")
print("##########################################################")
print("##########################################################")
for chapter in document.chapters:
    print("###################################################################")
    print("################## Chapter name: ", chapter.name)
    print("###################################################################")
    for paragraph in chapter.paragraphs:
        print(
            "Paragraph (ref:",
            paragraph.page_layout.reference_text,
            "):\n",
            paragraph.text,
            "\n",
        )
