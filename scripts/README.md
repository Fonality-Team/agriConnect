# AgriConnect Database Seeding Scripts

This directory contains utility scripts for populating the AgriConnect database with test data.

## Scripts

### seed_data.py
Populates the database with test data including:
- 10 categories (Fruits, Vegetables, Grains, etc.)
- 10 test farmer users
- 50 products with realistic names, descriptions, and prices
- Product images and price history
- 1 admin user

**Usage:**
```bash
cd /home/ivantana/Projects/agriConnect
python scripts/seed_data.py
```

**Test Credentials:**
- Admin: admin@agriconnect.com / admin123
- Farmers: farmer_john@farm.com / password123 (and 9 others)

### clear_data.py
Removes all test data from the database (useful for development).

**Usage:**
```bash
cd /home/ivantana/Projects/agriConnect
python scripts/clear_data.py
```

## Running the Scripts

1. Make sure your Flask application is properly configured
2. Ensure database migrations are up to date:
   ```bash
   flask db upgrade
   ```
3. Run the seeding script:
   ```bash
   python scripts/seed_data.py
   ```

## Notes

- The scripts use the application context to ensure proper database connections
- Products are assigned random prices within realistic ranges
- Price history includes random price changes for some products
- All test data is clearly identifiable for easy cleanup

## Development Workflow

1. **Initial setup:** Run `seed_data.py` to populate with test data
2. **Development:** Use the test data to develop and test features
3. **Reset:** Run `clear_data.py` when you need a clean slate
4. **Re-populate:** Run `seed_data.py` again with fresh test data
