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

from google.cloud import vision
from google.cloud import storage
from uuid import uuid4 as uuid
import os


class ProductCategories:
    HOMEGOODS = "homegoods-v2"
    APPAREL = "apparel-v2"
    TOYS = "toys-v2"
    PACKAGEDGOODS = "packagedgoods-v1"
    GENERAL = "general-v1"


class ProductSearch:
    def __init__(self, project_id, location, creds_file, bucket_name, storage_prefix=None):
        self.projectId = project_id
        self.location = location
        self.productClient = vision.ProductSearchClient.from_service_account_json(
            creds_file)
        self.imageClient = vision.ImageAnnotatorClient.from_service_account_file(
            creds_file)
        self.locationPath = self.productClient.location_path(
            project=project_id, location=location)
        self.storageClient = storage.Client.from_service_account_json(
            creds_file)
        self.bucket = self.storageClient.bucket(bucket_name)
        self.prefix = storage_prefix

    # Product

    class Product:
        def __init__(self, product_search, category, display_name, labels, product_path):

            self.productSearch = product_search
            self.category = category
            self.displayName = display_name
            self.labels = labels
            self.productPath = product_path
            self.deleted = False

        @staticmethod
        def _fromResponse(product_search, res):
            return ProductSearch.Product(product_search, res.product_category, res.display_name, res.product_labels, res.name)

        def _checkDeleted(self):
            if self.deleted:
                raise Exception(
                    "Cannot perform operation on already deleted product")

        def delete(self):
            self._checkDeleted()
            self.productSearch.productClient.delete_product(self.productPath)
            self.deleted = True

        def addReferenceImage(self, filename, bounding_polys=None):
            # TODO: Add bounding polys
            imageId = str(uuid())
            search = self.productSearch
            bucket = search.bucket
            blob = bucket.blob(
                imageId if not search.prefix else os.path.join(search.prefix, imageId))
            blob.upload_from_filename(filename)
            blob.make_public()

            gcs_uri = os.path.join("gs://", bucket.name, blob.name)

            # Create a reference image.
            reference_image = vision.types.ReferenceImage(
                uri=gcs_uri,
                bounding_polys=bounding_polys)

            # The response is the reference image with `name` populated.
            res = search.productClient.create_reference_image(
                parent=self.productPath,
                reference_image=reference_image,
                reference_image_id=imageId)

            return res.name

        def listReferenceImages(self):
            images = self.productSearch.productClient.list_reference_images(
                parent=self.productPath)
            return [x.name for x in images]

        def _getReferenceImageBlobName(self, name):
            refImage = self.productSearch.productClient.get_reference_image(
                name)
            return '/'.join(refImage.uri.split("//")[1].split("/")[1:])

        def getReferenceImageUrl(self, name):
            bucket = self.productSearch.bucket
            blobName = self._getReferenceImageBlobName(name)
            return bucket.blob(blobName).public_url

        def deleteReferenceImage(self, name):
            blobName = self._getReferenceImageBlobName(name)
            self.productSearch.productClient.delete_reference_image(name=name)
            self.productSearch.bucket.blob(blobName).delete()

    def createProduct(self, product_id, category, display_name=None, labels=[]):

        display_name = display_name if display_name else product_id

        product = vision.types.Product(
            display_name=display_name,
            product_category=category,
            product_labels=labels)

        res = self.productClient.create_product(
            parent=self.locationPath,
            product=product,
            product_id=product_id)

        return ProductSearch.Product(self, category, display_name, labels, res.name)

    def listProducts(self):
        response = self.productClient.list_products(parent=self.locationPath)
        return [ProductSearch.Product._fromResponse(self, x) for x in response]

    # ProductSet

    def _getProductSetPath(self, product_set_id):
        return self.productClient.product_set_path(
            project=self.projectId, location=self.location,
            product_set=product_set_id)

    class ProductSet:
        def __init__(self, product_search, name):
            self.productSearch = product_search
            self.productSetPath = product_search._getProductSetPath(name)
            self.name = name
            self.productSet = product_search.productClient.get_product_set(
                name=self.productSetPath)
            self.deleted = False

        def _checkDeleted(self):
            if self.deleted:
                raise Exception(
                    "Can't perform operation on already deleted product set")

        def indexTime(self):
            productSet = self.productSearch.productClient.get_product_set(
                name=self.productSetPath)
            return productSet.index_time

        def delete(self):
            self._checkDeleted()
            # Delete the product set.
            self.productSearch.productClient.delete_product_set(
                name=self.productSetPath)
            self.deleted = True

        def addProduct(self, product):
            self._checkDeleted()
            product._checkDeleted()

            self.productSearch.productClient.add_product_to_product_set(
                name=self.productSetPath, product=product.productPath)

        def removeProduct(self, product):
            self._checkDeleted()
            product._checkDeleted()

            self.productSearch.productClient.remove_product_from_product_set(
                name=self.productSetPath, product=product.productPath)

        def listProducts(self):
            self._checkDeleted()
            response = self.productSearch.productClient.list_products_in_product_set(
                name=self.productSetPath)
            return [ProductSearch.Product._fromResponse(self, x) for x in response]

        def search(self, product_category, file_path=None, image_uri=None, filter=None):
            self._checkDeleted()
            # This little hack checks that exactly one of file_path or image_uri is set
            if bool(file_path) == bool(image_uri):
                raise Exception(
                    "Must provide one of either a file path or an image uri")

            if file_path:
                with open(file_path, 'rb') as image_file:
                    content = image_file.read()
                image = vision.types.Image(content=content)
            else:
                image_source = vision.types.ImageSource(image_uri=image_uri)
                image = vision.types.Image(source=image_source)

            product_search_params = vision.types.ProductSearchParams(
                product_set=self.productSetPath,
                product_categories=[product_category],
                filter=filter)

            image_context = vision.types.ImageContext(
                product_search_params=product_search_params)
            # Search products similar to the image.

            results = self.productSearch.imageClient.product_search(
                image, image_context=image_context).product_search_results.results

            response = []
            for result in results:
                response.append({
                    'product': ProductSearch.Product._fromResponse(self.productSearch, result.product),
                    'score': result.score,
                    'image': result.image
                })
            return response

    def createProductSet(self, name, display_name=None):
        '''
            If display_name is None, just set it to the product set id
        '''
        display_name = name if not display_name else display_name

        # Create a product set with the product set specification in the region.
        product_set = vision.types.ProductSet(
            display_name=display_name)

        # The response is the product set with `name` populated.
        self.productClient.create_product_set(
            parent=self.locationPath,
            product_set=product_set,
            product_set_id=name)

        return ProductSearch.ProductSet(self, name)

    def getProductSet(self, name):
        return ProductSearch.ProductSet(self, name)

    def listProductSets(self):
        res = self.productClient.list_product_sets(parent=self.locationPath)
        return [ProductSearch.ProductSet(self, x.name.split('/')[-1]) for x in res]
