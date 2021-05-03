# Vision Product Search Wrapper
This library is a Python wrapper around the [Cloud Vision Product Search Libary](https://cloud.google.com/vision/product-search/docs). It makes this tool easier to use by allowing you to initalize a `ProductSearch` object once with all of your credentials. It's object-oriented, so that you don't have to be constantly ferrying around names and paths and project ids.

## Getting Started

```
from visionproductsearch.ProductSearch import ProductSearch, ProductCategories

# Initialize ProductSearch with your credentials

ps = ProductSearch(`my_gcp_project_id`, 'us-west1', 'path/to/creds.json', 'my_gcp_bucket_name' )

# Create a new product set
productSet = ps.createProductSet('my_test_set')

# Create a new product
product = ps.createProduct('my_fancy_shirt', ProductCategories.APPAREL)

# Add a reference image to a product
product.addReferenceImage('./skirt_pic.jpg')

# List all reference images for a product
for img in product.listReferenceImages():
    print(img)

# Add a product to a product set
productSet.addProduct(product)

# List all products in a product set
for p in productSet.listProducts():
    print(p)

# Search for similar products by image
productSet.search(ProductCategories.APPAREL, file_path='img/to/search.jpg')

```

Note that this is not a wrapper around _all_ the functions in the Product Search library, but feel free to add them as a contributor!