# lead-gen-auto-apply
LeadGenMailer is an open-source AI-powered tool that automates sending personalized emails using Gemini AI. Upload a CSV of leads, attach a resume or brochure, preview emails, and send them via Gmail. Runs locally with a modern UI, perfect for job applications or lead generation outreach.
# 🚀 LeadGen Emailer

An automated email campaign tool that generates personalized emails using AI and sends them via Gmail SMTP. Perfect for job applications, sales outreach, and lead generation.

## ✨ Features

- **CSV Upload**: Upload lead information with email, company, and role columns
- **PDF Attachment**: Attach resume or brochure to all emails
- **AI-Powered Personalization**: Uses Google's Gemini AI to generate personalized emails
- **Email Preview**: Review all generated emails before sending
- **Gmail Integration**: Send emails directly through Gmail SMTP
- **Activity Logging**: Track all activities with timestamps
- **Responsive Design**: Modern, mobile-friendly interface

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Flask (Python)
- **AI**: Google Gemini AI via LangChain
- **Email**: Gmail SMTP
- **Data Processing**: Pandas

## 📋 Prerequisites

- Python 3.8+
- Gmail account with 2FA enabled
- Google Gemini API key
- Gmail App Password

## 🚀 Quick Start

### 1. Clone the Repository


git clone https://github.com/yourusername/leadgen-emailer.git
cd leadgen-emailer


### 2. Set Up Virtual Environment


python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate


### 3. Install Dependencies


pip install -r requirements.txt


### 4. Run the Application


python app.py


The application will be available at \`http://localhost:5000\`

## 🔧 Configuration

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings → Security → 2-Step Verification
3. Generate an App Password for "Mail"
4. Use this 16-character password in the application

### Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for use in the application

### CSV Format

Your CSV file should contain these columns:
- \`email\`: Recipient email address
- \`company\`: Company name
- \`role\`: Job role/position

Example:
\`\`\`csv
email,company,role
hr@techcorp.com,TechCorp,Software Engineer
jobs@startup.io,StartupIO,Full Stack Developer
\`\`\`


## 🔒 Security Best Practices

- Never commit your \`.env\` file to version control
- Use environment variables for sensitive data
- Regularly rotate your API keys and passwords
- Review generated emails before sending
- Test with a small batch first

## 🎯 Usage Tips

1. **Start Small**: Test with 2-3 leads first
2. **Review Content**: Always preview emails before sending
3. **Customize Prompt**: Modify the AI prompt in \`app.py\` for your use case
4. **Monitor Logs**: Check the activity log for any issues
5. **Rate Limiting**: Gmail has sending limits, space out large campaigns

## 🐛 Troubleshooting

### Common Issues

**"Authentication failed"**
- Verify your Gmail app password is correct
- Ensure 2FA is enabled on your Gmail account

**"API key invalid"**
- Check your Gemini API key
- Ensure you have API credits available

**"CSV format error"**
- Verify your CSV has the required columns: email, company, role
- Check for any special characters or formatting issues

**"File upload failed"**
- Ensure files are under 16MB
- Check file extensions (.csv and .pdf only)

## 📝 Customization

### Email Template

Edit the prompt in \`app.py\` around line 95 to customize the email template:

\`\`\`python
prompt = ChatPromptTemplate.from_template("""
Your custom email template here...
Use {company} and {role} as placeholders.
""")
\`\`\`

### Styling

Modify the CSS in \`index.html\` to change the appearance and branding.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


## ⚠️ Disclaimer

This tool is for legitimate business purposes only. Always comply with:
- CAN-SPAM Act
- GDPR regulations
- Gmail's Terms of Service
- Recipient consent requirements

Use responsibly and ethically.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the activity logs
3. Open an issue on GitHub
4. Contact support

---

**Happy Emailing! 📧✨**
