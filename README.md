# Legal Obligation Management System

A proof-of-concept application for extracting, managing, and tracking legal obligations from documents with Jira integration.

## Overview

This application provides an end-to-end solution for legal teams to:

1. Extract legal obligations from uploaded documents using AI
2. Manage and track these obligations in a structured format
3. Create Jira issues for obligations to integrate with project management workflows
4. Enforce data integrity between the application and Jira

## Features

- **AI-Powered Extraction**: Automatically extract legal obligations from uploaded PDF documents
- **Obligation Management**: View, edit, and track legal obligations with details like priority, deadline, and responsible party
- **Jira Integration**: Create Jira issues for obligations with locked descriptions to maintain data integrity
- **Modern UI**: Clean, responsive interface built with React and Material UI
- **Robust Backend**: FastAPI backend with async support for efficient processing

## Screenshots

### Document Upload
![Document Upload Screen](/screenshots/upload_document.png)
*Upload a PDF or DOCX file to extract legal obligations*

### Obligations List
![Obligations List](/screenshots/obligations_list.png)
*View and manage all extracted obligations with filtering options*

### Edit Obligation
![Edit Obligation](/screenshots/edit_obligation.png)
*Edit obligation details including text, party name, deadline, section, and priority*

### Jira Integration
![Jira Issue](/screenshots/jira_issue.png)
*Automatically created Jira issue with locked description field*

## Architecture

### Backend (FastAPI)

- **API Layer**: RESTful endpoints for obligation management and document processing
- **Service Layer**: Business logic for obligation extraction, storage, and Jira integration
- **Models**: Pydantic models for data validation and serialization
- **Project Management**: Extensible factory pattern for integration with Jira (and potentially other tools)

### Frontend (React)

- **Context-based State Management**: React Context API for global state
- **Component-based UI**: Reusable React components
- **Responsive Design**: Mobile-friendly interface
- **Form Validation**: Client-side validation for obligation data

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Jira account (optional, mock implementation available for development)

### Environment Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Backend Setup

```bash
cd obligation-2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd obligation-2/frontend
npm install
npm run dev
```

## Usage

1. **Upload Documents**: Upload legal documents through the web interface
2. **Review Extracted Obligations**: View and edit the automatically extracted obligations
3. **Manage Obligations**: Add details like priority, deadline, and responsible party
4. **Create Jira Issues**: Link obligations to Jira for project management tracking
5. **Track Progress**: Monitor the status of obligations through the dashboard

## Jira Integration

The system integrates with Jira to create issues for legal obligations:

- Creates issues with detailed descriptions from obligation data
- Sets priority based on obligation priority
- Locks description fields in Jira to maintain data integrity
- Prevents modification of obligation text after Jira issue creation

## Development Features

- **Mock Jira Implementation**: Develop without real Jira credentials
- **Automatic Serialization**: Proper JSON serialization of Pydantic models
- **Error Handling**: Comprehensive error handling throughout the application
- **Logging**: Detailed logging for debugging and monitoring

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the AI-powered extraction capabilities
- Jira for project management integration
- FastAPI and React for the application framework
