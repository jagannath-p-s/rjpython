from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace 'your_secret_key' with a secret key of your choice

# Supabase credentials
SUPABASE_URL = 'https://smfonqblavmkgmcylqoc.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNtZm9ucWJsYXZta2dtY3lscW9jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTIxMjI0MjQsImV4cCI6MjAyNzY5ODQyNH0.Yk9jlcLu2Svi8cAsQLuMJHflvBqbtusICyNj2ZfrVZg'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = supabase.auth.sign_in(email=email, password=password)
        if user['user']:
            session['user'] = user['user']
            return redirect('/dashboard')
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')
    else:
        if 'user' in session:
            return redirect('/dashboard')
        else:
            return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        # Fetch customers data
        customers = get_customers()
        return render_template('index.html', customers=customers)
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

def get_customers():
    try:
        customers = supabase.table('customers').select("*").execute()
        return customers.data
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
