#############################################################################
##                              kt3extract                                    ##
#############################################################################
# Command line tool to consolidate several DHL labels 
# for printing with less waste

import os
import sys
import argparse
import glob
import re
from copy import deepcopy
from pypdf import PdfWriter, PdfReader, Transformation, PaperSize
from pypdf.generic import RectangleObject

#############################################################################
##                           Global variables                              ##
#############################################################################
input_path: str
output_format: str
horizontal_range: str
vertical_range: str
padding: float

#############################################################################
##                           Global constants                              ##
#############################################################################
CROPS = [
    [
    (127, 620, 468, 817), # Horizontal Line 1
    (127, 421, 468, 618), # Horizontal Line 2
    (127, 223, 468, 420), # Horizontal Line 3
    (127, 24, 468, 221)  # Horizontal Line 4
    ],
    [
    (100, 422, 297, 763), # Vertical Top Left
    (299, 422, 495, 763), # Vertical Top Right
    (100, 79, 297, 420),  # Vertical Bottom Left
    (299, 79, 495, 420)   # Vertical Bottom Right

    ]
#   (XBL, ZBL, XTR, ZTR)
]

#############################################################################
##                               Helpers                                   ##
#############################################################################

def argset():
    """
    Sets command line arguments
    """
    global input_path
    global output_format
    global horizontal_range
    global vertical_range
    global padding

    parser = argparse.ArgumentParser(description=
        "Command line tool to extract Kill Team 3rd edition datacards from free rules downloads")

    # Horizontal range
    parser.add_argument(
        '-hr', '--horizontal', 
        default="",
        type=str,
        help="""
            Range of pages with horizontal datacards
            "1-2"
            """
    )

    # Vertical range
    parser.add_argument(
        '-vr', '--vertical', 
        default="",
        type=str,
        help="""
            Range of pages with vertical datacards
            "3-4"
            """
    )
    
    # Input path
    parser.add_argument(
        '-input_path', '-i',
        type=str,
        help="""
            Path to input PDF.
            """
    )

    # Output Format
    parser.add_argument(
        '--output_format', '-o',
        default="png",
        type=str,
        help="""
            Format of output file.
            Available Options:
            png, pdf
            """
    )

    # Padding
    parser.add_argument(
        '--padding', '-p',
        default=0,
        type=int,
        help="""
            Amount of padding in mm to add to the cards for printing
            """
    )

    # Parse args
    args = parser.parse_args()
    input_path  = args.input_path
    output_format = args.output_format
    horizontal_range = args.horizontal
    vertical_range = args.vertical
    padding = args.padding

    # Test for ranges to be valid
    pattern = r'^\d+-\d+$'
    if not re.match(pattern, horizontal_range) or not re.match(pattern, vertical_range):
        print("Ranges entered invalid, please format them like '1-2'")
        sys.exit()

    # Test if input file is valid
    if not input_path.lower().endswith('.pdf'):
        print("File does not seem to be a pdf file")
        sys.exit()
    if not os.path.isfile(input_path):
        print("Input file does not seem to be a file at all")
        sys.exit()

    # Test if a valid output was set
    if not output_format == "pdf" and not output_format == "png":
        print("File format chosen does not match either pdf or png")
        sys.exit()


def read_file():
    """
    Read in and split file
    """
    global input_path
    global output_format
    global horizontal_range
    global vertical_range
    global padding

    # Prepare reader and writer
    reader = PdfReader(input_path)
    buffer = PdfWriter()
    writer = PdfWriter()

    # Get page ranges
    horirange =  [int(num) for num in horizontal_range.split('-')]
    verirange =  [int(num) for num in vertical_range.split('-')]
    pageranges = [horirange, verirange]

    # Loop through the page ranges
    for pagerange in range(2):
        # Loop through the pages of the range
        for page in range(pageranges[pagerange][0], pageranges[pagerange][1]+1):
            inpPage = reader.pages[page-1]
            # Loop through the 4 boxes where a card might be
            for card in range(4):
                # pagerange contains the number of the range we are currently reading
                # page is the actual page number of the current page we're looking at
                # card is the card slot number on the page we are looking at
                # CROPS[pagerange][card] should return the tuble of our current card cropbox
                
                # Read in single card with cropping
                cardPage = deepcopy(inpPage)
                cardPage.mediabox = cardPage.cropbox = RectangleObject(CROPS[pagerange][card])

                # Paste it over to a new card that is also cropped just to discard everything outside of cropping range
                bufferPage = buffer.add_blank_page(height=cardPage.mediabox.width, width=cardPage.mediabox.height)
                bufferPage.mediabox = bufferPage.cropbox = RectangleObject(CROPS[pagerange][card])
                bufferPage.merge_page(cardPage)

                # Another deep copy for exact scaling
                interPage = deepcopy(bufferPage)
                # if pagerange == 0:
                #     scale_x = (120 / 25.4 * 72) / interPage.mediabox.width
                #     scale_y = (70 / 25.4 * 72) / interPage.mediabox.height
                # else:
                #     scale_x = (70 / 25.4 * 72) / interPage.mediabox.width
                #     scale_y = (120 / 25.4 * 72) / interPage.mediabox.height
                # scaler = Transformation().scale(sx=scale_x, sy=scale_y)
                # interPage.add_transformation(scaler)

                # Create a padded page and paste our cropped thingy onto it
                paddingPoints = padding / 25.4 * 72
                if pagerange == 0:
                    newPage = writer.add_blank_page(width = 120 / 25.4 * 72 + 2 * paddingPoints, height = 70 / 25.4 * 72 + 2 * paddingPoints)
                else:
                    newPage = writer.add_blank_page(width = 70 / 25.4 * 72 + 2 * paddingPoints, height = 120 / 25.4 * 72 + 2 * paddingPoints)
                newPage.merge_translated_page(interPage, tx= -CROPS[pagerange][card][0] + paddingPoints, ty = -CROPS[pagerange][card][1] + paddingPoints)
                
                # Rotate horizontal pages so everything is in the same orientation
                if pagerange == 0:
                    # horizontal pages
                    newPage.rotate(-90)
                

    # Prepare output directory
    cwd = os.path.dirname(input_path)
    dirname = os.path.splitext(os.path.basename(input_path))[0]
    dirpath = os.path.join(cwd, dirname)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    # Output file(s)
    if output_format == "png":
        print("png output not yet implemented, sorgy")
        sys.exit()
    elif output_format == "pdf":
        # Write resulting PDF
        outputname = os.path.join(dirpath, "output.pdf");
        with open(outputname, "wb") as op:
            writer.write(op)

    print("---")
    print("All cards output")
    print("---")

#############################################################################
##                               main()                                    ##
#############################################################################
def main():

    print("-----------------------")
    print("--Starting kt3extract--")
    print("-----------------------")

    # Set command line arguments
    argset()

    # Output recognized args
    print("Using input path:")
    print(input_path)
    print("Using output format:")
    print(output_format)
    print("---")
    print("Assuming horizontal page range:")
    print(horizontal_range)
    print("Assuming vertical page range:")
    print(vertical_range)
    print("---")

    read_file()


#############################################################################
##                         main() idiom                                    ##
#############################################################################
if __name__ == "__main__":
    main()
