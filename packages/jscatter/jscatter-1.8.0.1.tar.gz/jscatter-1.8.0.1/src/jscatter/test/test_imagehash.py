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
import unittest
import os.path
from ..libs.imagehash import imageHash


class TestimageHash(unittest.TestCase):

    def check_hash_algorithm(self, image, type):
        original_hash = imageHash(image=image, type=type)
        rotate_image = image.rotate(-1)
        rotate_hash = imageHash(image=rotate_image, type=type)
        similarity = original_hash.similarity(rotate_hash)
        emsg = ('slightly rotated image should have '
                'similar hash {} {} {}'.format(original_hash, rotate_hash, similarity))
        self.assertTrue(similarity <= 0.1, emsg)
        rotate_image = image.rotate(-90)
        rotate_hash = imageHash(image=rotate_image, type=type)
        emsg = ('rotated image should have different '
                'hash {} {}'.format(original_hash, rotate_hash))
        self.assertNotEqual(original_hash, rotate_hash, emsg)
        similarity = original_hash.similarity(rotate_hash)
        emsg = ('rotated image should have larger different '
                'hash {} {} {}'.format(original_hash, rotate_hash, similarity))
        self.assertTrue(similarity > 0.1, emsg)

    def check_hash_length(self, image, type, sizes=range(2, 21, 1)):
        for hash_size in sizes:
            image_hash = imageHash(image=image, type=type, hashsize=hash_size)
            emsg = 'hashsize={} is not respected'.format(hash_size)
            self.assertEqual(image_hash.hash.size, hash_size ** 2, emsg)

    def check_hash_stored(self, image, type, sizes=range(2, 21, 1)):
        for hash_size in sizes:
            image_hash = imageHash(image=image, type=type, hashsize=hash_size)
            other_hash = imageHash(image_hash.hex, type=image_hash.hashtype)
            emsg = 'hash size {}: stringified hash {} != original hash {}'.format(hash_size,
                                                                                  other_hash, image_hash)
            self.assertEqual(image_hash, other_hash, emsg)
            distance = image_hash - other_hash
            emsg = ('unexpected hamming distance {}: original hash {} '
                    '- stringified hash {} --- hash size {}: '.format(distance, image_hash,
                                                                      other_hash, hash_size))
            self.assertEqual(distance, 0, emsg)

    def check_hash_size(self, image, type, sizes=range(-1, 2)):
        for hash_size in sizes:
            with self.assertRaises(ValueError):
                imageHash(image=image, type=type, hashsize=hash_size)


class allimageHashTest(TestimageHash):
    def setUp(self):
        self.image = Image.open(os.path.dirname(__file__) + '/contourImage.jpg')

    def test_hash(self):
        self.check_hash_algorithm(image=self.image, type='ahash')
        self.check_hash_algorithm(image=self.image, type='dhash')
        self.check_hash_algorithm(image=self.image, type='phash')

    def test_length(self):
        self.check_hash_length(image=self.image, type='ahash')
        self.check_hash_length(image=self.image, type='dhash', sizes=range(2, 21, 3))
        self.check_hash_length(image=self.image, type='phash', sizes=range(2, 21, 3))

    def test_stored(self):
        self.check_hash_stored(image=self.image, type='ahash')
        self.check_hash_stored(image=self.image, type='dhash', sizes=range(2, 21, 3))
        self.check_hash_stored(image=self.image, type='phash', sizes=range(2, 21, 3))

    def test_size(self):
        self.check_hash_size(image=self.image, type='ahash')
        self.check_hash_size(image=self.image, type='dhash')
        self.check_hash_size(image=self.image, type='phash')

    def tearDown(self):
        self.image.close()


def doTest(verbosity=1):
    """Do only one test."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(allimageHashTest))
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

    return


if __name__ == '__main__':
    unittest.main()
