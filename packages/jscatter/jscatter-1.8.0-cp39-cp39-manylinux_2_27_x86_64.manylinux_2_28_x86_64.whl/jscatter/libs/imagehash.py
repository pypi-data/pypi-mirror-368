# Copyright (c) 2013 Christopher J Pickett, MIT license, https://github.com/bunchesofdonald/photohash
# Copyright (c) 2013-2016, Johannes Buchner, BSD 2-Clause "Simplified"
# License, https://github.com/JohannesBuchner/imagehash
# Copyright (c) 2019, Ralf Biehl, BSD 2-Clause "Simplified" License, https://gitlab.com/biehl/jscatter
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# Redistributions of source code must retain the above copyright notice, this list of conditions 
# and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions 
# and the following disclaimer in the documentation and/or other materials provided with the 
# distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR 
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from PIL import Image
import numpy as np
import scipy.fftpack


class imageHash(object):
    """
    Hash encapsulation. Can be used for dictionary keys and comparisons.
    """

    def __init__(self, image, type=None, hashsize=8, highfreq_factor=4):
        """
        Creates image hash of an image to find duplicates or similar images in a fast way using the Hamming difference.
        
        Implements      
        * average hashing (`aHash`)
        * perception hashing (`pHash`)
        * difference hashing (`dHash`)

        Parameters
        ----------
        image : filename, hexstr, PIL image
            Image to calculate a hash. 
            If a hexstr is given to restore a saved hash it must prepend '0x' and the 0-padded length determines 
            the hash size. type needs to be given additionally.
        type : 'ahash', 'dhash', 'phash'
            Hash type.
        hashsize : int , default 16
            Hash size as hashsize x hashsize array.
        highfreq_factor : int, default=4
            For 'phash' increase initial image size to hashsize*highfreq_factor for cos-transform to
            catch high frequencies.

        Returns imageHash object
            - .bin, .hex, .int return respective representations
            - .similarity(other) returns relative Hamming distance.
            - imageHash subtractions returns Hamming distance.
            - equality checks hashtype and Hamming distance equal zero.

        Notes
        -----
        Images similarity cannot be done by bit comparison (e.g. md5sum) but using a simplified 
        image representation converted to a unique bit representation representing a hash for the image. 

        Similar images should be different only in some bits measured by the Hamming distance 
        (number of different bits).

        A typical procedure is 
         - Reduce color by converting to grayscale.
         - Reduce size to e.g. 8x8 pixels by averaging over blocks.
         - Calc binary pixel hash pased on pixel values:
          - ahash - average hash:  hash[i,j] = pixel > average(pixels)
          - dhash - difference hash: hash[i,j] = pixel[i,j+1] > pixel[i,j] 
          - phash - perceptual hash: 
             The low frequency part of the image cos-transform are most perceptual.
             The cos-transform of the image is used for an average hash.
             hash[i,j] = ahash(cos_tranform(pixels))
          - radial variance: See radon tranform in [1]_ (not implemented)
         - ahash and dhash are faster but phash dicriminates best.
         - Image similarity is decribed by the Hamming difference as number of different bits.
           A good measure is the relative Hamming difference (my similarity) as Hamming_diff/hash.size.
         - Similar images have similarity < 0.1 .
         - Random pixel difference results in  similarity=0.5, an iverted image in similarity =1 (all bits different)


        Examples
        --------
        The calibration image migth be not the best choice as demo or a good one. 
        rotate works not at the center of the beam but for the image center.
        ::

            import jscatter as js
            from jscatter.formel import imageHash
            from PIL import Image
            image = Image.open(js.examples.datapath+'/calibration.tiff')
            type='dhash'
            original_hash = imageHash(image=image, type=type)
            rotate_image = image.rotate(-1) 
            rotate_hash = imageHash(image=rotate_image,type=type)
            sim1 = original_hash.similarity(rotate_hash)
            
            rotate_image = image.rotate(-90)
            rotate_hash = imageHash(image=rotate_image, type=type)
            sim2 = original_hash.similarity(rotate_hash)



        References
        ----------
        .. [1] Rihamark: perceptual image hash benchmarking
               C. Zauner, M. Steinebach, E. Hermann
               Proc. SPIE 7880, Media Watermarking, Security, and Forensics III
               https://doi.org/10.1117/12.876617


        Started based on photohash and imagehash

        Copyright (c) 2013 Christopher J Pickett, MIT license,
        https://github.com/bunchesofdonald/photohash

        Copyright (c) 2013-2016, Johannes Buchner, BSD 2-Clause "Simplified" License,
        https://github.com/JohannesBuchner/imagehash

        Copyright (c) 2019, Ralf Biehl, BSD 2-Clause "Simplified" License, imagehash.py see
        https://gitlab.com/biehl/jscatter/tree/master/src/jscatter/libs

        """

        if hashsize < 2:
            raise ValueError("Hash size must be greater than or equal to 2")

        if isinstance(image, str):
            if image[:2] == '0x':
                # is hex string we convert it to a hash
                size = int(np.trunc((len(image[2:]) * 4) ** 0.5))
                binary = np.array([b == '1' for b in '{:0>{width}b}'.format(int(image, 16), width=size * size)])
                self.hash = binary.reshape(size, -1)
                self.image = None
                self.hashtype = type
                return
            else:
                self.image = Image.open(image)
        else:
            self.image = image

        if type == 'ahash':
            self.hash = self._ahash(hashsize)
            self.hashtype = type
        elif type == 'dhash':
            self.hash = self._ahash(hashsize)
            self.hashtype = type
        else:
            # default type == 'phash':
            self.hash = self._phash(hashsize, highfreq_factor)
            self.hashtype = 'phash'
        return

    def __str__(self):
        return self.hex[2:]

    def __repr__(self):
        return repr(self.hash)

    def __sub__(self, other):
        if other is None:
            raise TypeError('Other hash must not be None.')
        if self.hash.size != other.hash.size:
            raise TypeError('imageHashes must be of the same shape.', self.hash.shape, other.hash.shape)
        if self.hashtype != other.hashtype:
            raise TypeError('imageHashes must be of the same type.', self.type, other.type)
        return np.count_nonzero(self.hash.flatten() != other.hash.flatten())

    def __eq__(self, other):
        if other is None:
            return False
        if self.hashtype != other.hashtype:
            return False
        return np.array_equal(self.hash.flatten(), other.hash.flatten())

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # this returns a 8 bit integer, intentionally shortening the information
        return sum([2 ** (i % 8) for i, v in enumerate(self.hash.flatten()) if v])

    def similarity(self, other):
        """
        Relative Hamming difference.

        - Similar <0.1
        - Random pixels are close to 0.5
        - Inverted 1 

        """
        return self.__sub__(other) / (self.shape[0] * self.shape[1])

    @property
    def size(self):
        """
        Size of the hash.
        """
        return self.hash.size

    @property
    def shape(self):
        """
        Shape of the hash.
        """
        return self.hash.shape

    @property
    def bin(self):
        """
        Binary representation
        """
        return '0b' + ''.join(str(b) for b in 1 * self.hash.flatten())

    @property
    def int(self):
        """
        Integer representation
        """
        return int(self.bin, 2)

    @property
    def hex(self):
        """
        Hexadecimal representation
        """
        l = int(np.ceil(self.size // 4))
        hh = hex(self.int)
        return '0x' + hh[2:].rjust(l, '0')

    def _ahash(self, hash_size=8):
        self.image = self.image.convert("L").resize((hash_size, hash_size), Image.LANCZOS)

        # find average pixel value; 'pixels' is an array of the pixel values, ranging from 0 (black) to 255 (white)
        pixels = np.asarray(self.image)
        avg = pixels.mean()

        # create string of bits
        diff = pixels > avg
        # make a hash
        return diff

    def _phash(self, hash_size, highfreq_factor):
        img_size = hash_size * highfreq_factor
        self.image = self.image.convert("L").resize((img_size, img_size), Image.LANCZOS)

        pixels = np.asarray(self.image)
        dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
        dctlowfreq = dct[:hash_size, :hash_size]
        med = np.median(dctlowfreq)
        diff = dctlowfreq > med
        return diff

    def _dhash(self, hash_size):
        self.image = self.image.convert("L").resize((hash_size + 1, hash_size), Image.LANCZOS)

        pixels = np.asarray(self.image)
        # compute differences between columns
        diff = pixels[:, 1:] > pixels[:, :-1]
        return diff


def hex_to_hash(hexstr):
    """
    Convert a stored hash (hex, as retrieved from str(Imagehash))
    back to a Imagehash object.

    Notes:
    1. This algorithm assumes all hashes are bidimensional arrays
       with dimensions hashsize * hashsize.
    2. This algorithm does not work for hashsize < 2.
    """
    hash_size = int(np.sqrt(len(hexstr) * 4))
    binary_array = '{:0>{width}b}'.format(int(hexstr, 16), width=hash_size * hash_size)
    bit_rows = [binary_array[i:i + hash_size] for i in range(0, len(binary_array), hash_size)]
    hash_array = np.array([[bool(int(d)) for d in row] for row in bit_rows])
    return imageHash(hash_array)
