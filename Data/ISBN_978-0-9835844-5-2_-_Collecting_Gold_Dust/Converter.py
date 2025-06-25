import sys
import re
import os
import roman
from pypdf import PdfReader
from Model import Chapter, Paragraph
import nltk

# Refer to
# https://stackoverflow.com/questions/78862426/unable-to-use-nltk-functions
nltk.download("punkt_tab")


class PageLayout:
    """
    reader_page_number: str
        The page number as it appears to a human reader on the printed (or
        rendered by a pdf viewer) page. Note that, some pages might have roman
        numbering, some pages an integerand some pages may have no numbering
        at all (e.g. the cover or back-cover or some illustrative pages).
    """

    def __init__(self, reader_page_number):
        self.reader_page_number = reader_page_number
        self._reference_text = None

    @property
    def reference_text(self):
        return self._reference_text

    def set_reference_text(self, value):
        self._reference_text = value


class ExtractedPage:
    """
    Representation of a pdf extracted page
    Attributes
    ----------
    page_number: int
        The index of the page as it appears extracted by pydf::PdfReader()
    original_pdf_page: str
        the text as original extracted by the constructor caller
    """

    def __init__(self, page_number, layout, original_page):
        self.page_number = page_number
        self.page_layout = layout
        self.original_pdf_page = original_page
        self.text = None

    def set_text(self, text_in):
        self.text = text_in

    def set_removed_header(self, removed_header):
        self.removed_header = removed_header

    def __repr__(self):
        return (
            "Extracted paragraph id: " + repr(id(self)) + "\n"
            "Python page number: " + str(self.page_number) + "\n"
            "Reader page number (written on paper and/or as given by pdf viewer): "
            + repr(self.page_layout.reader_page_number)
            + "\n"
            + "Original Text: "
            + repr(self.original_pdf_page.extract_text(extraction_mode="layout"))
            + "\n"
            + "Removed header: "
            + repr(self.removed_header)
            + "\n"
            + "Extracted text: "
            + repr(self.text)
        )


class ExtractedParagraph:
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
        # self.extracted_page = extracted_page

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
            os.path.dirname(__file__),
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

        # The structural information constituted by the presence of chapters,
        # illustrations, illumination, headers ... is quite often difficult
        # to be automatically discovered. While waiting for better (and free)
        # tools, the following is a manually extracted.
        # Concerning the format:
        # "type" is the {"chapter", "generic" "illustration"}
        # A page_info of "chapter" type must have a "chapter_info" dictionary
        self.pages_info = {
            0: {
                # Artificial/fake chapter that is not explicitly defined in the
                # book. This is a technicality for the first pages not to be
                # devoid of belonging chapter:
                "type": "chapter",
                "chapter_info": {
                    "name": "",
                    "illumination_delimiter": None,
                },
                "paragraph_fits_on_page": True,
            },
            1: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            2: {
                "type": "illustration",
            },
            3: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            4: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            5: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            6: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            7: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Acknowledgements",
                    "illumination_delimiter": "MBhaddanta",
                },
                "paragraph_fits_on_page": True,
            },
            9: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Dear Reader",
                    "illumination_delimiter": "Iobservation",
                },
            },
            10: {
                "type": "generic",
                # Notice that "practice." would be an erroneous delimiter:
                "first_paragraph_delimiter": "flagging practice.",
            },
            11: {
                "type": "generic",
                "first_paragraph_delimiter": "view.",
            },
            12: {
                "type": "generic",
                "first_paragraph_delimiter": "daily life.",
            },
            13: {
                "type": "generic",
                "first_paragraph_delimiter": "info@wisdomstreams.org.",
            },
            14: {
                "type": "generic",
                "first_paragraph_delimiter": "Tuck Loon.",
            },
            15: {
                "type": "chapter",
                "chapter_info": {
                    "name": "On Language",
                    "illumination_delimiter": "Wwords",
                },
            },
            16: {
                "type": "generic",
                "first_paragraph_delimiter": "wisdom.",
            },
            17: {
                "type": "chapter",
                "chapter_info": {"name": "Contents", "illumination_delimiter": None},
                "paragraph_fits_on_page": True,
            },
            18: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            19: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            20: {
                "type": "illustration",
                # By default pages with illustrations (or illustration quotes)
                # have no headers. The following line is thus implicit
                # "header": None,
            },
            21: {
                "type": "chapter",
                "chapter_info": {
                    "name": "A Note from the Teacher",
                    "illumination_delimiter": "Ytime",
                },
            },
            22: {
                "type": "generic",
                "first_paragraph_delimiter": "wisdom.",
            },
            23: {
                "type": "generic",
                # Everything shorter would be wrong
                "first_paragraph_delimiter": "was that I was mindful.",
            },
            24: {
                "type": "illustration",
            },
            25: {
                "type": "generic",
                "first_paragraph_delimiter": "discoveries.",
            },
            26: {
                "type": "generic",
                "first_paragraph_delimiter": "thing.",
            },
            27: {
                "type": "generic",
                "first_paragraph_delimiter": "do it.”",
            },
            28: {
                "type": "generic",
                "first_paragraph_delimiter": "center.",
            },
            29: {
                "type": "generic",
                "first_paragraph_delimiter": "depression.",
            },
            30: {
                "type": "illustration",
            },
            31: {
                "type": "generic",
                "first_paragraph_delimiter": "resort.",
            },
            32: {
                "type": "generic",
                "first_paragraph_delimiter": "state.",
            },
            33: {
                "type": "generic",
                "first_paragraph_delimiter": "mind.",
            },
            34: {
                "type": "generic",
                "first_paragraph_delimiter": "emotions.",
            },
            35: {
                "type": "generic",
                "first_paragraph_delimiter": "disguise!",
                # We don't have to look for paragraph continuation on the next
                # page
                "paragraph_fits_on_page": True,
            },
            36: {
                "type": "illustration",
            },
            37: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            # 38: well nothing to express
            39: {
                "type": "generic",
                "first_paragraph_delimiter": "time.",
                "paragraph_fits_on_page": True,
            },
            # 40: zilch
            41: {
                "type": "generic",
                "first_paragraph_delimiter": "himself.",
                "paragraph_fits_on_page": True,
            },
            42: {
                "type": "illustration",
            },
            43: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Mindfulness is a Lifestyle Change",
                    "illumination_delimiter": "WTwo",
                },
            },
            44: {
                "type": "illustration",
            },
            45: {
                "type": "generic",
                "first_paragraph_delimiter": "mind.",
                "paragraph_fits_on_page": True,
            },
            46: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            # 47: zilch
            48: {
                "type": "generic",
                "first_paragraph_delimiter": "business.",
                "paragraph_fits_on_page": True,
            },
            50: {
                "type": "illustration",
            },
            51: {
                "type": "generic",
                "first_paragraph_delimiter": "suffering.",
                "paragraph_fits_on_page": True,
            },
            # 52: zilch
            53: {
                "type": "generic",
                "first_paragraph_delimiter": "day.",
                "paragraph_fits_on_page": True,
            },
            # 54: nada
            55: {
                "type": "generic",
                "first_paragraph_delimiter": "understanding.",
            },
            56: {
                "type": "illustration",
            },
            57: {
                "type": "generic",
                "first_paragraph_delimiter": "habits.",
            },
            58: {
                "type": "generic",
                "first_paragraph_delimiter": "happen.",
            },
            59: {
                "type": "generic",
                "first_paragraph_delimiter": "effect.",
            },
            60: {
                "type": "generic",
                "first_paragraph_delimiter": "Understanding.",
                "paragraph_fits_on_page": True,
            },
            # 61: nichts
            62: {
                "type": "illustration",
            },
            63: {
                "type": "generic",
                "first_paragraph_delimiter": "you.",
                "paragraph_fits_on_page": True,
            },
            64: {
                "type": "illustration",
            },
            65: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Take a Closer Look",
                    "illumination_delimiter": "Man",
                },
            },
            66: {
                "type": "generic",
                "first_paragraph_delimiter": "vedanā.",
            },
            67: {
                "type": "generic",
                "first_paragraph_delimiter": "experience.",
                "paragraph_fits_on_page": True,
            },
            68: {
                "type": "illustration",
            },
            # 69: this space intentionally left non void
            70: {
                "type": "generic",
                "first_paragraph_delimiter": "effects.",
                "paragraph_fits_on_page": True,
            },
            # 71: default is ok
            72: {
                "type": "generic",
                "first_paragraph_delimiter": "further.",
                "paragraph_fits_on_page": True,
            },
            73: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            74: {
                "type": "illustration",
            },
            # 75: nothing
            76: {
                "type": "generic",
                "first_paragraph_delimiter": "happening.",
                "paragraph_fits_on_page": True,
            },
            77: {
                "type": "illustration",
                # By default illustrations have no header, unless ... they have
                "header": True,
            },
            78: {
                "type": "illustration",
            },
            79: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Reflect. Learn. Keep Going.",
                    "illumination_delimiter": "Dnot",
                },
            },
            80: {
                "type": "generic",
                "first_paragraph_delimiter": "through.",
                "paragraph_fits_on_page": True,
            },
            # 81: nothing to say
            82: {
                "type": "illustration",
            },
            83: {
                "type": "generic",
                "first_paragraph_delimiter": "process.",
            },
            84: {
                "type": "generic",
                "first_paragraph_delimiter": "uncomfortable.",
                "paragraph_fits_on_page": True,
            },
            # 85: nothing
            86: {
                "type": "generic",
                "first_paragraph_delimiter": "practice.",
            },
            87: {
                "type": "generic",
                "first_paragraph_delimiter": "or another.",
                "paragraph_fits_on_page": True,
            },
            88: {
                "type": "illustration",
            },
            89: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            90: {
                "type": "illustration",
            },
            91: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Day-to-Day",
                    "illumination_delimiter": "Wchange",
                },
            },
            92: {
                "type": "generic",
                "first_paragraph_delimiter": "term.",
                "paragraph_fits_on_page": True,
            },
            # 93: nothing to say
            94: {
                "type": "illustration",
            },
            95: {
                "type": "generic",
                "first_paragraph_delimiter": "deepened.",
            },
            96: {
                "type": "generic",
                "first_paragraph_delimiter": "effect.",
                "paragraph_fits_on_page": True,
            },
            # 97: default
            98: {
                "type": "generic",
                "first_paragraph_delimiter": "people.",
                "paragraph_fits_on_page": True,
            },
            99: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            100: {
                "type": "illustration",
            },
            # 101: dalmatians
            102: {
                "type": "generic",
                "first_paragraph_delimiter": "automatic.",
                "paragraph_fits_on_page": True,
            },
            # 103: default works
            104: {
                "type": "generic",
                "first_paragraph_delimiter": "time.",
            },
            105: {
                "type": "generic",
                "first_paragraph_delimiter": "well.",
            },
            106: {
                "type": "illustration",
            },
            107: {
                "type": "generic",
                "first_paragraph_delimiter": ".",  # Notice the default case
            },
            108: {
                "type": "generic",
                "first_paragraph_delimiter": "steadier.",
            },
            109: {
                "type": "generic",
                "first_paragraph_delimiter": "silent?",
            },
            110: {
                "type": "generic",
                "first_paragraph_delimiter": "it.",
            },
            111: {
                "type": "generic",
                "first_paragraph_delimiter": "balanced.",
                "paragraph_fits_on_page": True,
            },
            112: {
                "type": "illustration",
            },
            # 113: nothing
            114: {
                "type": "generic",
                "first_paragraph_delimiter": "understanding.",
                "paragraph_fits_on_page": True,
            },
            # 115: nothing
            116: {
                "type": "generic",
                "first_paragraph_delimiter": "violated.",
            },
            117: {
                "type": "generic",
                "first_paragraph_delimiter": "disappear.",
                "paragraph_fits_on_page": True,
            },
            118: {
                "type": "illustration",
            },
            119: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            # 120: nothing
            121: {
                "type": "generic",
                "first_paragraph_delimiter": "people.",
            },
            122: {
                "type": "generic",
                "first_paragraph_delimiter": "deteriorate.",
            },
            123: {
                "type": "generic",
                "first_paragraph_delimiter": "way!",
                "paragraph_fits_on_page": True,
            },
            124: {
                "type": "illustration",
            },
            125: {
                "type": "chapter",
                "chapter_info": {
                    "name": "A Lighter Approach",
                    "illumination_delimiter": "Wawareness",
                },
                "paragraph_fits_on_page": True,
            },
            # 126: nothing
            127: {
                "type": "generic",
                "first_paragraph_delimiter": "life.",
            },
            128: {
                "type": "illustration",
            },
            129: {
                "type": "generic",
                "first_paragraph_delimiter": "habits.",
            },
            130: {
                "type": "generic",
                "first_paragraph_delimiter": "solutions.",
            },
            131: {
                "type": "generic",
                "first_paragraph_delimiter": "truth.",
            },
            132: {
                "type": "generic",
                "first_paragraph_delimiter": "lives.",
                "paragraph_fits_on_page": True,
            },
            133: {
                "type": "illustration",
                # By default illustrations have no header, unless ... they have
                "header": True,
            },
            134: {
                "type": "illustration",
            },
            135: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Continuing the Work",
                    "illumination_delimiter": "A remember",
                },
            },
            136: {
                "type": "generic",
                "first_paragraph_delimiter": "moment.",
                "paragraph_fits_on_page": True,
            },
            137: {
                "type": "generic",
                "first_paragraph_delimiter": "Thought.",
                "paragraph_fits_on_page": True,
            },
            138: {
                "type": "illustration",
            },
            # 139
            140: {
                "type": "generic",
                "first_paragraph_delimiter": "perspective.",
            },
            141: {
                "type": "generic",
                "first_paragraph_delimiter": ".",  # End of first sentence
            },
            142: {
                "type": "generic",
                "first_paragraph_delimiter": "useful.",
            },
            143: {
                "type": "generic",
                "first_paragraph_delimiter": "operate.",
                "paragraph_fits_on_page": True,
            },
            144: {
                "type": "illustration",
            },
            145: {
                "type": "chapter",
                "chapter_info": {
                    "name": "Appendix: Mindfulness in Brief",
                    "illumination_delimiter": "Sour",
                },
            },
            146: {
                "type": "generic",
                "first_paragraph_delimiter": "the mind.",
            },
            147: {
                "type": "generic",
                "first_paragraph_delimiter": "mind.",
                "paragraph_fits_on_page": True,
            },
            148: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            149: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            150: {
                "type": "illustration",
            },
            # 151
            152: {
                "type": "generic",
                "first_paragraph_delimiter": ".",
                "paragraph_fits_on_page": True,
            },
            153: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            154: {
                "type": "generic",
                "paragraph_fits_on_page": True,
            },
            # 155
            156: {
                "type": "illustration",
            },
            157: {
                "type": "generic",
                "first_paragraph_delimiter": "learn.",
                "paragraph_fits_on_page": True,
            },
            158: {
                "type": "chapter",
                "chapter_info": {"name": "Dedication", "illumination_delimiter": None},
                "paragraph_fits_on_page": True,
            },
            159: {
                # This is the back cover of the book
                "type": "illustration",
            },
        }

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

    def __page_is_illustration(self, page_number):
        if not page_number in self.pages_info:
            return False
        if not "type" in self.pages_info[page_number]:
            print("Page with no known type (page number ", page_number, ").")
            print("Exiting")
            sys.exit()
        if self.pages_info[page_number]["type"] == "illustration":
            return True
        return False

    def __page_requires_paragraph_continuation(self, page_number):
        if not page_number in self.pages_info:
            return True  # Looks a bit ambitious but let's try it
        if self.__page_is_illustration(page_number):
            return False
        if "paragraph_fits_on_page" in self.pages_info[page_number]:
            return False
        return True

    def __get_page_number_finishing_last_paragraph(self, page_number):
        """
        A pages that is followed by an illustration will need to skip that
        illustration page in order to retrieve the end of its last paragraph.
        Return the page number of the first page that defines a paragraph
        delimiter.
        """
        next_page_number = page_number + 1
        while not self.__page_has_paragraph_delimiter(next_page_number):
            if not self.__page_is_illustration(next_page_number):
                print(
                    "Oddly enough we are on page number ",
                    page_number,
                    " and we are looking for the page holding the content of the end of the paragraph.",
                )
                print("Yet page number ", next_page_number, " is not an illustration.")
                print("How could this be?")
                print(
                    "Maybe we forgot to define the first_paragraph_delimiter of page number ",
                    next_page_number,
                    "?",
                )
                print("Exiting.")
                sys.exit()
            next_page_number += 1
        return next_page_number

    def __page_has_paragraph_delimiter(self, page_number):
        if not page_number in self.pages_info:
            return False
        if not "first_paragraph_delimiter" in self.pages_info[page_number]:
            return False
        return True

    def __get_first_paragraph_delimiter(self, page_number):
        """
        Return the delimiting string (delimiter) the end of the paragraph that
        started on the previous page and finishes on page with the page number page_number
        """
        if not self.__page_has_paragraph_delimiter(page_number):
            print("How is it that were a looking for an unknown delimiter?")
            print("Exiting")
            sys.exit()
        return self.pages_info[page_number]["first_paragraph_delimiter"]

    def __is_chapter_beginning_page(self, page_number):
        if not page_number in self.pages_info:
            return False
        if self.pages_info[page_number]["type"] == "chapter":
            return True
        return False

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
            if self.__is_chapter_beginning_page(page_number):
                current_chapter_page = page_number
            self.__chapter_page[page_number] = current_chapter_page

    def __get_chapter_page(self, page_number):
        self.__initialize_chapter_page()
        return self.__chapter_page[page_number]

    def __get_chapter_name(self, page_number):
        chapter_page = self.__get_chapter_page(page_number)
        return self.pages_info[chapter_page]["chapter_info"]["name"]

    def __convert_to_logical_page_number(self, page_number):
        if page_number == 0:
            return "Cover"
        # Deal with the first pages numbering that uses roman numeration
        if page_number >= 1 and page_number <= 17:
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

    def fix_illumination(self, page_number, text_to_fix):
        """Chapters beginnings (that is the first page of a new chapter) start
        with an illumination (decorated first letter) that confuses pypdf.
        The letter of the illumination ends mixed up within the text of the
        first sentence of the chapter. Fix that.
        """
        if not self.__is_chapter_beginning_page(page_number):
            print("Erroneous call to Converter::fix_illumination()")
            print("  This does not seem to be a chapter starting page.")
            print("  Exiting")
            sys.exit()
        delimiter = self.pages_info[page_number]["chapter_info"][
            "illumination_delimiter"
        ]
        if delimiter is None:
            # This chapter has no illumination to fix (probably because there
            # is no illumination at all). Return the original text:
            return text_to_fix
        # The illumination character that got embedded in the text happens to
        # to always be preceded by a return character. Looking for the delimiter
        # prefixed with a return character will make the result a little more
        # secure (yet not foolproof):
        delimiter_with_return = "[\n]" + delimiter
        if not re.search(delimiter_with_return, text_to_fix):
            print(
                "Delimiter ",
                repr(delimiter),
                "not found within illumination of chapter on page ",
                page_number,
                ".",
            )
            print(
                "Chapter text that we were looking to fix: ",
                repr(text_to_fix),
            )
            print("Exiting.")
            sys.exit()
        # The first thing to do is to remove the illumination character from
        # the text. We use this opportunity to replace the return character,
        # that prefixed the delimiter, with a whitespace:
        corrected_snippet = delimiter[1:]
        text_to_fix = re.sub(
            delimiter_with_return, " " + corrected_snippet, text_to_fix
        )
        # The second thing to do is to reinsert the illumination character
        # within the text
        text_to_fix = delimiter[0] + text_to_fix
        # The third fix consists in replacing the hand made spacing of the
        # first lines of the text (that would be overwritten by the illumination
        # drawing of the leading character) with a single white space:
        return re.sub("\n      ", " ", text_to_fix)

    def __is_headless_page(self, page_number):
        # Only illustrations can be headless
        if not self.__page_is_illustration(page_number):
            return False
        # Yet some illustrations still have a header
        if "header" in self.pages_info[page_number]:
            return False
        # Eventually illustrations not flagged as having a header are headless
        return True

    def __get_page_header(self, page_number):

        if page_number < 0 or page_number > self.total_page_number:
            print("Page number is outside of book page numeration.")
            print("Exiting")
            sys.exit()

        # Pages explicitly flagged as headless, well, are headless:
        if self.__is_headless_page(page_number):
            return ""

        # First headers of pages starting a new chapter have that new
        # chapter name as header
        if self.__is_chapter_beginning_page(page_number):
            return self.__get_chapter_name(page_number)

        ####### Concerning the Preamble (from page 0 to 20 included)
        # Before the body of the book, there is a (quite lengthy) preamble that
        # has quite specific header rules :
        if page_number < 10:
            # Default value for a preamble header is to be empty
            return ""
        if page_number >= 10 and page_number < 15:
            return roman.toRoman(page_number).lower()
        if page_number == 16:
            # The following hardcoded value for page 16 is because that page
            # doesn't follow the above logical rule. The following fix for page
            # 16 _is_ correct ! It is the pdf that is erroneous.
            return roman.toRoman(16).lower() + roman.toRoman(16).lower()
        if page_number == 17:
            return ""
        if page_number >= 18 and page_number < 20:
            return str(self.__convert_to_logical_page_number(page_number))
        if page_number <= 19 and page_number <= 21:
            return ""

        ####### Concerning the body of the book.
        # Pages of the body of the book, have a headers that follow a simple
        # constructive rule with some exceptions...

        if (page_number % 2) == 0:
            # Odd pages have a header that is simply the book title followed
            # by their page number
            return self.__book_title_page_header(page_number)
        if (page_number % 2) != 0:
            if page_number == 133:
                # Page 133 has a brain damaged header that doesn't
                # follow the even page header rule (although it is a near miss). The
                # only possible fix is to define an exception:
                return (
                    self.book_title
                    + self.__get_chapter_name(133)
                    + "  | | "
                    + str(self.__convert_to_logical_page_number(133))
                    + str(self.__convert_to_logical_page_number(133))
                )
            else:
                # Even pages have a different header pattern based on the current
                # chapter name
                return self.__chapter_page_header(page_number)

        print("Header for page number ", page_number, " is not defined")
        print("Exiting")
        sys.exit()

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
                PageLayout(self.__convert_to_logical_page_number(page_number)),
                original_page,
            )
            self.remove_header(new_extracted_page)
            current_chapter.add_page(new_extracted_page)
        for chapter in resulting_chapters:
            self.sanitize_newlines(chapter)
        for chapter in resulting_chapters:
            self.reconstitute_pages_ending_sentence(chapter)
        for chapter in resulting_chapters:
            self.break_chapter_into_paragraphs(chapter)
        return resulting_chapters

    def sanitize_newlines(self, chapter):
        # Newlines are encountered to denote different usages
        #  - set some tabulations of illuminations (example "\       ")
        #  - define a new paragraph in which case newline is followed by
        #    exactly 4 whitespaces (example "\n    ")
        #  - simple line folding within paragraphs. In which case they are
        #    preceded or followed by a single whitespace or without (examples
        #    "here\nand", "here \nand", "here\n and")
        # This method only fixes the last case while preserving the other ones
        for page in chapter.pages:
            # We here need to use both lookbehind and lookahead notations. The
            # following pattern is here: look for a newline preceded (?<=...)
            # by any character that is not an extended whitespace (\s) and
            # followed (?=[^\s]) by any character that is not a whitespace:
            new_text = re.sub("(?<=[^\s])\n(?=[^\s])", " ", page.text)
            page.text = new_text

    def break_chapter_into_paragraphs(self, chapter):
        for page in chapter.pages:
            paragraphs = re.split("\n    ", page.text)
            page_number = page.page_layout.reader_page_number
            for paragraph_text in paragraphs:
                if len(paragraph_text) == 0:
                    # Avoid creating empty paragraphs (resulting from previous
                    # erroneous/careless string manipulations):
                    continue
                new_paragraph_layout = PageLayout(page_number)
                new_paragraph_layout.set_reference_text(
                    "[Chapter: "
                    + chapter.name
                    + ", reader page number: "
                    + str(page_number)
                    + ", page number: "
                    + str(page.page_number)
                    + "]"
                )
                new_paragraph = Paragraph(new_paragraph_layout)
                new_paragraph.text = paragraph_text
                chapter.add_paragraph(new_paragraph)

    def reconstitute_pages_ending_sentence(self, chapter):
        """
        When a page ends with un unfinished sentence then the next page begins
        with the end of that sentence. If we want the page layout to be correct
        we need to reconstitute the unfinished sentence of the pages. In order
        to do so, we need to remove the finishing part of the sentence from the
        next page and for this we need to know were that (partial) sentence
        ends. By default the delimiter is the dot ("."") character but when this
        is not the case we use a manually defined delimiter (an ad-hoc string).
        """
        if len(chapter.pages) == 1:
            # Nothing to do for a single page
            return
        for page_index in range(0, len(chapter.pages) - 1):
            current_page = chapter.pages[page_index]
            page_number = current_page.page_number
            if not self.__page_requires_paragraph_continuation(page_number):
                continue
            next_page_number = self.__get_page_number_finishing_last_paragraph(
                page_number
            )
            if not self.__page_has_paragraph_delimiter(next_page_number):
                # The page was explicitly stated as no to be treated. Skip it.
                continue
            if self.__is_chapter_beginning_page(next_page_number):
                # The next page is the starting page of a new chapter. This
                # implies that the current page is the last page of this
                # chapter which is thus complete. There is hence nothing to be
                # collected from the next page
                continue

            number_skipped_pages = next_page_number - page_number - 1
            next_page = chapter.pages[page_index + 1 + number_skipped_pages]
            # Note: when some illustration pages have been skipped in order to
            # retrieve the page holding the end of the paragraph, it is most
            # often due to the fact that we found some illustration in between.
            # We thus could/should advance the page_index in order to skip that
            # (illustration) page when reconstituting the paragraph. Yet we
            # leave this non optimal situation for code readability reasons.
            delimiter = self.__get_first_paragraph_delimiter(next_page_number)
            try:
                ending_sentence, remaining_page_text = next_page.text.split(
                    delimiter, 1
                )
                current_page.set_text(current_page.text + ending_sentence + delimiter)
                next_page.text = remaining_page_text
            except:
                print(
                    "Within page number ",
                    next_page.page_number,
                    " unable to find delimiter ",
                    delimiter,
                    " within page text: ",
                    next_page.text,
                )
                print("Skipping handling of page number ", page_number)
                continue

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
        header_text = self.__get_page_header(extracted_page.page_number)
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
                "(that is reader page number ",
                extracted_page.page_layout.reader_page_number,
                ")",
            )
            original_page_text = extracted_page.original_pdf_page.extract_text(
                extraction_mode="layout"
            )
            print("Pdf original text : ", repr(original_page_text))
            print("Exiting.")
            sys.exit()
        # Proceed with the removal of the header
        header_less_page_text = re.sub(header_text, "", header_less_page_text)
        extracted_page.set_removed_header(header_text)
        # Eventually, remove some possibly leaving whitespaces
        header_less_page_text = header_less_page_text.lstrip()
        # When necessary fix chapter illumination
        page_number = extracted_page.page_number
        if self.__is_chapter_beginning_page(page_number):
            header_less_page_text = self.fix_illumination(
                page_number, header_less_page_text
            )

        # Break the original streamlined text into sentences.
        # FIXME FIXME
        tokenized_text = nltk.tokenize.sent_tokenize(header_less_page_text)
        # print("Tokenized text: ", nltk.tokenize.sent_tokenize(text))

        extracted_page.text = header_less_page_text
