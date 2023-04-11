from pdfquery import PDFQuery
from itertools import groupby
from pypdf import PdfReader

def pdf_scraping():
    # pdf = PDFQuery('coventry_hmo/coventry_p4-5.pdf')
    # pdf.load()
    #
    # # Use CSS-like selectors to locate the elements
    # text_elements = pdf.pq('LTTextLineHorizontal')
    #
    # # Extract the text from the elements
    # text = [t.text for t in text_elements]
    # test_list = [list(g) for k, g in groupby(text, lambda x: x == 'Licensee ') if not k]
    #
    # data = []
    # for index, item in enumerate(test_list):
    #     item = [i.strip() for i in item]
    #     item.insert(0, "Licensee")
    #
    #     for i, j in enumerate(item):
    #         if j != '':
    #             print(f"{i} -> {j}")
    #
    #     data.append({
    #         'date': item[10],
    #         'reference': item[1]
    #     })
    #
    #     print(item)

    # reader = PdfReader("coventry_hmo/coventry_p4-5.pdf")
    # number_of_pages = len(reader.pages)
    # print(number_of_pages)
    # page = reader.pages[0]
    # text = page.extract_text()
    # print(text)

    # from pdfminer.high_level import extract_text
    #
    # text = extract_text("coventry_hmo/coventry_p4-5.pdf")
    # text = text.strip()
    # text = text.replace("\n", "")
    # text = text.replace("\t", "")
    # test_list = [list(g) for k, g in groupby(text, lambda x: x == "REGISTER") if not k]
    # print(test_list)
    #
    # from pdfrw import PdfReader, PdfWriter, IndirectPdfDict
    # x = PdfReader('coventry_hmo/coventry_p4-5.pdf')
    # print(x.pages[0].Contents.stream)

    import os
    from io import StringIO
    import re
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage

    manager = PDFResourceManager()
    retstr = StringIO()
    layout = LAParams(all_texts=False, detect_vertical=True)
    device = TextConverter(manager, retstr, laparams=layout)
    interpreter = PDFPageInterpreter(manager, device)
    with open("coventry_hmo/coventry_p4-5.pdf", 'rb') as filepath:
        for page in PDFPage.get_pages(filepath, check_extractable=True):
            interpreter.process_page(page)
    text = retstr.getvalue()
    print(text)
    device.close()
    retstr.close()



if __name__ == '__main__':
    pdf_scraping()
