import os
import pandas as pd
import smtplib
import json
from datetime import datetime
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
LOGS_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'csv', 'pdf'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables to store data
uploaded_files = {}
generated_emails = []
gmail_credentials = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_activity(message):
    """Log activity to file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(os.path.join(LOGS_FOLDER, 'email_log.txt'), 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'csv_file' not in request.files or 'pdf_file' not in request.files:
            return jsonify({'error': 'Both CSV and PDF files are required'}), 400
        
        csv_file = request.files['csv_file']
        pdf_file = request.files['pdf_file']
        
        if csv_file.filename == '' or pdf_file.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        if not (allowed_file(csv_file.filename) and allowed_file(pdf_file.filename)):
            return jsonify({'error': 'Invalid file types. Only CSV and PDF allowed'}), 400
        
        # Save files
        csv_filename = secure_filename(csv_file.filename)
        pdf_filename = secure_filename(pdf_file.filename)
        
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        
        csv_file.save(csv_path)
        pdf_file.save(pdf_path)
        
        # Store file paths globally
        uploaded_files['csv'] = csv_path
        uploaded_files['pdf'] = pdf_path
        
        # Validate CSV structure
        try:
            df = pd.read_csv(csv_path)
            df.columns = df.columns.str.strip().str.lower()
            
            required_columns = ['email', 'company', 'role']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return jsonify({
                    'error': f'CSV missing required columns: {", ".join(missing_columns)}. Required: email, company, role'
                }), 400
            
            log_activity(f"Files uploaded successfully: {csv_filename}, {pdf_filename}")
            return jsonify({
                'message': 'Files uploaded successfully',
                'csv_rows': len(df),
                'columns': list(df.columns)
            })
            
        except Exception as e:
            return jsonify({'error': f'Error reading CSV: {str(e)}'}), 400
            
    except Exception as e:
        log_activity(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/generate', methods=['POST'])
def generate_emails():
    try:
        data = request.json
        api_key = data.get('api_key')
        gmail_email = data.get('gmail_email')
        app_password = data.get('app_password')
        
        if not all([api_key, gmail_email, app_password]):
            return jsonify({'error': 'API key, Gmail email, and app password are required'}), 400
        
        if 'csv' not in uploaded_files:
            return jsonify({'error': 'Please upload CSV file first'}), 400
        
        # Store Gmail credentials
        gmail_credentials['email'] = gmail_email
        gmail_credentials['password'] = app_password
        
        # Set up Gemini AI
        os.environ["GOOGLE_API_KEY"] = api_key
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
        
        prompt = ChatPromptTemplate.from_template("""
Please write a short, professional job application email for the role of {role} at {company}.

My name is Gokul Arya. I have completed 3 internships in software engineering and web security. I have hands-on experience building REST APIs using Flask, optimizing SQL databases, and applying OWASP security practices. My technical skills include Python, Flask, Django, JavaScript, SQL, and AWS.

Do not mention where the job was posted or how it was found. Avoid using any placeholders or speculative content. Focus on clearly expressing interest in the role, mentioning the attached resume, and briefly stating relevant skills. The tone should be polite, confident, and direct.

End the email with this sign-off:
Gokul Arya  
📞 +91 7414909606  
✉️ gokularya800@gmail.com
        """)
        
        # Read CSV
        df = pd.read_csv(uploaded_files['csv'])
        df.columns = df.columns.str.strip().str.lower()
        
        # Generate emails
        global generated_emails
        generated_emails = []
        
        chain = prompt | llm
        
        for index, row in df.iterrows():
            try:
                email = row['email']
                company = row['company']
                role = row['role']
                
                # Generate email content
                result = chain.invoke({"company": company, "role": role})
                email_body = result.content
                subject = f"Application for {role} at {company}"
                
                generated_emails.append({
                    'to': email,
                    'subject': subject,
                    'body': email_body,
                    'company': company,
                    'role': role
                })
                
                log_activity(f"Generated email for {company} - {role}")
                
            except Exception as e:
                log_activity(f"Error generating email for {company}: {str(e)}")
                continue
        
        return jsonify({
            'message': f'Generated {len(generated_emails)} emails successfully',
            'emails': generated_emails
        })
        
    except Exception as e:
        log_activity(f"Generation error: {str(e)}")
        return jsonify({'error': f'Email generation failed: {str(e)}'}), 500

@app.route('/send', methods=['POST'])
def send_emails():
    try:
        if not generated_emails:
            return jsonify({'error': 'No emails to send. Generate emails first.'}), 400
        
        if not gmail_credentials:
            return jsonify({'error': 'Gmail credentials not set'}), 400
        
        if 'pdf' not in uploaded_files:
            return jsonify({'error': 'Resume PDF not uploaded'}), 400
        
        sent_count = 0
        failed_count = 0
        
        for email_data in generated_emails:
            try:
                # Create email message
                msg = EmailMessage()
                msg['Subject'] = email_data['subject']
                msg['From'] = gmail_credentials['email']
                msg['To'] = email_data['to']
                msg.set_content(email_data['body'])
                
                # Attach PDF
                with open(uploaded_files['pdf'], 'rb') as f:
                    msg.add_attachment(
                        f.read(),
                        maintype='application',
                        subtype='pdf',
                        filename='resume.pdf'
                    )
                
                # Send email
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(gmail_credentials['email'], gmail_credentials['password'])
                    smtp.send_message(msg)
                
                sent_count += 1
                log_activity(f"Email sent successfully to {email_data['to']} ({email_data['company']})")
                
            except Exception as e:
                failed_count += 1
                log_activity(f"Failed to send email to {email_data['to']}: {str(e)}")
                continue
        
        return jsonify({
            'message': f'Email sending completed. Sent: {sent_count}, Failed: {failed_count}',
            'sent': sent_count,
            'failed': failed_count
        })
        
    except Exception as e:
        log_activity(f"Sending error: {str(e)}")
        return jsonify({'error': f'Email sending failed: {str(e)}'}), 500

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'files_uploaded': bool(uploaded_files),
        'emails_generated': len(generated_emails),
        'credentials_set': bool(gmail_credentials)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
