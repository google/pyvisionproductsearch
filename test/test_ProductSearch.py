import unittest
import sys
from googleproductsearch.ProductSearch import ProductSearch, ProductCategories
from random import randint
import os

LOCATION = "us-west1"
CREDS = "key.json"
PROJECTID = "mismatch"
BUCKET = "mismatch-test"


class ProductSearchTest(unittest.TestCase):
    def setUp(self):
        self.productSearch = ProductSearch(PROJECTID, LOCATION, CREDS, BUCKET)
        self.setName = "test-" + str(randint(0, 10000))
        self.productSet = self.productSearch.createProductSet(self.setName)
        self.productName = "fakeProduct-" + str(randint(0, 100000))
        self.product = self.productSearch.createProduct(self.productName, ProductCategories.APPAREL)

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
            print(pSet.name)
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
        assert product.productId
        products = self.productSearch.listProducts()
        assert any([product.productId == x.productId for x in products])
        product.delete()
    
    def test_ReferenceImages(self):
        imgPath = os.path.join(os.path.dirname(__file__), './data/skirt.jpg')
        imgName = self.product.addReferenceImage(imgPath)
        images = self.product.listReferenceImages()
        assert len(images)
        assert all(images)
        url = self.product.getReferenceImageUrl(imgName)
        print(url)
        self.product.deleteReferenceImage(imgName)

    def tearDown(self):
        """Call after every test case."""
        self.productSet.delete()
        self.product.delete()


if __name__ == '__main__':
    unittest.main()