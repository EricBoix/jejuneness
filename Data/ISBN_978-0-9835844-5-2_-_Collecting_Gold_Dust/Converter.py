import sys
import re
import os
import roman
from pypdf import PdfReader
from Model import Chapter
import nltk

# Refer to
# https://stackoverflow.com/questions/78862426/unable-to-use-nltk-functions
nltk.download("punkt_tab")


class ExtractedPage:
    """
    Representation of a pdf extracted page
    Attributes
    ----------
    page_number: int
        The index of the page as it appears extracted by pydf::PdfReader()
    reader_page_number: str
        The page number as it appears printed (rendered on the page by a pdf
        viewer). Some pages might have roman numbering, some pages an integer
        and some pages may have no numbering at all
    original_pdf_page: str
        the text as original extracted by the constructor caller
    """

    def __init__(self, page_number, reader_page_number, original_page):
        self.page_number = page_number
        self.reader_page_number = reader_page_number
        self.text = None
        self.original_pdf_page = original_page

    def set_text(self, text_in):
        self.text = text_in


class Converter:
    """
    Class converting the original set of pages extracted from the pypdf::reader
    to a structured document. In order to realize its purpose the Converter
    needs to be manually provided with the structural information (extracted by
    a human reader) that must be promoted to the semantic structure (document,
    chapter, sub-chapter, paragraph...).
    """

    def __init__(self):

        # The original pdf document file name that this converter will act from
        self.pdf_filename = os.path.join(
            "original_data",
            "2019_-_Sayadaw-U-Tejaniya-Collecting-Gold-Dust-Web-Book-1.pdf",
        )

        # The original pdf document has a title. This title ends-up embedded in
        # some headers of the pages and must be extracted from the text.
        self.book_title = "COLLECTING GOLD DUST: Nurturing the Dhamma in Daily Living"

        # This number of pages is already known (will assert it later on)
        self.total_page_number = 160

        # The preamble section pages use roman numbering. This offsets the numbering
        # of the body pages
        self.page_numbering_offset = 16

        # The structural information constituted by the presence of chapters is
        # hard to be automatically discovered. It thus need to be provided manually
        self.chapters = {
            7: "Acknowledgements",
            9: "Dear Reader",
            15: "On Language",
            17: "Contents",
            21: "A Note from the Teacher",
            43: "Mindfulness is a Lifestyle Change",
            65: "Take a Closer Look",
            79: "Reflect. Learn. Keep Going.",
            91: "Day-to-Day",
            125: "A Lighter Approach",
            135: "Continuing the Work",
            145: "Appendix: Mindfulness in Brief",
            158: "Dedication",
        }

        # Pages with illustrated quotes from the text have no headers
        self.headless_pages = [
            24,
            30,
            36,
            42,
            44,
            48,
            50,
            56,
            62,
            64,
            68,
            74,
            78,
            82,
            88,
            90,
            94,
            100,
            106,
            112,
            118,
            124,
            128,
            134,
            138,
            144,
            150,
            156,
            159,  # This is back cover of the book
        ]

        self.headers = {}

        # Technical (optimisation) variable used to hold the correspondance
        # between a given page number and the chapter to which that page
        # belongs to. In other terms for this dictionary
        #  - a key is a page number
        #  - the associated value holds the current chapter number for that key
        self.__chapter_page = {}

        self.reader = PdfReader(self.pdf_filename)
        if len(self.reader.pages) != self.total_page_number:
            print("Erroneous number of pages:")
            print(
                "Was expecting",
                self.total_page_number,
                " but got ",
                len(self.reader.pages),
            )
            print("Exiting")
            sys.exit()

        self.__initialize_page_header()

    def __is_chapter_beginning_page(self, page_number):
        return page_number in self.chapters

    def __book_title_page_header(self, page_number):
        return (
            str(self.__convert_to_logical_page_number(page_number))
            + r" \| "
            + self.book_title
        )

    def __chapter_page_header(self, page_number):
        return (
            self.__get_chapter_name(page_number)
            + r" \| "
            + str(self.__convert_to_logical_page_number(page_number))
        )

    def __initialize_chapter_page(self):
        if bool(self.__chapter_page):
            # Already initialized
            return
        current_chapter_page = None
        for page_number in range(0, self.total_page_number):
            if page_number in self.chapters:
                current_chapter_page = page_number
            self.__chapter_page[page_number] = current_chapter_page

    def __get_chapter_page(self, page_number):
        self.__initialize_chapter_page()
        return self.__chapter_page[page_number]

    def __get_chapter_name(self, page_number):
        return self.chapters[self.__get_chapter_page(page_number)]

    def __convert_to_logical_page_number(self, page_number):
        # Deal with the first pages numbering that uses roman numeration
        if page_number <= 17:
            return roman.toRoman(page_number).lower()
        # Just making sure
        original_reader_page = self.reader.pages[page_number]
        original_reader_page_number = self.reader.get_page_number(original_reader_page)
        if page_number != original_reader_page_number:
            print("Python page number does not match pypdf::reader page number:")
            print("   - Python page number: ", page_number)
            print("   - pypdf::reader page number: ", original_reader_page_number)
            print("Exiting.")
            sys.exit()
        return page_number - self.page_numbering_offset

    def __initialize_page_header(self):

        # Before the body of the book, there is a (quite lengthy) preamble that
        # has quite specific header rules :
        for page_number in range(0, 21):
            # First headers of pages starting a new chapter have that new
            # chapter name as header
            if self.__is_chapter_beginning_page(page_number):
                self.headers[page_number] = self.__get_chapter_name(page_number)
                continue

            # For some other specific pages the header holds the page number
            # (sometimes using the roman notation):
            if page_number in range(10, 15):
                self.headers[page_number] = roman.toRoman(page_number).lower()
                continue
            if page_number in range(18, 20):
                self.headers[page_number] = str(
                    self.__convert_to_logical_page_number(page_number)
                )
                continue

            # Eventually the default value for a preamble header is to be empty
            self.headers[page_number] = ""

        # The following pages, that is the body of the book, have a header that
        # follows a simple constructive rule with some exceptions...
        for page_number in range(21, self.total_page_number):
            # Some pages are illustrations with quotes extracted from the text
            # and because they mainly have pictural design, they are headless:
            if page_number in self.headless_pages:
                self.headers[page_number] = ""
                continue
            # Headers of pages starting a new chapter have that new chapter
            # name as header
            if self.__is_chapter_beginning_page(page_number):
                self.headers[page_number] = self.__get_chapter_name(page_number)
                continue
            if (page_number % 2) == 0:
                # Odd pages have a header that is simply the book title followed
                # by their page number
                self.headers[page_number] = self.__book_title_page_header(page_number)
                continue
            if (page_number % 2) != 0:
                if page_number == 133:
                    # Page 133 has a brain damaged header that doesn't
                    # follow the even page header rule (although it is a near miss). The
                    # only possible fix is to define an exception:
                    self.headers[133] = (
                        self.book_title
                        + self.__get_chapter_name(133)
                        + "  | | "
                        + str(self.__convert_to_logical_page_number(133))
                        + str(self.__convert_to_logical_page_number(133))
                    )
                else:
                    # Even pages have a different header pattern based on the current
                    # chapter name
                    self.headers[page_number] = self.__chapter_page_header(page_number)
                continue

            # Eventually the default value for a preamble header is to be empty
            self.headers[page_number] = ""

    def build_chapters(self):
        resulting_chapters = []
        current_chapter = Chapter("Preamble")
        resulting_chapters.append(current_chapter)
        for page_number in range(0, self.total_page_number):
            if self.__is_chapter_beginning_page(page_number):
                new_chapter_name = self.__get_chapter_name(page_number)
                current_chapter = Chapter(new_chapter_name)
                resulting_chapters.append(current_chapter)

            original_page = self.reader.pages[page_number]
            new_extracted_page = ExtractedPage(
                page_number,
                self.__convert_to_logical_page_number(page_number),
                original_page,
            )
            self.remove_header(new_extracted_page)
            current_chapter.add_page(new_extracted_page)
        return resulting_chapters

    def remove_header(self, extracted_page):
        """
        The original pdf text of a page is polluted with the content of the
        header of the page, that varies from chapter names, the book name,
        the page number, a combination of the above ... or nothing.
        Clean up this mess.
        """
        original_page_text = extracted_page.original_pdf_page.extract_text(
            extraction_mode="layout"
        )

        # Remove the heading bunch of whitespaces (and assimilated characters)
        header_less_page_text = original_page_text.lstrip()
        # Make sure the exact header text is encountered
        header_text = self.headers[extracted_page.page_number]
        if not re.match("^" + header_text, header_less_page_text):
            print(
                "Header ",
                header_text,
                "not found on pdf page ",
                extracted_page.page_number,
                " ",
                end="",
            )
            print(
                "(that is reader page number ", extracted_page.reader_page_number, ")"
            )
            print("Exiting.")
            print("ORIGINAL TEXT", repr(extracted_page.original_pdf_text))
            sys.exit()
        # Proceed with the removal of the header
        header_less_page_text = re.sub(header_text, "", header_less_page_text)
        # Eventually, remove some possibly leaving whitespaces
        header_less_page_text = header_less_page_text.lstrip()

        # Break the original streamlined text into sentences.
        # FIXME FIXME
        tokenized_text = nltk.tokenize.sent_tokenize(header_less_page_text)
        # print("Tokenized text: ", nltk.tokenize.sent_tokenize(text))

        extracted_page.text = header_less_page_text
