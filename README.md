# CRE Email Assistant

AI-powered email management system for commercial real estate brokers that organizes communications into intelligent Capsules.

## Project Status

Currently in development phase (Level 2: Core Functionality).

## Roadmap Progress

- [x] Create GitHub repository
- [x] Set up development environment
- [x] Initialize Flask project
- [x] Set up Google API connections
- [x] Implement Email Processing Pipeline
- [x] Implement Entity Recognition with OpenAI
- [ ] Implement Capsule Management System
- [ ] Develop User Interface

## Email Processing Pipeline

The Email Processing Pipeline is a core component of the CRE Email Assistant that:

1. Fetches emails from Gmail
2. Processes and normalizes email data
3. Extracts entities and key information (properties, people, companies, dates)
4. Organizes emails into intelligent Capsules based on content analysis
5. Stores processed data in MongoDB

### Running the Pipeline

You can run the email processing pipeline in several ways:

#### Command Line

```bash
# Process emails once
python process_emails.py

# Process emails continuously (every 5 minutes)
python process_emails.py --continuous --interval=300 --max-emails=10
```

#### API Endpoint

```bash
# Trigger email processing via API
curl -X POST http://localhost:8000/api/emails/process -H "Content-Type: application/json" -d '{"max_emails": 10}'
```

## Entity Recognition

The Entity Recognition system uses OpenAI's GPT-4o-mini model to extract structured information from emails:

1. Properties: Real estate properties mentioned in emails (addresses, details)
2. People: Individuals mentioned in emails (names, roles, contact info)
3. Companies: Organizations mentioned in emails (names, types)
4. Dates: Important dates mentioned in emails (meetings, deadlines)
5. Financial details: Monetary values and financial terms
6. Action items: Tasks, follow-ups, and requests
7. Keywords: Important CRE-specific terms and concepts

The system also generates concise summaries of emails and categorizes them by type and priority.

### Testing Entity Recognition

You can test the entity recognition capabilities with:

```bash
# Run entity recognition tests
python -m tests.test_entity_recognition
```

## Development

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_connection_string
   SECRET_KEY=your_secret_key
   ```
4. Run the application: `python run.py`

### Authentication

Before using the email processing pipeline, you need to authenticate with Gmail:

1. Start the web application: `python run.py`
2. Navigate to the authentication page
3. Follow the OAuth flow to grant access to your Gmail account

## Frontend

The CRE Email Assistant includes a React-based frontend for managing emails and capsules.

### Setup

1. Install Node.js and npm if you don't have them already
2. Run the frontend setup script:
   ```bash
   ./setup_frontend.sh
   ```
   
   This will install the required dependencies and build the frontend.

### Development

To start the frontend development server:

```bash
npm start
```

This will start a webpack dev server with hot reloading at http://localhost:8080.

### Building for Production

To build the frontend for production:

```bash
npm run build
```

This will create optimized production files in the `app/static/dist` directory.

