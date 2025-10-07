// Chat application
class ChatApp {
    constructor() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.input = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.statusText = document.getElementById('status-text');
        this.statusDot = document.querySelector('.status-dot');
        
        this.conversationHistory = [];
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        // Send button click handler
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key handler (with Shift+Enter for new line)
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.input.addEventListener('input', () => {
            this.input.style.height = 'auto';
            this.input.style.height = this.input.scrollHeight + 'px';
        });
        
        // Focus input on load
        this.input.focus();
    }
    
    async sendMessage() {
        const message = this.input.value.trim();
        
        if (!message || this.isProcessing) {
            return;
        }
        
        // Clear input and reset height
        this.input.value = '';
        this.input.style.height = 'auto';
        
        // Add user message to UI
        this.addMessage(message, 'user');
        
        // Add to conversation history
        this.conversationHistory.push({
            role: 'user',
            content: message
        });
        
        // Set processing state
        this.setProcessing(true);
        
        // Show typing indicator
        const typingMessage = this.addTypingIndicator();
        
        try {
            // Call the API (streaming will handle displaying the message)
            const response = await this.callChatAPI(message);
            
            // Remove typing indicator
            typingMessage.remove();
            
            if (response) {
                // Add to conversation history only (message already displayed by streaming)
                this.conversationHistory.push({
                    role: 'assistant',
                    content: response
                });
            }
        } catch (error) {
            console.error('Error sending message:', error);
            typingMessage.remove();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant', true);
            this.setStatus('Error', 'error');
        } finally {
            this.setProcessing(false);
        }
    }
    
    async callChatAPI(message) {
        try {
            const response = await fetch('/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: this.conversationHistory,
                    stream: true,
                    call: {
                        id: this.generateConversationId(),
                        type: 'chat'
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = '';
            let messageElement = null;
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    break;
                }
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data === '[DONE]') {
                            continue;
                        }
                        
                        try {
                            const parsed = JSON.parse(data);
                            const content = parsed.choices?.[0]?.delta?.content;
                            
                            if (content) {
                                assistantMessage += content;
                                
                                // Update or create message element
                                if (!messageElement) {
                                    messageElement = this.addStreamingMessage();
                                }
                                this.updateStreamingMessage(messageElement, assistantMessage);
                            }
                        } catch (e) {
                            // Skip invalid JSON
                            console.warn('Failed to parse chunk:', data);
                        }
                    }
                }
            }
            
            return assistantMessage;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
    
    addMessage(content, role, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? '👤' : '🤖';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);
        
        if (isError) {
            contentDiv.style.background = '#fee2e2';
            contentDiv.style.color = '#991b1b';
            contentDiv.style.border = '1px solid #fecaca';
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        
        contentDiv.appendChild(typingDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    addStreamingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const p = document.createElement('p');
        contentDiv.appendChild(p);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    updateStreamingMessage(messageElement, content) {
        const p = messageElement.querySelector('.message-content p');
        p.textContent = content;
        this.scrollToBottom();
    }
    
    setProcessing(processing) {
        this.isProcessing = processing;
        this.sendButton.disabled = processing;
        this.input.disabled = processing;
        
        if (processing) {
            this.setStatus('Thinking...', 'thinking');
        } else {
            this.setStatus('Ready', 'ready');
        }
    }
    
    setStatus(text, state) {
        this.statusText.textContent = text;
        this.statusDot.className = 'status-dot';
        
        if (state === 'thinking') {
            this.statusDot.classList.add('thinking');
        } else if (state === 'error') {
            this.statusDot.classList.add('error');
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    generateConversationId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}

// Initialize the chat app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

