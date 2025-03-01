# CRE Email Assistant

An AI-powered email management system designed specifically for commercial real estate brokers that organizes communications into intelligent Capsules.

## 📋 Overview

CRE Email Assistant helps commercial real estate brokers manage their email communications more efficiently by:

- Automatically categorizing emails into "Capsules" based on properties, deals, and relationships
- Extracting key information from emails (property details, deadlines, follow-ups)
- Providing concise summaries of email threads and conversations
- Tracking follow-ups and scheduling reminders
- Integrating with calendar and CRM systems

## ✨ Key Features

- **Smart Email Organization**: Emails are automatically imported and sorted into relevant Capsules
- **Intelligent Information Extraction**: AI identifies and extracts important CRE-specific details
- **Capsule Management**: Interactive sidebar UI for managing Capsules (pin, archive, follow-up)
- **Follow-up Tracking**: Automated detection and reminders for required follow-ups
- **CRE-Specific Templates**: Pre-built templates for common commercial real estate communications

## 🔧 Technology Stack

- **Backend**: Python with Flask/FastAPI
- **Frontend**: React.js
- **Database**: MongoDB
- **NLP**: OpenAI API and specialized CRE entity recognition
- **Email Integration**: Gmail API (initial version)
- **Deployment**: Docker containers on AWS/Heroku

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm
- MongoDB
- Google Developer Account (for Gmail API)

## 📝 Project Structure

```
cre-email-assistant/
├── app/                    # Main application code
│   ├── api/                # API endpoints
│   ├── models/             # Database models
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── frontend/               # React frontend application
├── scripts/                # Setup and utility scripts
├── tests/                  # Test suite
├── .env.example            # Example environment variables
├── app.py                  # Application entry point
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🛣️ Roadmap

This project is being developed in stages:

1. Setting up infrastructure and email connectivity
2. Implementing core NLP functionality
3. Building user interface components
4. Connecting with external tools
5. Preparing and launching for user testing

See our detailed roadmap for more information.


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
