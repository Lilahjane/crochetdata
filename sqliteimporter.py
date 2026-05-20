import sqlite3
import csv
import os

def create_database():
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect('hbyarninfo.db')
    cursor = conn.cursor()
    
    # Create price_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            product_id TEXT,
            product_name TEXT,
            current_price REAL,
            original_price REAL,
            discounted_price REAL,
            on_sale INTEGER,
            last_modified_at TEXT
        )
    ''')
    
    # Create products_master table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_master (
            product_id TEXT,
            product_key TEXT,
            object_id TEXT,
            display_sku TEXT,
            product_name TEXT,
            display_name TEXT,
            brand TEXT,
            lowest_original_price REAL,
            highest_original_price REAL,
            lowest_price REAL,
            highest_price REAL,
            lowest_discounted_price REAL,
            highest_discounted_price REAL,
            in_stock INTEGER,
            is_new INTEGER,
            on_sale INTEGER,
            availability TEXT,
            active_variant_count INTEGER,
            fiber TEXT,
            yarn_weight TEXT,
            yarn_content TEXT,
            color_family TEXT,
            content TEXT,
            color_code TEXT,
            knitting_needles TEXT,
            knit_gauge TEXT,
            crochet_hook TEXT,
            crochet_gauge TEXT,
            skein_weight TEXT,
            skein_yardage TEXT,
            quantity INTEGER,
            care_instructions TEXT,
            department TEXT,
            category TEXT,
            subcategory TEXT,
            rating_average REAL,
            rating_count INTEGER,
            product_url TEXT,
            image_url TEXT,
            description TEXT,
            days_online INTEGER,
            last_modified_at TEXT
        )
    ''')
    
    # Create search_metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_metadata (
            product_id TEXT,
            product_name TEXT,
            brand TEXT,
            fiber TEXT,
            yarn_weight TEXT,
            department TEXT,
            category TEXT,
            subcategory TEXT,
            color_family TEXT,
            keywords TEXT,
            availability TEXT,
            on_sale INTEGER,
            in_stock INTEGER,
            is_new INTEGER
        )
    ''')
    
    # Create yarns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS yarns (
            sku TEXT,
            product_key TEXT,
            price REAL,
            url TEXT,
            image TEXT,
            brand TEXT,
            color TEXT,
            color_family TEXT,
            fiber TEXT,
            yarn_weight TEXT,
            description TEXT
        )
    ''')
    
    conn.commit()
    return conn

def import_csv_to_table(conn, csv_filename, table_name):
    """Import CSV file into specified table"""
    
    if not os.path.exists(csv_filename):
        print(f"Warning: {csv_filename} not found. Skipping...")
        return False
    
    cursor = conn.cursor()
    
    # Read CSV file
    with open(csv_filename, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Skip header row
        
        # Clean up headers (remove BOM if present)
        headers = [h.strip().replace('\ufeff', '') for h in headers]
        
        # Prepare placeholders for SQL query
        placeholders = ','.join(['?' for _ in headers])
        
        # Build INSERT query
        insert_query = f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({placeholders})"
        
        # Insert rows
        rows_inserted = 0
        for row in csv_reader:
            try:
                # Clean up row data
                clean_row = [None if cell == '' else cell for cell in row]
                
                # Convert numeric fields if needed
                # (SQLite handles type affinity automatically)
                cursor.execute(insert_query, clean_row)
                rows_inserted += 1
            except Exception as e:
                print(f"Error inserting row in {table_name}: {e}")
                print(f"Row data: {row[:5]}...")  # Show first 5 columns for debugging
        
        conn.commit()
        print(f"Imported {rows_inserted} rows into {table_name}")
        return True

def verify_database(conn):
    """Verify that all tables were created and have data"""
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n=== Database Verification ===")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Table '{table_name}': {count} rows")
        
        # Show column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"  Columns: {', '.join([col[1] for col[:3] in columns])}...")

def main():
    print("Starting database creation and import...")
    
    # Create database and tables
    conn = create_database()
    print("✓ Database and tables created successfully")
    
    # Define CSV files and their corresponding tables
    csv_mappings = [
        ('price_history.csv', 'price_history'),
        ('products_master.csv', 'products_master'),
        ('search_metadata.csv', 'search_metadata'),
        ('yarns.csv', 'yarns')
    ]
    
    # Import each CSV file
    print("\n=== Importing CSV files ===")
    for csv_file, table_name in csv_mappings:
        print(f"\nImporting {csv_file} into {table_name}...")
        import_csv_to_table(conn, csv_file, table_name)
    
    # Verify the database
    verify_database(conn)
    
    # Close connection
    conn.close()
    print("\n✓ Database 'hbyarninfo.db' has been created and populated successfully!")

def query_examples():
    """Example queries to test the database"""
    conn = sqlite3.connect('hbyarninfo.db')
    cursor = conn.cursor()
    
    print("\n=== Example Queries ===")
    
    # Example 1: Get all yarns on sale
    print("\n1. Yarns currently on sale:")
    cursor.execute("""
        SELECT product_name, current_price, original_price 
        FROM price_history 
        WHERE on_sale = 1 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: ${row[1]} (was ${row[2]})")
    
    # Example 2: Get yarns by brand
    print("\n2. Yarn brands in database:")
    cursor.execute("""
        SELECT DISTINCT brand, COUNT(*) as count 
        FROM products_master 
        WHERE brand IS NOT NULL 
        GROUP BY brand 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} products")
    
    # Example 3: Search for wool yarns
    print("\n3. Wool yarns available:")
    cursor.execute("""
        SELECT product_name, brand, fiber 
        FROM products_master 
        WHERE fiber LIKE '%wool%' AND in_stock = 1
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} by {row[1]} - {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    main()
    
    # Uncomment to run example queries
    # query_examples()
