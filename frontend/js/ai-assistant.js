/**
 * AI Assistant Module
 * Handles natural language queries using Bedrock
 */

class AIAssistant {
    constructor() {
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendChatBtn');
        this.chatMessages = document.getElementById('chatMessages');
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.addWelcomeMessage();
    }

    setupEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    addWelcomeMessage() {
        this.addMessage('Hi! I\'m your ADR scanner assistant. Ask me about crossings, filters, or insights.', 'assistant');
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Determine query type
        let queryType = 'filter';
        if (message.toLowerCase().includes('summary') || 
            message.toLowerCase().includes('total') ||
            message.toLowerCase().includes('how many')) {
            queryType = 'summary';
        } else if (message.toLowerCase().includes('explain') ||
                   message.toLowerCase().includes('why')) {
            queryType = 'explain';
        }
        
        try {
            authManager.showLoading(true);
            
            const headers = authManager.getAuthHeaders();
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    query: message,
                    type: queryType
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            // Handle different response types
            if (data.response_type === 'filters') {
                this.addMessage(data.message, 'assistant');
                if (data.filters) {
                    this.applyAIFilters(data.filters);
                }
                if (data.disclaimer) {
                    this.addMessage(data.disclaimer, 'assistant');
                }
            } else if (data.response_type === 'summary') {
                this.addMessage(data.message, 'assistant');
                if (data.disclaimer) {
                    this.addMessage(data.disclaimer, 'assistant');
                }
            } else if (data.response_type === 'text') {
                this.addMessage(data.message, 'assistant');
                if (data.disclaimer) {
                    this.addMessage(data.disclaimer, 'assistant');
                }
            } else if (data.response_type === 'error') {
                this.addMessage('Sorry, I couldn\'t process that query. ' + data.message, 'assistant');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, an error occurred. Please try again.', 'assistant');
        } finally {
            authManager.showLoading(false);
        }
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.textContent = text;
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    applyAIFilters(filters) {
        // Apply filters from AI interpretation
        if (filters.direction) {
            document.getElementById('directionFilter').value = filters.direction;
        }
        if (filters.min_price) {
            document.getElementById('minPrice').value = filters.min_price;
        }
        if (filters.min_volume_ratio) {
            document.getElementById('minVolume').value = filters.min_volume_ratio;
        }
        if (filters.adr_pct_min) {
            document.getElementById('minADR').value = filters.adr_pct_min;
        }
        if (filters.adr_pct_max) {
            document.getElementById('maxADR').value = filters.adr_pct_max;
        }
        
        // Trigger filter application
        if (window.dashboard) {
            window.dashboard.applyFilters();
        }
    }
}

// Initialize AI assistant when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (authManager.isAuthenticated()) {
            window.aiAssistant = new AIAssistant();
        }
    }, 100);
});
