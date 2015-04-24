#!/usr/bin/env python
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import os.path
from glob import glob
from codecs import open

from topicexplorer.lib import util

import chardet

def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    text += '\n'
    return text 

def convert_and_write(fname, output_dir=None, overwrite=False):
    if output_dir is not None and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output = fname.replace('.pdf','.txt')
    if output_dir:
        output = os.path.join(output_dir, output)

    if overwrite or util.overwrite_prompt(output):
        with open(output, 'wb') as outfile:
            outfile.write(convert(fname))
        print "converted", fname, "->", output

def main(path_or_paths, output_dir=None):
    if isinstance(path_or_paths, basestring):
        path_or_paths = [path_or_paths]
    for p in path_or_paths:
        if os.path.isdir(p):
            for pdffile in util.find_files(p, '*.pdf'):
                convert_and_write(os.path.join(p, pdffile), output_dir)
        else:
            convert_and_write(p, output_dir)
    

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("path", nargs='+', help="PDF file or folder to parse",
        type=lambda x: util.is_valid_filepath(parser, x))
    parser.add_argument("-o", '--output',
        help="output path [default: same as filename]")

    args = parser.parse_args()

    main(args.path, args.output)