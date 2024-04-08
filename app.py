from flask import Flask, render_template, request
import csv
from supabase import create_client
from postgrest import exceptions

app = Flask(__name__)

# Supabase credentials
SUPABASE_URL = 'https://smfonqblavmkgmcylqoc.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNtZm9ucWJsYXZta2dtY3lscW9jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTIxMjI0MjQsImV4cCI6MjAyNzY5ODQyNH0.Yk9jlcLu2Svi8cAsQLuMJHflvBqbtusICyNj2ZfrVZg'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CUSTOMERS_TABLE_NAME = "customers"
POINTS_TABLE_NAME = "points"

# Define the headers for the CSV data
headers = ['SL NO', 'CUSTOMER CODE', 'ADDRESS1', 'ADDRESS2', 'ADDRESS3', 'ADDRESS4', 'PIN CODE', 'PHONE', 'MOBILE', 'NET WEIGHT', 'LAST SALES DATE']

@app.route('/')
def index():
    customers = get_customers()  # Fetch customers data
    return render_template('index.html', customers=customers)

def get_customers():
    try:
        # Fetch all customers from the "customers" table
        customers = supabase.table(CUSTOMERS_TABLE_NAME).select("*").execute()
        return customers.data
    except exceptions.APIError as e:
        print(f"Error fetching customers: {e}")
        return None

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        for file in files:
            if file.filename == '':
                return render_template('index.html', message='No file selected')
            if file:
                result = handle_uploaded_file(file)
                if result:
                    update_points_table()  # Update points table after inserting data
                    return render_template('index.html', message='Files uploaded successfully')
                else:
                    return render_template('index.html', message='Error inserting data')
        return render_template('index.html', message='No files uploaded')

def handle_uploaded_file(file):
    try:
        csv_reader = csv.reader(file.stream.read().decode("utf-8").splitlines())
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            insert_or_update_row(row)
        return True
    except Exception as e:
        print(f"Error handling file: {e}")
        return False

def insert_or_update_row(row):
    data = dict(zip(headers, row))
    customer_code = data['CUSTOMER CODE']
    try:
        existing_customer = supabase.table(CUSTOMERS_TABLE_NAME).select("*").eq('CUSTOMER CODE', customer_code).execute()
        if existing_customer.data:
            # Update existing customer data
            existing_data = existing_customer.data[0]
            existing_net_weight = float(existing_data['NET WEIGHT'])
            new_net_weight = float(data['NET WEIGHT'])
            data['NET WEIGHT'] = existing_net_weight + new_net_weight
            supabase.table(CUSTOMERS_TABLE_NAME).update(data).eq('CUSTOMER CODE', customer_code).execute()
        else:
            # Insert new customer data
            supabase.table(CUSTOMERS_TABLE_NAME).insert(data).execute()
        return True
    except exceptions.APIError as e:
        print(f"API Error: {e}")
        return False

def update_points_table():
    try:
        customers = supabase.table(CUSTOMERS_TABLE_NAME).select("*").execute()
        for customer in customers.data:
            total_points = int(customer['NET WEIGHT']) // 10
            unclaimed_points = total_points
            data = {
                "CUSTOMER CODE": customer['CUSTOMER CODE'],
                "SL NO": customer['SL NO'],
                "ADDRESS1": customer['ADDRESS1'],
                "ADDRESS2": customer['ADDRESS2'],
                "ADDRESS3": customer['ADDRESS3'],
                "ADDRESS4": customer['ADDRESS4'],
                "PIN CODE": customer['PIN CODE'],
                "PHONE": customer['PHONE'],
                "MOBILE": customer['MOBILE'],
                "TOTAL POINTS": total_points,
                "UNCLAIMED POINTS": unclaimed_points,
                "LAST SALES DATE": customer['LAST SALES DATE']
            }
            supabase.table(POINTS_TABLE_NAME).upsert(data).execute()
    except exceptions.APIError as e:
        print(f"API Error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
