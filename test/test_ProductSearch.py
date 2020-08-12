# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import sys
from pyvisionproductsearch.ProductSearch import ProductSearch, ProductCategories
from random import randint
import os

LOCATION = "us-west1"
CREDS =  "PATH_TO_CREDS_FILE"
PROJECTID = "YOUR_GCP_PROJECT_ID"
BUCKET = "STORAGE_BUCKET_NAME_FOR_STORING_IMAGES"
OLD_PRODUCT_SET = "NAME_OF_EXISTING_PRODUCT_SET"


class ProductSearchTest(unittest.TestCase):
    def setUp(self):
        self.productSearch = ProductSearch(PROJECTID, LOCATION, CREDS, BUCKET)
        self.setName = "test-" + str(randint(0, 10000))
        self.productSet = self.productSearch.createProductSet(self.setName)
        self.productName = "fakeProduct-" + str(randint(0, 100000))
        self.product = self.productSearch.createProduct(self.productName, ProductCategories.APPAREL)
        self.oldProductSet = self.productSearch.getProductSet(OLD_PRODUCT_SET)

    def test_cantCreateEmptySet(self):
        try:
            self.productSearch.createProductSet("")
        except :
            return
        # Fail if the craeteProductSet method didn't throw an error
        assert False

    def test_listProductSets(self):
        productSets = list(self.productSearch.listProductSets())

        for pSet in productSets:
            assert pSet.name 
            assert pSet.productSetPath
            assert pSet.productSearch
        assert any([pSet.name == self.setName for pSet in productSets])

    def test_deleteProductSet(self):
        thisSet = self.productSearch.createProductSet("testSet2")
        thisSet.delete()
        productSets = list(self.productSearch.listProductSets())
        assert not any([pSet.name == "testSet2" for pSet in productSets])

        try:
            thisSet.delete()
        except:
            return
        # Check that you can't delete a set twice
        assert False
    
    def test_createProduct(self):
        productName = "fakeProduct-" + str(randint(0, 100000))
        product = self.productSearch.createProduct(productName, ProductCategories.APPAREL)
        assert product.productPath
        products = self.productSearch.listProducts()
        assert any([product.productPath == x.productPath for x in products])
        product.delete()
    
    def test_addAndListProductToSet(self):
        self.productSet.addProduct(self.product)
        addedProducts = self.productSet.listProducts()
        assert any([x.productPath == self.product.productPath for x in addedProducts])

    def test_ReferenceImages(self):
        imgPath = os.path.join(os.path.dirname(__file__), './data/skirt.jpg')
        imgName = self.product.addReferenceImage(imgPath)
        images = self.product.listReferenceImages()
        assert len(images)
        assert all(images)
        url = self.product.getReferenceImageUrl(imgName)
        self.product.deleteReferenceImage(imgName)
    
    def test_ProductSetIndexTime(self):
        assert self.oldProductSet.indexTime().seconds
        assert self.oldProductSet.indexTime().nanos
    
    def test_ProductSetSearch(self):
        imgPath = os.path.join(os.path.dirname(__file__), './data/skirt.jpg')
        res = self.oldProductSet.search(ProductCategories.APPAREL, file_path=imgPath)
        for item in res:
            print(item['product'].getReferenceImageUrl(item['image']))

    def tearDown(self):
        """Call after every test case."""
        self.productSet.delete()
        self.product.delete()


if __name__ == '__main__':
    unittest.main()