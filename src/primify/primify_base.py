import argparse
import math
from pathlib import Path

from PIL import Image, ImageFilter
from primify.next_prime import *

class PrimeImage(object):
    """
    This class provides methods to convert any image into a prime number.

    We use the python package Pillow to do all the image processing
    and sympy to check for primality.


    Arguments:

        image_path (Path): Path to image.

        max_digits (int): Maximal number of digits in the resulting prime.

        converion_method (int): number between 0 and 2. Play around to see
            which one produces the clearest image.

        verbose (bool): Verbose status reporting in terminal if True

        output_file (Path): Output file (default: "./prime.txt")

    Note:

        The computational complexity is O(d*log(d)^3) in the number of digits

    Example:

        if you have the source image at `./source.png` and you want to convert it into a prime contained in `./prime/prime.txt` which has at most 5000 digits and using conversion method 0 (other options are 1 or 2). Then you should run:

        `primify -v --image ./source.png --max_digits 5000 --method 0 --output_dir ./prime/ --output_file prime.txt`



    """

    def __init__(
        self,
        image_path: Path = False,
        max_digits: int = 5000,
        start_path: Path = False,
        conversion_method: int = 1,
        output_file_path: Path = Path("./prime.txt"),
        verbose: bool = False,
        parallel: bool = False,
    ):
        super(PrimeImage, self).__init__()

        self.IMAGE_PATH = image_path
        self.MAX_DIGITS = max_digits

        self.START_PATH = start_path


        # saving conversion method.
        self.CONVERSION_METHOD = conversion_method

        # saving verbosity status
        self.VERBOSE = verbose


        self.PARALLEL = parallel

        # check if verbose is boolean
        if not isinstance(verbose, bool):
            raise ValueError("Verbosity must be True or False")

        # check if max_digits is and integer and greater than 10
        if not (isinstance(self.MAX_DIGITS, int) or (self.MAX_DIGITS < 10)):
            raise ValueError("max_digits should be an integer and > 10")

        # Both height and width must be less than or equal to the root
        # of max_digits to insure that the total number of pixels does
        # not exceed max_digits.
        self.MAX_LENGTH = math.floor(self.MAX_DIGITS ** 0.5)

        # ordered list of digits from bright to dark
        self.ORDERED_DIGITS = [1, 7, 3, 9, 8]

        if not (self.IMAGE_PATH or self.START_PATH):
            raise Exception('Neither Image path or Start path specified')


        # loading the Pillow image object
        if self.IMAGE_PATH:
            self.im = Image.open(self.IMAGE_PATH)

        # saving output file path
        self.output_file_path = output_file_path

        # Flags to tell functions if certain heavy operations have
        # already been performed

        # True if we already converted the image to a number
        self.flag_numberised = False

        # True if we found a prime that looks like the image
        self.flag_primed = False

    def _resize(self):
        """
        We resize the image to contain at most max_size pixels

        description:
            The reason is that we don't want to find too large primes
        """

        # if verbose
        if self.VERBOSE:
            print("Resizing image...")

        # squash the height of the image to 45% to account for
        # the shape of the glyphs and the spacing between lines.
        x, y = self.im.size
        y_new = int(y * 0.45)

        self.im = self.im.resize((x, y_new), 1)

        # resizing to only have MAX_DIGITS many digits
        self.im.thumbnail([self.MAX_LENGTH, self.MAX_LENGTH])

        # getting width after resizing
        self.width = self.im.size[0]

        if self.VERBOSE:
            print(f"Resized image to be {self.width}x{self.im.size[1]} pixels.")

    def show(self):
        """Shows the Pillow image instance

        description:
            Mainly for debugging
        """
        # self.im.show()

    def _enhance(self):
        """We apply various filters to the image to improve the conversion
        to ASCII.

        Warning:
            SHOULD BE DONE AFTER RESIZING

        description:
            Step 1: Apply an edge enhancement algorithm

            Step 2: Convert to gray scale

            Step 3: Quantize to 5 color levels
        """

        if self.VERBOSE:
            print("Preparing image for conversion into number.")

        # Enhance edges using Pillow ImageFilter module
        self.im = self.im.filter(ImageFilter.EDGE_ENHANCE)

        # convert to gray scale
        self.im = self.im.convert(mode="L")

        # quantize image into 5 levels
        self.im = self.im.quantize(colors=5, method=self.CONVERSION_METHOD)

    def numberise(self):
        """Turn the image into a number that looks like the image

        description:
            We convert the picture into a gray scale image with 5 levels
            of greyness and then map each level to a digit and return that array.
        """
        # Do nothing if we already numberised
        if self.flag_numberised:
            return 0

        # resize and enhance image
        self._resize()
        self._enhance()

        if self.VERBOSE:
            print("Converting image to a number...")

        # map each level or greyness to a number between 0 and 10
        self.CONVERTED_IMAGE_DATA = [
            str(self.ORDERED_DIGITS[-i]) for i in self.im.getdata()
        ]

        # get the actual number representing the converted image
        self.NUMBER = int("".join(self.CONVERTED_IMAGE_DATA))

        # set flag_numberised to true
        self.flag_numberised = True

        if self.VERBOSE:
            self.show()
            print(self.show_number())

    def show_number(self):
        """Numberise the image and print the resulting number accordingly.
        """
        # numberise if haven't already
        if not self.flag_numberised:
            self.numberise()

        result = ""
        for index, digit in enumerate(self.CONVERTED_IMAGE_DATA):

            # take a line break after we reach the width of the image
            if index % self.width == 0 and index > 0:
                result += "\n"

            result += str(digit)

        return result

    def read_number(self):
        with open(self.START_PATH, 'r') as f:
            lines = f.read()
            print(lines)
            self.width = lines.index('\n')
            num = int(lines.replace('\n', ''))
            return num

    def find_next_prime(self):
        """We use sympy's nextprime() to find the next biggest prime

        description:
            Note that by the prime number theorem for a number of order e^n
            we expect every log(n) number following our number to be prime.
            So finding the prime should not be difficult, especially since
            primality testing is quick.
        """
        # numberise if haven't already
        if self.IMAGE_PATH:
            self.numberise()
        else:
            print('Starting from:')
            self.NUMBER = self.read_number()

        # find prime only if we haven't already
        if self.flag_primed:
            return 0

        self.prime = 0 + self.NUMBER

        self.expected = int(self.MAX_DIGITS * 2.3/3)

        if self.VERBOSE:
            print(
                f"""Starting search for prime.
Note that in this instance we would expect to run
about {self.expected} primality tests."""
            )

        # self.prime = nextprime(self.prime)
        (self.prime, self.total) = next_prime(self.prime, self.expected, self.PARALLEL)

        if self.VERBOSE:
            print("Found!")
            print(f"Did {self.total} primality tests")

        # set primed flag to true
        self.flag_primed = True

    def get_prime(self):
        """Converts the image into a prime number

        description:
            The prime number is stored at self.prime
            and the formated string at self.prime_string.
        """

        # first we find the next prime
        self.find_next_prime()

        # now we create the prime string
        self.prime_string = ""

        for index, digit in enumerate(str(self.prime)):

            # take a line break after we reach the width of the image
            if index % self.width == 0 and index > 0:
                self.prime_string += "\n"

            self.prime_string += str(digit)

    def create_prime(self):
        """Wraps all the methods to generate a file containing your primed picture

        description:
            Turns the picture that the class has been initialized with
            into a prime which it outputs into a text file.

        """

        # start the search for the prime
        self.get_prime()

        # print it to the output file
        with open(self.output_file_path, "w") as f:
            print(self.prime_string, file=f)

            if self.VERBOSE:
                print(self.prime_string)
