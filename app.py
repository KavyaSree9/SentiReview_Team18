from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import BytesIO
from fpdf import FPDF  # Import FPDF for PDF generation
import base64
app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy data for visualizations
data = {
    'category': ['Positive', 'Neutral', 'Negative'],
    'counts': [20, 50, 30],
}

# Sample sales data for graphs
sales_data = {
    'month': ['January', 'February', 'March', 'April', 'May'],
    'sales': [200, 300, 250, 400, 500],
    'visitors': [150, 200, 175, 300, 350],
    'revenue': [1000, 1500, 1250, 2000, 2500],
}

# In-memory user storage (for demonstration purposes)
users = {}

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('sign_up'))

        # Store user info (this should be stored in a database in a real app)
        users[username] = {
            'email': email,
            'mobile': mobile,
            'password': password
        }
        flash('Sign up successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('sign_up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check against stored user info
        if username in users and users[username]['password'] == password:
            return redirect(url_for('upload'))  # Redirect to upload page
        else:
            flash('Invalid username or password!')

    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"File uploaded successfully to {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")  # Debug statement
            return redirect(url_for('dashboard'))  # Ensure it redirects to dashboard

    return render_template('upload.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')  # Ensure this template exists

@app.route('/logout')
def logout():
    # Logic to handle logout, e.g., clearing session
    return redirect(url_for('login'))  # Ensure you have a 'login' route

@app.route('/chat')
def chat():
    # Your chat support logic here
    return render_template('chat.html')

@app.route('/dashboard')
def dashboard():
    # Generate visualizations
    sentiment_chart = generate_sentiment_chart()
    sales_chart = generate_sales_chart()
    revenue_chart = generate_revenue_chart()
    visitors_chart = generate_visitors_chart()

    # Encode to base64
    sentiment_chart_b64 = base64.b64encode(sentiment_chart.getvalue()).decode('utf-8')
    sales_chart_b64 = base64.b64encode(sales_chart.getvalue()).decode('utf-8')
    revenue_chart_b64 = base64.b64encode(revenue_chart.getvalue()).decode('utf-8')
    visitors_chart_b64 = base64.b64encode(visitors_chart.getvalue()).decode('utf-8')

    return render_template('dashboard.html',  # Changed to 'dashboard.html'
                           sentiment_chart=sentiment_chart_b64,
                           sales_chart=sales_chart_b64,
                           revenue_chart=revenue_chart_b64,
                           visitors_chart=visitors_chart_b64)


@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/download_report')
def download_report():
    # Generate the PDF report
    pdf_path = create_pdf_report()
    return send_file(pdf_path, as_attachment=True)

def create_pdf_report():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'User Review Sentiment Analysis Report', ln=True, align='C')

    # Add Sentiment Chart
    sentiment_chart = generate_sentiment_chart()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Sentiment Analysis', ln=True)
    pdf.image(sentiment_chart, x=10, y=30, w=180)

    # Add Sales Chart
    sales_chart = generate_sales_chart()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Sales Performance', ln=True)
    pdf.image(sales_chart, x=10, y=30, w=180)

    # Add Revenue Chart
    revenue_chart = generate_revenue_chart()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Revenue Overview', ln=True)
    pdf.image(revenue_chart, x=10, y=30, w=180)

    # Add Visitors Chart
    visitors_chart = generate_visitors_chart()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Visitor Statistics', ln=True)
    pdf.image(visitors_chart, x=10, y=30, w=180)

    # Save the PDF to a temporary file
    pdf_file_path = os.path.join(UPLOAD_FOLDER, "report.pdf")
    pdf.output(pdf_file_path)
    return pdf_file_path

def generate_sentiment_chart():
    df = pd.DataFrame(data)
    plt.figure(figsize=(5, 3))
    sns.barplot(x='category', y='counts', data=df, hue='category', palette='Blues', legend=False)
    plt.title('Sentiment Analysis')
    plt.xlabel('Sentiment')
    plt.ylabel('Counts')
    plt.ylim(0, 100)

    # Save to a file instead of BytesIO
    chart_path = os.path.join(UPLOAD_FOLDER, 'sentiment_chart.png')
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def generate_sentiment_chart():
    df = pd.DataFrame(data)
    plt.figure(figsize=(5, 3))
    sns.barplot(x='category', y='counts', data=df, hue='category', palette='Blues', legend=False)
    plt.title('Sentiment Analysis')
    plt.xlabel('Sentiment')
    plt.ylabel('Counts')
    plt.ylim(0, 100)

    # Save to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)  # Move to the beginning of the BytesIO object
    return img

def generate_sales_chart():
    df = pd.DataFrame(sales_data)
    plt.figure(figsize=(5, 3))
    sns.lineplot(x='month', y='sales', data=df, marker='o')
    plt.title('Sales Performance')
    plt.xlabel('Month')
    plt.ylabel('Sales')
    plt.ylim(0, 600)

    # Save to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return img

def generate_revenue_chart():
    df = pd.DataFrame(sales_data)
    plt.figure(figsize=(5, 3))
    sns.barplot(x='month', y='revenue', data=df, hue='month', palette='Blues', legend=False)
    plt.title('Revenue Overview')
    plt.xlabel('Month')
    plt.ylabel('Revenue')
    plt.ylim(0, 3000)

    # Save to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return img

def generate_visitors_chart():
    df = pd.DataFrame(sales_data)
    plt.figure(figsize=(5, 3))
    sns.lineplot(x='month', y='visitors', data=df, marker='o', color='orange')
    plt.title('Visitor Statistics')
    plt.xlabel('Month')
    plt.ylabel('Visitors')
    plt.ylim(0, 400)

    # Save to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return img


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'xls', 'xlsx']

if __name__ == '__main__':
    app.run(debug=True)