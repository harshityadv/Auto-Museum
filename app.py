import os
import json
import gc
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
import re
import time
from google import genai
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import ollama
from contextlib import contextmanager

app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Gemini client
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize global SentenceTransformer model to avoid reloading
try:
    GLOBAL_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    print("SentenceTransformer model loaded successfully")
except Exception as e:
    print(f"Error loading SentenceTransformer: {e}")
    GLOBAL_MODEL = None

@contextmanager
def memory_cleanup():
    """Context manager for memory cleanup"""
    try:
        yield
    finally:
        # Force garbage collection
        gc.collect()
        # Clear any lingering variables
        if 'locals' in dir():
            for var in list(locals().keys()):
                if var not in ['gc']:
                    del locals()[var]

class WikipediaScraper:
    """Scraper for Wikipedia that retrieves information about objects identified in images."""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/wiki/"
        self.headers = {
            'User-Agent': 'Auto-Museum/1.0 (Educational Project; contact@automuseum.example.com)'
        }
    
    def clean_text(self, text):
        """Remove references, citations and other wiki markup"""
        if not text:
            return ""
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\(listen\)', '', text)
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        return text.strip()
    
    def get_article_content(self, title, url):
        """Retrieve and parse Wikipedia article content for a given topic"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find(id="mw-content-text")
            
            if not content_div:
                raise ValueError("Could not find article content")
            
            paragraphs = []
            paragraph_count = 0
            max_paragraphs = 10  # Limit to prevent memory issues
            
            for p in content_div.find_all('p'):
                if paragraph_count >= max_paragraphs:
                    break
                    
                text = self.clean_text(p.get_text())
                if text and len(text) > 50:  # Only include substantial paragraphs
                    paragraphs.append(text)
                    paragraph_count += 1
            
            return {
                'title': title,
                'url': url,
                'paragraphs': paragraphs
            }
            
        except requests.RequestException as e:
            print(f"Network error retrieving Wikipedia content for {title}: {e}")
            return {
                'title': title,
                'url': url,
                'paragraphs': [f"Could not retrieve information about {title} due to network error."]
            }
        except Exception as e:
            print(f"Error retrieving Wikipedia content for {title}: {e}")
            return {
                'title': title,
                'url': url,
                'paragraphs': [f"Could not retrieve information about {title}."]
            }

class RAGPipeline:
    def __init__(self, model=None):
        self.model = model or GLOBAL_MODEL
        if not self.model:
            raise ValueError("SentenceTransformer model not available")
            
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.documents = []
        self.metadata = {}
        self.object_name = ""
    
    def add_wikipedia_content(self, wiki_data):
        """Process Wikipedia content and add to the vector database"""
        try:
            self.documents = wiki_data['paragraphs'][:8]  # Limit documents to prevent memory issues
            self.metadata = {'title': wiki_data['title'], 'url': wiki_data['url']}
            self.object_name = wiki_data['title']
            self._update_index()
        except Exception as e:
            print(f"Error adding Wikipedia content: {e}")
            raise
    
    def _update_index(self):
        """Update the FAISS index with the current documents"""
        if not self.documents:
            return
        
        try:
            # Clear existing index
            if self.index:
                del self.index
                gc.collect()
            
            # Create embeddings in batches to manage memory
            embeddings = []
            batch_size = 4
            
            for i in range(0, len(self.documents), batch_size):
                batch = self.documents[i:i+batch_size]
                batch_embeddings = self.model.encode(batch, show_progress_bar=False)
                embeddings.extend(batch_embeddings)
            
            embeddings = np.array(embeddings).astype('float32')
            
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings)
            
            # Clear embeddings from memory
            del embeddings
            gc.collect()
            
        except Exception as e:
            print(f"Error updating FAISS index: {e}")
            raise
    
    def retrieve(self, query, top_k=3):
        """Retrieve relevant context for a query"""
        if not self.index or not self.documents:
            return []
        
        try:
            query_embedding = self.model.encode([query], show_progress_bar=False)[0]
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            k = min(top_k, len(self.documents), self.index.ntotal)
            distances, indices = self.index.search(query_embedding, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents) and idx >= 0:
                    results.append({
                        'text': self.documents[idx],
                        'metadata': self.metadata,
                        'distance': float(distances[0][i])
                    })
            
            return results
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    def generate_museum_description(self, model="llama3"):
        """Generate a museum-style description using the LLM and retrieved context"""
        try:
            context = self.retrieve(f"Information about {self.object_name}", top_k=5)
            
            if not context:
                return {
                    'title': f"Exhibit: {self.object_name}",
                    'description': f"Information about this {self.object_name} is currently being curated for display.",
                    'object_name': self.object_name,
                    'sources': self.metadata.get('url', '')
                }
            
            # Build context text with length limit
            context_text = ""
            for item in context:
                if len(context_text) + len(item['text']) > 2000:  # Limit context size
                    break
                context_text += item['text'] + "\n\n"
            
            prompt = f'''You are a museum curator writing an informative and engaging description plaque for an exhibit.

Object: {self.object_name}

Based on the following information, write a museum-style description plaque for this object.
The description should be informative, educational, and engaging for museum visitors.
Write in a professional tone similar to what would be found in a prestigious museum.

CONTEXTUAL INFORMATION:
{context_text.strip()}

REQUIREMENTS:
1. Begin with a catchy title (max 10 words)
2. The main description should be 300-400 words
3. Include key historical or scientific information
4. Make it accessible to general audience (grade 10 level)
5. Include 2-3 interesting facts that would surprise visitors
6. Format as: Title on first line, then description

Please write a complete museum description now.'''

            # Generate description using Ollama with timeout
            try:
                response = ollama.generate(
                    model=model, 
                    prompt=prompt,
                    options={
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'max_tokens': 500,
                        'timeout': 30
                    }
                )
                
                if not response or 'response' not in response:
                    raise ValueError("Empty response from Ollama")
                
                description = response['response'].strip()
                
                # Parse response
                lines = description.split('\n', 1)
                title = lines[0].strip().replace('"', '').replace('Title:', '').strip()
                body = lines[1].strip() if len(lines) > 1 else description
                
                # Clean title
                if not title or len(title) > 100:
                    title = f"Exhibit: {self.object_name}"
                
                return {
                    'title': title,
                    'description': body,
                    'object_name': self.object_name,
                    'sources': self.metadata.get('url', '')
                }
                
            except Exception as llm_error:
                print(f"Error with Ollama generation: {llm_error}")
                return {
                    'title': f"Exhibit: {self.object_name}",
                    'description': f"This fascinating {self.object_name} represents an important artifact with rich historical significance. While our curatorial team is working to provide detailed information, we encourage visitors to explore and discover the stories this piece holds. Museum descriptions will be updated as our research continues.",
                    'object_name': self.object_name,
                    'sources': self.metadata.get('url', '')
                }
                
        except Exception as e:
            print(f"Error generating museum description: {e}")
            return {
                'title': f"Exhibit: {self.object_name}",
                'description': f"Information about this {self.object_name} is currently being curated.",
                'object_name': self.object_name,
                'sources': self.metadata.get('url', '')
            }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.index:
                del self.index
            self.documents.clear()
            self.metadata.clear()
            gc.collect()
        except Exception as e:
            print(f"Error during cleanup: {e}")

def simple_parse(response_text):
    """Simple parsing for consistent format responses"""
    if not response_text:
        return {'title': None, 'url': None}
    
    lines = [line.strip() for line in response_text.strip().split('\n') if line.strip()]
    title = lines[0] if len(lines) > 0 else "Unknown"
    url = lines[1] if len(lines) > 1 else None
    
    # Clean title
    title = title.replace('Object:', '').replace('Title:', '').strip()
    
    # Validate URL
    if url and not (url.startswith('http://') or url.startswith('https://')):
        # Try to construct Wikipedia URL
        if 'wikipedia.org' not in url:
            url = f"https://en.wikipedia.org/wiki/{url.replace(' ', '_')}"
    
    return {
        'title': title,
        'url': url
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/process_image', methods=['POST'])
def process_image():
    filepath = None
    rag = None
    
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload JPG, PNG, or GIF.'}), 400

        # Check API key
        if not GOOGLE_API_KEY:
            return jsonify({'success': False, 'error': 'Google API key not configured'}), 500

        # Check if model is available
        if not GLOBAL_MODEL:
            return jsonify({'success': False, 'error': 'SentenceTransformer model not available'}), 500

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process with memory cleanup
        with memory_cleanup():
            try:
                # Upload to Gemini
                my_file = client.files.upload(file=filepath)
                
                # Get object identification
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[
                        my_file, 
                        "Identify this object and provide: 1) The exact name of the object, 2) The Wikipedia URL for this object (if it exists). Format: Object name on first line, Wikipedia URL on second line. If no Wikipedia page exists, write 'No Wikipedia page' on the second line."
                    ],
                )

                if not response or not response.text:
                    raise ValueError("Empty response from Gemini")

                # Parse response
                result = simple_parse(response.text)
                
                if not result['title'] or result['title'].lower() == 'unknown':
                    return jsonify({
                        'success': False, 
                        'error': 'Could not identify the object in the image. Please try a clearer image.'
                    }), 400

                if not result['url'] or 'No Wikipedia page' in result['url']:
                    # Create basic description without Wikipedia
                    return jsonify({
                        'success': True,
                        'result': {
                            'title': f"Exhibit: {result['title']}",
                            'description': f"This appears to be a {result['title']}. While we don't have detailed historical information available at the moment, this represents an interesting object worthy of study and appreciation. Museum curators are working to provide more comprehensive information about similar artifacts.",
                            'object_name': result['title'],
                            'sources': 'Information pending curatorial research'
                        }
                    })

                # Scrape Wikipedia with timeout and memory management
                scraper = WikipediaScraper()
                wiki_info = scraper.get_article_content(result['title'], result['url'])

                if not wiki_info['paragraphs']:
                    return jsonify({
                        'success': False,
                        'error': 'Could not retrieve information from Wikipedia'
                    }), 400

                # Generate museum description
                rag = RAGPipeline()
                rag.add_wikipedia_content(wiki_info)
                output = rag.generate_museum_description()

                return jsonify({
                    'success': True,
                    'result': output
                })

            except Exception as processing_error:
                print(f"Processing error: {processing_error}")
                return jsonify({
                    'success': False,
                    'error': f'Processing failed: {str(processing_error)}'
                }), 500

    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

    finally:
        # Cleanup resources
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            if rag:
                rag.cleanup()
            gc.collect()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': 'Internal server error. Please try again.'}), 500

if __name__ == '__main__':
    print("Starting Auto-Museum Flask App...")
    print(f"Google API Key configured: {'Yes' if GOOGLE_API_KEY else 'No'}")
    print(f"SentenceTransformer model loaded: {'Yes' if GLOBAL_MODEL else 'No'}")
    app.run(debug=True, host='0.0.0.0', port=5000)