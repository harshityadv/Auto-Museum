# Auto-Museum Generator 🏛️

Transform any image into a professional museum exhibit description using AI and natural language processing.

## 🌟 Features

- **Image Recognition**: Upload images and automatically identify objects using Google's Gemini AI
- **Wikipedia Integration**: Automatically fetches comprehensive information from Wikipedia
- **RAG Pipeline**: Uses Retrieval-Augmented Generation with sentence transformers and FAISS for context-aware descriptions  
- **Museum-Quality Content**: Generates professional exhibit descriptions using Ollama LLM
- **Clean Web Interface**: Modern, responsive UI for easy interaction
- **Real-time Processing**: Fast image analysis and content generation


## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **AI/ML**: Google Gemini AI, Sentence Transformers, FAISS, Ollama
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data**: Wikipedia API, Beautiful Soup for web scraping

## 📋 Prerequisites

Before running this project, ensure you have:

1. **Python 3.8+** installed
2. **Google API Key** for Gemini AI
3. **Ollama** installed locally (for LLM generation)
4. **Git** for version control

### API Keys Required:
- Google Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/harshityadv/Auto-Museum.git
cd auto-museum-generator
```

### 2. Set Up Virtual Environment
```bash
python -m venv automuseum
source automuseum/bin/activate  # On Windows: automuseum\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### 5. Install Ollama (for LLM generation)
Visit [Ollama.ai](https://ollama.ai) and install for your operating system, then:
```bash
ollama pull llama3
```

### 6. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📁 Project Structure

```
auto-museum-generator/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore rules
│
├── static/                # Frontend files  
│   ├── style.css          # Styling
│   └── app.js             # JavaScript functionality
│
├── uploads/               # Temporary image uploads (auto-created)
├── templates/             # Flask templates
│   ├── index.html         # Main HTML page
│
└── notebooks/             # Original Jupyter notebook
    └── 01.ipynb          # Original development notebook
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
SECRET_KEY=your_flask_secret_key
FLASK_ENV=development
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

### Ollama Models

The project uses Ollama for generating museum descriptions. Install the required model:

```bash
ollama pull llama3  # Primary model
# Alternatives:
# ollama pull llama3:70b  # For better quality (requires more resources)
# ollama pull mistral     # Alternative model
```

## 📖 API Reference

### POST /api/process_image

Process an uploaded image and generate museum exhibit description.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `image` file (PNG, JPG, JPEG, GIF)

**Response:**
```json
{
  "success": true,
  "result": {
    "title": "Exhibit Title",
    "description": "Generated museum description...",
    "object_name": "Identified Object",
    "sources": "https://en.wikipedia.org/wiki/..."
  }
}
```

## 🧪 How It Works

1. **Image Upload**: User uploads an image through the web interface
2. **Object Identification**: Google Gemini AI analyzes the image and identifies the object
3. **Information Retrieval**: System searches Wikipedia for relevant information
4. **Content Processing**: RAG pipeline processes the Wikipedia content using:
   - Sentence Transformers for embedding generation
   - FAISS for efficient similarity search
   - Context retrieval for relevant information
5. **Description Generation**: Ollama LLM generates museum-quality descriptions
6. **Result Display**: Formatted exhibit description is returned to the user

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Google Gemini AI for image recognition
- Wikipedia for comprehensive object information
- Sentence Transformers team for embedding models
- Meta for FAISS vector search
- Ollama team for local LLM capabilities

## 🐛 Troubleshooting

### Common Issues

1. **Import Error with sentence-transformers**: Install torch first
```bash
pip install torch torchvision torchaudio
pip install sentence-transformers
```

2. **FAISS Installation Issues**: Use CPU version
```bash
pip install faiss-cpu
```

3. **Ollama Connection Error**: Ensure Ollama is running
```bash
ollama serve
```

4. **Google API Errors**: Check API key and enable Gemini API in Google Cloud Console

### Performance Tips

- Use smaller sentence transformer models for faster processing
- Adjust FAISS index parameters for your use case
- Consider using GPU versions for production workloads

**Made with ❤️ for education and cultural preservation**
