from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            field_names = df.columns.tolist()
            return render_template('result.html', field_names=field_names)
        else:
            return "Please upload a valid Excel file (xlsx)."

@app.route('/generate_sql', methods=['POST'])
def generate_sql():
    if request.method == 'POST':
        field_names = request.form.getlist('field_names')
        table_name = request.form['table_name']
        sql_script = generate_sql_table(field_names, table_name)
        return render_template('sql_result.html', sql_script=sql_script)

def generate_sql_table(field_names, table_name='your_table_name'):
    sql_script = f"CREATE TABLE {table_name} (\n"
    for field in field_names:
        sql_script += f"\t{field} VARCHAR(255),\n"  # Assuming all fields are of VARCHAR type with max length 255, you can adjust this based on your actual data
    sql_script = sql_script.rstrip(",\n") + "\n);"  # Remove the last comma and newline, and add closing parenthesis
    return sql_script

if __name__ == '__main__':
    app.run(debug=True)
