// Auto-Museum Generator JavaScript - Fixed Version

class AutoMuseumApp {
    constructor() {
        this.demoData = {
            title: "Unlocking the Secrets of the Ancient World: The Rosetta Stone",
            description: "Discover one of history's most significant archaeological finds, the Rosetta Stone! This ancient stele holds the key to deciphering Egyptian hieroglyphics and is a testament to human ingenuity.\n\nIn 196 BC, during the Ptolemaic dynasty of Egypt, King Ptolemy V Epiphanes issued a decree inscribed on this granodiorite stone. The top register features ancient Egyptian hieroglyphs, while the middle text is written in Demotic script, and the bottom inscription is in Ancient Greek. This unique trilingual artifact allows us to understand the evolution of language and writing systems.\n\nInterestingly, the Rosetta Stone's inscriptions were only slightly modified across its three versions, making it a crucial tool for deciphering Egyptian scripts. The stone itself measures 112.3 cm high, 75.7 cm wide, and 28.4 cm thick, weighing approximately 760 kilograms.\n\nDid you know that the Rosetta Stone has inspired various language translation tools and software in modern times? It's a testament to the enduring power of ancient knowledge!\n\n**Fascinating Facts:**\n\n* The Rosetta Stone is not the only \"Rosetta stone\" in history. Other bilingual or trilingual epigraphical documents have been described as similar, allowing for the decipherment of ancient written scripts.\n* A replica of the Rosetta Stone can be found in the King's Library of the British Museum, where visitors can touch and experience it as early 19th-century visitors did.\n\nCome and explore this incredible artifact, and uncover the secrets of the ancient world!",
            object_name: "Rosetta Stone",
            sources: "https://en.wikipedia.org/wiki/Rosetta_Stone"
        };

        this.initializeElements();
        this.bindEvents();
        this.initializeSpeech();
    }

    initializeElements() {
        // Main sections
        this.uploadSection = document.getElementById('uploadSection');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        
        // Upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadPreview = document.getElementById('uploadPreview');
        this.previewImage = document.getElementById('previewImage');
        this.previewFilename = document.getElementById('previewFilename');
        
        // Buttons
        this.demoBtn = document.getElementById('demoBtn');
        this.processBtn = document.getElementById('processBtn');
        this.removeBtn = document.getElementById('removeBtn');
        this.copyBtn = document.getElementById('copyBtn');
        this.shareBtn = document.getElementById('shareBtn');
        this.newUploadBtn = document.getElementById('newUploadBtn');
        this.speakBtn = document.getElementById('speakBtn');
        this.stopSpeakBtn = document.getElementById('stopSpeakBtn');
        
        // Result elements
        this.resultTitle = document.getElementById('resultTitle');
        this.resultDescription = document.getElementById('resultDescription');
        this.resultObject = document.getElementById('resultObject');
        this.resultSource = document.getElementById('resultSource');
    }

    initializeSpeech() {
        this.speechSynthesis = window.speechSynthesis;
        this.currentUtterance = null;
        this.isPlaying = false;
        
        // Load voices
        if (this.speechSynthesis) {
            this.loadVoices();
            this.speechSynthesis.addEventListener('voiceschanged', () => this.loadVoices());
        }
    }

    loadVoices() {
        this.voices = this.speechSynthesis.getVoices();
        // Prefer high-quality English voices
        this.preferredVoice = this.voices.find(voice => 
            /Google|Microsoft|Apple/i.test(voice.name) && 
            /en[-_]?US|en[-_]?GB/i.test(voice.lang)
        ) || this.voices.find(voice => /en/i.test(voice.lang)) || this.voices[0];
    }

    bindEvents() {
        // File upload events
        this.uploadArea.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.fileInput.click();
        });
        
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Button events
        this.demoBtn.addEventListener('click', () => this.runDemo());
        this.processBtn.addEventListener('click', () => this.processImage());
        this.removeBtn.addEventListener('click', () => this.removeImage());
        this.copyBtn.addEventListener('click', () => this.copyDescription());
        this.shareBtn.addEventListener('click', () => this.shareResult());
        this.newUploadBtn.addEventListener('click', () => this.resetToUpload());
        
        // Speech events
        if (this.speakBtn) {
            this.speakBtn.addEventListener('click', () => this.speakDescription());
        }
        if (this.stopSpeakBtn) {
            this.stopSpeakBtn.addEventListener('click', () => this.stopSpeaking());
        }
        
        // Prevent file input from interfering with upload area clicks
        this.fileInput.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // Drag and drop handlers
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    // File handling
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }

    handleFile(file) {
        if (!file.type.startsWith('image/')) {
            this.showNotification('Please select an image file', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.previewFilename.textContent = file.name;
            this.showPreview();
        };
        reader.readAsDataURL(file);
    }

    showPreview() {
        this.uploadArea.style.display = 'none';
        this.uploadPreview.classList.remove('hidden');
    }

    removeImage() {
        this.uploadArea.style.display = 'block';
        this.uploadPreview.classList.add('hidden');
        this.fileInput.value = '';
        this.previewImage.src = '';
        this.previewFilename.textContent = '';
    }

    // Processing functions - FIXED VERSION
    async processImage() {
        if (!this.fileInput.files.length) {
            this.showNotification('Please select an image first', 'error');
            return;
        }

        const file = this.fileInput.files[0];
        this.showLoading();
        
        // Disable process button to prevent multiple submissions
        this.processBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch('/api/process_image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }

            if (!data.success) {
                throw new Error(data.error || 'Processing failed');
            }

            // Show results and speak description
            this.showResults(data.result);
            this.speakDescription(data.result.description);
            
        } catch (error) {
            console.error('Processing error:', error);
            this.showNotification(`❌ ${error.message}`, 'error');
            this.resetToUpload();
        } finally {
            this.processBtn.disabled = false;
        }
    }

    runDemo() {
        this.showLoading();
        // Simulate processing time for demo
        setTimeout(() => {
            this.showResults(this.demoData);
            this.speakDescription(this.demoData.description);
        }, 2500);
    }

    // Speech synthesis methods
    speakDescription(text) {
        if (!this.speechSynthesis) {
            this.showNotification('Speech synthesis not supported in this browser', 'error');
            return;
        }

        if (!text) {
            text = this.resultDescription?.textContent || '';
        }

        if (!text) return;

        // Stop any current speech
        this.stopSpeaking();

        // Create new utterance
        this.currentUtterance = new SpeechSynthesisUtterance(text);
        
        // Configure speech settings for museum-style narration
        this.currentUtterance.lang = 'en-US';
        this.currentUtterance.rate = 0.9; // Slower, more deliberate pace
        this.currentUtterance.pitch = 0.95; // Slightly lower pitch for authority
        this.currentUtterance.volume = 1.0;
        
        // Use preferred voice
        if (this.preferredVoice) {
            this.currentUtterance.voice = this.preferredVoice;
        }

        // Event listeners
        this.currentUtterance.onstart = () => {
            this.isPlaying = true;
            this.updateSpeechButtons();
        };

        this.currentUtterance.onend = () => {
            this.isPlaying = false;
            this.currentUtterance = null;
            this.updateSpeechButtons();
        };

        this.currentUtterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            this.isPlaying = false;
            this.currentUtterance = null;
            this.updateSpeechButtons();
        };

        // Start speaking
        this.speechSynthesis.speak(this.currentUtterance);
    }

    stopSpeaking() {
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
            this.isPlaying = false;
            this.currentUtterance = null;
            this.updateSpeechButtons();
        }
    }

    updateSpeechButtons() {
        if (this.speakBtn && this.stopSpeakBtn) {
            if (this.isPlaying) {
                this.speakBtn.style.display = 'none';
                this.stopSpeakBtn.style.display = 'inline-flex';
            } else {
                this.speakBtn.style.display = 'inline-flex';
                this.stopSpeakBtn.style.display = 'none';
            }
        }
    }

    // UI State Management
    showLoading() {
        this.uploadSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        this.loadingSection.classList.remove('hidden');
        
        // Stop any current speech
        this.stopSpeaking();
    }

    showResults(data) {
        this.loadingSection.classList.add('hidden');
        this.resultsSection.classList.remove('hidden');
        this.resultsSection.classList.add('success-animation');
        
        // Populate results
        this.resultTitle.textContent = data.title;
        this.resultDescription.textContent = data.description;
        this.resultObject.textContent = data.object_name;
        this.resultSource.textContent = data.sources;
        this.resultSource.href = data.sources;
        
        // Update speech buttons
        this.updateSpeechButtons();
        
        // Scroll to results
        this.resultsSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    resetToUpload() {
        this.resultsSection.classList.add('hidden');
        this.uploadSection.classList.remove('hidden');
        this.removeImage();
        
        // Stop any current speech
        this.stopSpeaking();
        
        // Scroll to top
        this.uploadSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    // Utility functions
    copyDescription() {
        const description = this.resultDescription.textContent;
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(description).then(() => {
                this.showNotification('Description copied to clipboard!', 'success');
            }).catch(() => {
                this.fallbackCopy(description);
            });
        } else {
            this.fallbackCopy(description);
        }
    }

    fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showNotification('Description copied to clipboard!', 'success');
        } catch (err) {
            this.showNotification('Failed to copy description', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    shareResult() {
        if (this.isPlaying) {
            this.stopSpeaking();
        }
        
        const shareData = {
            title: this.resultTitle.textContent,
            text: this.resultDescription.textContent.substring(0, 200) + '...',
            url: window.location.href
        };
        
        if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
            navigator.share(shareData).catch(err => {
                console.log('Error sharing:', err);
                this.fallbackShare();
            });
        } else {
            this.fallbackShare();
        }
    }

    fallbackShare() {
        const url = encodeURIComponent(window.location.href);
        const text = encodeURIComponent(this.resultTitle.textContent);
        const twitterUrl = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
        window.open(twitterUrl, '_blank', 'width=600,height=400');
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `copy-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            transition: opacity 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AutoMuseumApp();
});

// Add some smooth scrolling behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add intersection observer for animations
if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    // Observe cards for animation on scroll
    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(card);
    });
}