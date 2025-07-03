# AI Document Analysis Application

A powerful AI-powered document analysis tool that lets you upload documents and chat with them using Azure OpenAI.

## Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **AI Chat**: Interactive chat interface to query your documents
- **Smart Search**: FAISS vector store for intelligent document retrieval
- **Modern UI**: Clean Streamlit interface with real-time status updates
- **RESTful API**: FastAPI backend with comprehensive endpoints

## Prerequisites

- Python 3.11 or higher
- Azure OpenAI account with API access
- Git (for cloning the repository)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-document-analysis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with your Azure OpenAI credentials:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-01
```

### 3. Run the Application

**Option A: Run Both Services Together**
```bash
python start_services.py
```

**Option B: Run Services Separately**

Terminal 1 (Backend):
```bash
python run_backend.py
```

Terminal 2 (Frontend):
```bash
streamlit run app.py --server.port 5000
```

### 4. Access the Application

- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## How to Use

1. **Upload Document**: Use the sidebar to upload a PDF, TXT, or DOCX file
2. **Wait for Processing**: The system will extract text and create embeddings
3. **Start Chatting**: Ask questions about your document in the chat interface
4. **Get AI Responses**: Receive intelligent answers based on document content

## Example Queries

- "What is the main topic of this document?"
- "Summarize the key points"
- "What are the conclusions mentioned?"
- "Find information about [specific topic]"

## Project Structure

```
ai-document-analysis/
├── app.py                 # Streamlit frontend
├── backend/
│   ├── main.py           # FastAPI application
│   ├── models/
│   │   └── schemas.py    # Pydantic models
│   ├── services/
│   │   ├── azure_openai_service.py
│   │   ├── document_processor.py
│   │   └── vector_store.py
│   └── utils/
│       └── file_utils.py
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── requirements.txt      # Python dependencies
├── start_services.py     # Service orchestrator
└── run_backend.py        # Backend runner
```

## Troubleshooting

### Common Issues

1. **Backend fails to start**: Check that your Azure OpenAI credentials are correct
2. **Document upload fails**: Ensure the file is under 50MB and is PDF/TXT/DOCX format
3. **No AI responses**: Verify your Azure OpenAI deployment names are correct
4. **Connection errors**: Make sure both backend (8000) and frontend (5000) ports are available

### Environment Variables

Make sure all required environment variables are set:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`

## API Endpoints

- `POST /upload` - Upload and process document
- `POST /query` - Query the document
- `GET /status` - Check processing status
- `POST /reset` - Reset current session
- `GET /health` - Health check

## Support

For issues or questions, check the logs in your terminal or review the API documentation at `/docs`.