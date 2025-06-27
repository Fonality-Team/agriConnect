# agiConnect Database Documentation

This document describes the database schema for the **agiConnect** application, built using Flask-SQLAlchemy. The database supports connecting farmers and users, allowing farmers to list products with multiple images, provide their location and contact details, and submit KYC (Know Your Customer) verification. The schema consists of nine tables: `users`, `categories`, `products`, `product_images`, `price_history`, `deliveries`, `locations`, `contacts`, and `kyc`.

## Table Overview
- **users**: Stores information about all users (farmers and regular users).
- **categories**: Stores product categories and subcategories (self-referential).
- **products**: Stores details of products listed by farmers for sale.
- **product_images**: Stores multiple image URLs for each product.
- **price_history**: Tracks historical price changes for products.
- **deliveries**: Stores delivery/order information for products.
- **locations**: Stores geolocation data for farmers.
- **contacts**: Stores contact information for farmers.
- **kyc**: Stores KYC verification details for farmers.

## Schema Details

### 1. `users` Table
Stores user accounts, including both farmers and regular users.

| Column Name   | Type         | Constraints                     | Description                                   |
|---------------|--------------|---------------------------------|-----------------------------------------------|
| `id`          | Integer      | Primary Key                     | Unique identifier for the user.               |
| `username`    | String(80)   | Unique, Not Null                | Unique username for the user.                 |
| `email`       | String(120)  | Unique, Not Null                | User's email address.                         |
| `password_hash` | String(128) | Not Null                      | Hashed password for security.                 |
| `role`        | String(20)   | Not Null, Default: 'user'       | Role of the user ('farmer' or 'user').        |
| `created_at`  | DateTime     | Default: UTC now                | Timestamp when the user was created.          |
| `updated_at`  | DateTime     | Default: UTC now, On Update: UTC now | Timestamp when the user was last updated. |

**Relationships**:
- One-to-Many: `users` to `products` (a user can have many products; `farmer_id` in `products`).
- One-to-One: `users` to `locations` (via `user_id` in `locations`).
- One-to-One: `users` to `contacts` (via `user_id` in `contacts`).
- One-to-One: `users` to `kyc` (via `user_id` in `kyc`).

### 2. `categories` Table
Stores product categories and subcategories using a self-referential parent-child relationship.

| Column Name   | Type         | Constraints                     | Description                                   |
|---------------|--------------|---------------------------------|-----------------------------------------------|
| `id`          | Integer      | Primary Key                     | Unique identifier for the category.           |
| `name`        | String(50)   | Unique, Not Null                | Category or subcategory name.                 |
| `description` | Text         | Nullable                        | Description of the category.                  |
| `parent_id`   | Integer      | Foreign Key (`categories.id`), Nullable | If set, points to the parent category (for subcategories). |
| `created_at`  | DateTime     | Default: UTC now                | Timestamp when the category was created.      |

**Relationships**:
- Self-referential: Categories can have subcategories (`parent_id` references `categories.id`).
- One-to-Many: `categories` to `products` (a category or subcategory can have many products).

### 3. `products` Table
Stores products listed by farmers for sale.

| Column Name   | Type         | Constraints                     | Description                                   |
|---------------|--------------|---------------------------------|-----------------------------------------------|
| `id`          | Integer      | Primary Key                     | Unique identifier for the product.            |
| `name`        | String(100)  | Not Null                        | Name of the product.                          |
| `description` | Text         | Nullable                        | Description of the product.                   |
| `price`       | Float        | Not Null                        | Price of the product.                         |
| `image_url`   | String(255)  | Nullable                        | Path or URL to the product image.             |
| `farmer_id`   | Integer      | Foreign Key (`users.id`), Not Null | ID of the farmer who listed the product.     |
| `category_id` | Integer      | Foreign Key (`categories.id`), Not Null | ID of the (sub)category.                    |
| `created_at`  | DateTime     | Default: UTC now                | Timestamp when the product was created.       |
| `updated_at`  | DateTime     | Default: UTC now, On Update: UTC now | Timestamp when the product was last updated. |

**Relationships**:
- Many-to-One: `products` to `users` (via `farmer_id`).
- Many-to-One: `products` to `categories` (via `category_id`).
- One-to-Many: `products` to `product_images` (via `product_id` in `product_images`).

### 4. `product_images` Table
Stores multiple image URLs for each product.

| Column Name   | Type         | Constraints                     | Description                                   |
|---------------|--------------|---------------------------------|-----------------------------------------------|
| `id`          | Integer      | Primary Key                     | Unique identifier for the image.              |
| `product_id`  | Integer      | Foreign Key (`products.id`), Not Null | ID of the associated product.                |
| `image_url`   | String(255)  | Not Null                        | URL or path to the product image.             |
| `created_at`  | DateTime     | Default: UTC now                | Timestamp when the image was added.           |
| `updated_at`  | DateTime     | Default: UTC now, On Update: UTC now | Timestamp when the image was last updated. |

**Relationships**:
- Many-to-One: `product_images` to `products` (via `product_id`).
- Cascade: Deleting a product deletes its associated images (`cascade='all, delete-orphan'`).

### 5. `price_history` Table
Tracks historical price changes for products.

| Column Name   | Type         | Constraints                     | Description                                   |
|---------------|--------------|---------------------------------|-----------------------------------------------|
| `id`          | Integer      | Primary Key                     | Unique identifier for the price record.       |
| `product_id`  | Integer      | Foreign Key (`products.id`), Not Null | ID of the associated product.                |
| `price`       | Float        | Not Null                        | Price of the product at this point in time.   |
| `changed_at`  | DateTime     | Default: UTC now                | Timestamp when the price was recorded.        |

**Relationships**:
- Many-to-One: `price_history` to `products` (via `product_id`).

### 6. `deliveries` Table
Stores delivery/order information for products.

| Column Name        | Type         | Constraints                     | Description                                   |
|--------------------|--------------|---------------------------------|-----------------------------------------------|
| `id`               | Integer      | Primary Key                     | Unique identifier for the delivery.           |
| `product_id`       | Integer      | Foreign Key (`products.id`), Not Null | ID of the product being delivered.         |
| `customer_id`      | Integer      | Foreign Key (`users.id`), Not Null | ID of the customer receiving the product.   |
| `farmer_id`        | Integer      | Foreign Key (`users.id`), Not Null | ID of the farmer sending the product.       |
| `delivery_address` | String(255)  | Not Null                        | Address for delivery.                         |
| `delivery_status`  | String(50)   | Not Null, Default: 'pending'     | Status: 'pending', 'shipped', 'delivered', etc. |
| `order_date`       | DateTime     | Default: UTC now                | When the order was placed.                    |
| `delivery_date`    | DateTime     | Nullable                        | When the product was delivered.               |
| `created_at`       | DateTime     | Default: UTC now                | Timestamp when the delivery record was created.|
| `updated_at`       | DateTime     | Default: UTC now, On Update: UTC now | Timestamp when the record was last updated. |

**Relationships**:
- Many-to-One: `deliveries` to `products` (via `product_id`).
- Many-to-One: `deliveries` to `users` as customer (via `customer_id`).
- Many-to-One: `deliveries` to `users` as farmer (via `farmer_id`).

### 7. `locations` Table
Stores geolocation data for farmers.

| Column Name   | Type         | Constraints                     | Description                                   |
|---------------|--------------|---------------------------------|-----------------------------------------------|
| `id`          | Integer      | Primary Key                     | Unique identifier for the location.           |
| `user_id`     | Integer      | Foreign Key (`users.id`), Not Null, Unique | ID of the associated farmer.                 |
| `latitude`    | Float        | Not Null                        | Latitude coordinate of the farmer's location. |
| `longitude`   | Float        | Not Null                        | Longitude coordinate of the farmer's location. |
| `address`     | String(255)  | Nullable                        | Optional full address of the farmer.          |
| `created_at`  | DateTime     | Default: UTC now                | Timestamp when the location was added.        |
| `updated_at`  | DateTime     | Default: UTC now, On Update: UTC now | Timestamp when the location was last updated. |

**Relationships**:
- One-to-One: `locations` to `users` (via `user_id`).

### 8. `contacts` Table
Stores contact information for farmers.

| Column Name   | Type         | Constraints                     | Description                                   |
|---------------|--------------|---------------------------------|-----------------------------------------------|
| `id`          | Integer      | Primary Key                     | Unique identifier for the contact.            |
| `user_id`     | Integer      | Foreign Key (`users.id`), Not Null, Unique | ID of the associated farmer.                 |
| `phone`       | String(20)   | Nullable                        | Farmer's phone number.                        |
| `email`       | String(120)  | Nullable                        | Farmer's contact email.                       |
| `whatsapp`    | String(20)   | Nullable                        | Farmer's WhatsApp number.                     |
| `created_at`  | DateTime     | Default: UTC now                | Timestamp when the contact was added.         |
| `updated_at`  | DateTime     | Default: UTC now, On Update: UTC now | Timestamp when the contact was last updated. |

**Relationships**:
- One-to-One: `contacts` to `users` (via `user_id`).

### 9. `kyc` Table
Stores KYC verification details for farmers.

| Column Name       | Type         | Constraints                     | Description                                   |
|-------------------|--------------|---------------------------------|-----------------------------------------------|
| `id`              | Integer      | Primary Key                     | Unique identifier for the KYC record.         |
| `user_id`         | Integer      | Foreign Key (`users.id`), Not Null, Unique | ID of the associated farmer.                 |
| `document_type`   | String(50)   | Not Null                        | Type of document (e.g., ID card, passport).   |
| `document_number` | String(50)   | Not Null                        | Document number.                              |
| `document_image_url` | String(255) | Nullable                     | URL or path to the uploaded document image.   |
| `status`          | String(20)   | Not Null, Default: 'pending'    | Verification status ('pending', 'verified', 'rejected'). |
| `submitted_at`    | DateTime     | Default: UTC now                | Timestamp when the KYC was submitted.         |
| `updated_at`      | DateTime     | Default: UTC now, On Update: UTC now | Timestamp when the KYC was last updated.     |

**Relationships**:
- One-to-One: `kyc` to `users` (via `user_id`).

## Relationships Diagram
```
[Users]
  |
  | 1:N
[Products]
  | 1:N
[ProductImages]
  | 1:N
[PriceHistory]
  | 1:N
[Deliveries]
      |
      | N:1
  [Categories]
      |
      | self-ref (parent_id)
  [Categories]
```
- **1:N (One-to-Many)**: One user (farmer) can have multiple products, one product can have multiple images, price history records, and deliveries. One category can have multiple subcategories and products.
- **Self-referential**: Categories can have subcategories via `parent_id`.
- **Deliveries**: Each delivery links a product, a customer, and a farmer (all users).

## Notes
- **Database Engine**: The application uses SQLite (`sqlite:///agiconnect.db`) for development, but can be configured for other databases (e.g., PostgreSQL, MySQL) by updating the `SQLALCHEMY_DATABASE_URI` in `app.py`.
- **File Storage**: Product images (`product_images.image_url`) and KYC documents (`kyc.document_image_url`) are stored as URLs or file paths, currently managed by the `LocalFileUpload` service in `static/uploads`.
- **Security**: Passwords in the `users` table are hashed using Werkzeug's `generate_password_hash`. Ensure proper validation and sanitization for file uploads and user inputs.
- **Cascading Deletes**: The `product_images` table uses `cascade='all, delete-orphan'` to ensure images are deleted when their associated product is deleted.

## Usage
- **Farmers**: Register as users with `role='farmer'`, submit KYC details, add location and contact information, and list products with multiple images.
- **Users**: Register with `role='user'` to view products and farmer details.
- **KYC Verification**: Admins can review `kyc` records and update the `status` field.
- **File Uploads**: Use the `LocalFileUpload` service to upload product images and KYC documents, storing URLs in the respective tables.

This schema supports the core functionality of **agiConnect**, enabling scalable and organized data management for farmers and users.
