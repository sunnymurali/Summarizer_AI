# 🚀 Local Setup Guide - AI Document Analysis

This guide will help you set up and run the AI Document Analysis application on your local machine.

## 📋 Prerequisites

- **Python 3.11+** (required)
- **Azure OpenAI account** with API access
- **Git** (for cloning)

## 🔧 Quick Setup (Choose One Method)

### Method 1: Automated Setup (Recommended)

```bash
# Run the setup script
python setup_local.py
```

### Method 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
# Windows:
install_requirements.bat
# macOS/Linux:
chmod +x install_requirements.sh
./install_requirements.sh
```

## 🔑 Configure Azure OpenAI

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your Azure OpenAI credentials:**
   ```env
   AZURE_OPENAI_API_KEY=your_actual_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   ```

### 🔍 Where to Find Your Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Click "Keys and Endpoint" in the left sidebar
4. Copy your API key and endpoint
5. Go to "Model deployments" to see your deployment names

## 🎯 Run the Application

### Option A: Run Everything Together
```bash
python start_services.py
```

### Option B: Run Services Separately

**Terminal 1 - Backend:**
```bash
python run_backend.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run app.py --server.port 5000
```

## 🌐 Access the Application

- **Main App**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 📱 How to Use

1. **Upload Document**: Click "Choose a document" in the sidebar
2. **Supported Formats**: PDF, TXT, DOCX files
3. **Wait for Processing**: The system will extract and index the content
4. **Start Chatting**: Ask questions about your document
5. **Get AI Responses**: Receive intelligent answers based on the content

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
- Check your Azure OpenAI credentials in `.env`
- Verify your deployment names are correct
- Ensure port 8000 is available

**Frontend connection errors:**
- Make sure the backend is running on port 8000
- Check firewall settings
- Verify both services are running

**Document upload fails:**
- File size limit is 50MB
- Only PDF, TXT, DOCX formats are supported
- Check file permissions

**No AI responses:**
- Verify Azure OpenAI deployment names
- Check API key permissions
- Review backend logs for errors

### Debug Steps

1. **Check backend logs:**
   ```bash
   python run_backend.py
   ```

2. **Test API directly:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Verify environment variables:**
   ```bash
   python -c "import os; print(os.getenv('AZURE_OPENAI_API_KEY', 'NOT_SET'))"
   ```

## 📊 System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Network**: Internet connection for Azure OpenAI API
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## 📁 Project Structure

```
ai-document-analysis/
├── 📄 app.py                 # Streamlit frontend
├── 📁 backend/
│   ├── 📄 main.py           # FastAPI server
│   ├── 📁 models/           # Data models
│   ├── 📁 services/         # Business logic
│   └── 📁 utils/            # Utilities
├── 📁 .streamlit/           # Streamlit config
├── 📄 start_services.py     # Run both services
├── 📄 run_backend.py        # Run backend only
├── 📄 setup_local.py        # Setup script
├── 📄 .env.example          # Environment template
└── 📄 README.md             # Documentation
```

## 💡 Tips

- **Virtual Environment**: Always use a virtual environment to avoid conflicts
- **File Size**: Keep documents under 50MB for best performance
- **Token Limits**: Very large documents may be truncated
- **Browser**: Use Chrome or Firefox for best compatibility

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review backend logs for error messages
3. Test API endpoints at http://localhost:8000/docs
4. Verify your Azure OpenAI credentials

## 🎉 Success!

If everything is working:
- You should see the Streamlit interface at http://localhost:5000
- The backend API should respond at http://localhost:8000/health
- Document uploads should process without errors
- Chat responses should be generated from your documents

Happy document analysis! 🚀