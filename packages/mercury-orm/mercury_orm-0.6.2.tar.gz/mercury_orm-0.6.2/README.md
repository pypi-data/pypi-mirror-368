# Mercury (ORM Zendesk CustomObjects)

Mercury is a Python ORM (Object-Relational Mapping) designed to integrate seamlessly with the Zendesk Custom Objects API. It provides a Django-like interface for defining, managing, and interacting with Zendesk custom objects and records, simplifying the communication with Zendesk's API.

## Key Features

-   **Custom Object Representation**: Define Zendesk custom objects using Python classes.
-   **Automatic Record Management**: Built-in methods for creating, reading, updating, and deleting records via Zendesk's API.
-   **Support for All Field Types**: Compatible with all Zendesk custom field types including name, text, dropdown, checkbox, date, integer, and more.
-   **Automatic Object Creation**: Automatically create Zendesk custom objects and fields from Python class definitions.
-   **Easy Record Operations**: Simple API to manage custom object records, with built-in support for querying, filtering, and pagination.
-   **Support field Name autoincrement and unique constraint**: Supports automatic field name incrementation and enforcement of unique constraints.

## Installation

```bash
pip install mercury-orm
# add variables in .env or:
export ZENDESK_SUBDOMAIN=<your_zendesk_subdomain>.
export ZENDESK_API_TOKEN=<your_zendesk_api_token>.
export ZENDESK_EMAIL=<your_zendesk_email>.
```

## Field Types
Mercury supports various field types, allowing customization of your Zendesk custom objects:
- **TextField:** For short text data (e.g., names, codes)
- **TextareaField:** For longer text content (e.g., descriptions)
- **CheckboxField:** Boolean fields for toggles or binary states
- **DateField:** Date values represented as strings
- **IntegerField:** Numeric values for counting or indexing
- **DecimalField:** Precise decimal values for prices, percentages, etc.
- **DropdownField:** Predefined selectable options
- **MultiselectField:** Multiple selectable options
- **RegexpField:** Regular expressions for pattern matching
- **LookupField:** Establish relationships with other custom objects
- **NameField:** Specialized text field with options for either uniqueness or auto-incrementation (cannot be used simultaneously)

## CRUD Operations with Records

Mercury ORM provides simple methods for performing CRUD (Create, Read, Update, Delete) operations on Zendesk custom object records. Below are examples of how to manage records in your custom objects.

### Creating a CustomObjects

```python
class Product(CustomObject):
    #name = fields.NameField(unique=True)
    name = fields.NameField(autoincrement_enabled=True, autoincrement_prefix="PROD_", autoincrement_padding=5, autoincrement_next_sequence=10)
    code = fields.TextField("code")
    description = fields.TextareaField("description")
    price = fields.DecimalField("price")
    active = fields.CheckboxField("active")
    voltage = fields.DropdownField("voltage", choices=["220", "110", "Bivolt"])
```

### Creating a Custom Object and Fields in Zendesk

Once you define the custom object class, you can create it in Zendesk using ZendeskObjectManager. This will automatically create the custom object and its fields in Zendesk.

```python
from mercuryormc.zendesk_manager import ZendeskObjectManager

# Create the custom object and fields in Zendesk
manager = ZendeskObjectManager()
manager.create_custom_object_from_model(Product)
# or
manager.get_or_create_custom_object_from_model(Product)
```

### Record Manager

Each custom object class is automatically assigned a RecordManager that handles interaction with the Zendesk API. The RecordManager allows you to:

-   Create records: `Product.objects.create(**kwargs)`
-   Get a single record: `Product.objects.get(id=1)`
-   Filter records: `Product.objects.filter(active=True)`
-   Delete records: `Product.objects.delete(id=1)`
-   Retrieve all records: `Product.objects.all()`
-   Search all records: `Product.objects.search(word="something")`
-   Find records: `Product.objects.find(filters=filters)`
-   Find records with pagination: `Product.objects.find_paginated(filters=filters)`

### Creating a Record

You can create a new record by instantiating your custom object and calling the `save()` method:

```python
product = Product(name="Sample Product", code="12345", price=99.99, active=True)
product.save()

#or
Product.objects.create(name="Sample Product", code="12345", price=99.99, active=True)
```

### Retrieving a Record

You can retrieve an individual record by using the get() method:

```python
retrieved_product = Product.objects.get(id=product.id)
```

### Updating a Record

To update a record, modify its attributes and call the save() method again:

```python
retrieved_product.price = 89.99
retrieved_product.save()
```

### Deleting a Record

To delete a record from Zendesk, call the delete() method on the object:

```python
retrieved_product.delete()
```

## Querying and Filtering Records

You can retrieve all records or filter them based on certain criteria.

```python
all_products = Product.objects.all()
filtered_products = Product.objects.filter(active=True)
last_object = Product.objects.last()
find_products = Products.objects.find(filters=filters)
find_products_paginated = Products.objects.find_paginated(filters=filters)
```

## Find Method Explanation

The `find` method is based on Zendesk's filtering options for custom objects. It allows filtering records using logical operators and comparison operators.

### Supported Logical Operators

-   **`$or`**
-   **`$and`**

### Supported Comparison Operators

#### Custom Fields:

Custom objects have the following types of custom fields that you can filter on:

| Field Type          | Supported Operators                                                       | Meaning (in same order)                                                   |
| ------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Checkbox            | `$eq`                                                                     | is                                                                        |
| Date                | `$eq`, `$noteq`, `$gt`, `$gte`, `$lt`, `$lte`, `$exists`                  | is, is not, after, after or on, before, before or on, present, in range   |
| Decimal             | `$eq`, `$noteq`, `$gt`, `$gte`, `$lt`, `$lte`, `$exists`, `$in`, `$notin` | is, is not, after, after or on, before, before or on, present, in, not in |
| Drop-down           | `$eq`, `$noteq`, `$contains`, `$notcontains`, `$exists`                   | is, is not, contains, not contained, present                              |
| Integer             | `$eq`, `$noteq`, `$gt`, `$gte`, `$lt`, `$lte`, `$exists`, `$in`, `$notin` | is, is not, after, after or on, before, before or on, present, in, not in |
| Lookup Relationship | `$eq`, `$noteq`, `$exists`                                                | is, is not, present                                                       |
| Multi-line text     | `$eq`, `$noteq`, `$contains`, `$notcontains`, `$exists`                   | is, is not, contains, not contained, present                              |
| Multi-select        | `$eq`, `$noteq`, `$contains`, `$notcontains`, `$exists`, `$in`, `$notin`  | is, is not, contains, not contained, present, in, not in                  |
| Text                | `$eq`, `$noteq`, `$contains`, `$notcontains`, `$exists`                   | is, is not, contains, not contained, present                              |

---

#### Standard Fields

Custom objects have the following standard fields that you can filter on:

| Field Type        | Supported Operators | Meaning (in same order)    |
| ----------------- | ------------------- | -------------------------- |
| `created_at`      | `$gt`               | after                      |
| `created_by_user` | `$eq`               | is equal to a user ID      |
| `external_id`     | `$eq`               | is equal to an external ID |
| `name`            | `$contains`         | contains                   |
| `updated_at`      | `$gt`               | after                      |
| `updated_by_user` | `$eq`               | is equal to a user ID      |

### Filter Examples

#### Single Comparison

```python
filters = {
    {"custom_object_fields.price": {"$eq": "12"}}
}
```

In this case, records where the field named `price` is equal to **12** will be returned.

#### OR Comparison

```python
filters = {
    "$or": [
        {"name": {"$contains": "value"}},
        {"updated_at": {"$gt": "2024-12-13"}}
    ]
}
```

In this case, records where the `name` contains **value** or `updated_at` is greater than **2024-12-13** will be returned

#### AND Comparison

```python
filters = {
    "$and": [
        {"name": {"$contains": "value"}},
        {"updated_at": {"$gt": "2024-12-13"}}
    ]
}
```

In this case, records where the `name` contains **value** and `updated_at` is greater than **2024-12-13** will be returned.

#### Combined OR and AND Comparison

```python
filters = {
    "$or": [
        {"name": {"$contains": "value"}},
        {"updated_at": {"$gt": "2024-12-13"}}
    ],
    "$and":[
        {"custom_object_fields.price": {"$eq": "12"}},
        {"custom_object_fields.origin": {"$eq": "BR"}}
    ]
}
```

In this case, records matching the `OR` conditions (`name` contains **value** or `updated_at` is greater than **2024-12-13**) and the `AND` conditions (`price` equals **12** and `origin` equals **BR**) will be returned.

For more information, visit: [Zendesk Documentation](https://developer.zendesk.com/documentation/custom-data/v2/searching-custom-object-records/)
