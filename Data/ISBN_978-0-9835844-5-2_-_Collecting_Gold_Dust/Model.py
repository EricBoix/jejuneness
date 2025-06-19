class Document:
    """
    A list of Chapters.
    """

    def __init__(self):
        self.chapters = []

    def add_chapter(self, new_chapter):
        self.chapters.append(new_chapter)


class PageLayout:
    def __init__(self, reader_page_number):
        self.reader_page_number = reader_page_number


class Chapter:
    """
    A list of Paragraphs.
    """

    def __init__(self, name):
        self.name = name
        self.pages = []  # The original pages out of which this chapter is made
        self.paragraphs = []  # The paragraphs that got extracted from the pages
        self.page_layout = None

    def add_page(self, page):
        self.pages.append(page)

    def add_paragraph(self, new_paragraph):
        self.chapters.append(new_paragraph)


class Paragraph:
    """
    A list of sentences.
    """

    def __init__(self):
        self.sentences = {}


class Sentence:
    """
    A sentence _has_ a Layout (a page identifier for the reader to retrieve it)
    """

    def __init__(self, text, reader_page_number):
        self.sentence = text
        self.page_layout = PageLayout(reader_page_number)
