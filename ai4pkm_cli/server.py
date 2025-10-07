"""Web server for AI4PKM."""

import threading
import json
import time
import os
import re
from flask import Flask, request, jsonify, Response, send_from_directory, abort
from .config import Config
from .logger import Logger
from .agent_factory import AgentFactory

class Server:
    """Web server for Vapi integration and a web application."""
    
    def __init__(self, logger: Logger, config: Config):
        """Initialize the web server."""
        self.logger = logger
        self.config = config
        self.port = self.config.get_web_api_port()
        self.agent = AgentFactory.create_agent(logger, config)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.web_app_dir = os.path.join(base_dir, "web_app")
        
        self.app = Flask(__name__, static_folder=os.path.join(self.web_app_dir, 'static'))
        
        self._setup_routes()
        
        self.server_thread = None
        self.is_running = False
    
    def _setup_routes(self):
        """Setup API routes."""

        # Chat UI route
        @self.app.route("/chat")
        def chat_ui():
            return send_from_directory(self.web_app_dir, "chat.html")

        # Route for the web application - serves index.html for any non-API path
        @self.app.route("/", defaults={'path': ''})
        @self.app.route("/<path:path>")
        def catch_all(path):
            return send_from_directory(self.web_app_dir, "index.html")
        
        @self.app.route("/api/gobi-log/<filename>")
        def gobi_log(filename):
            """Parse and return a specific Gobi log file."""
            try:
                # Basic security: ensure filename is just a filename
                if "/" in filename or ".." in filename:
                    abort(400)
                
                log_file_path = os.path.join(os.getcwd(), "Ingest/Gobi", filename)
                if not os.path.exists(log_file_path):
                    return jsonify({"error": f"Log file '{filename}' not found"}), 404
                
                log_file_dir = os.path.dirname(log_file_path)
                log_data = []
                # Regex to capture timestamp, optional image path, and transcription
                line_regex = re.compile(
                    r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s"  # Timestamp
                    r"(?:!\[frame\]\((.*?)\)\s*)?"              # Optional image path
                    r"(.*)"                                     # Transcription
                )

                with open(log_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        match = line_regex.match(line.strip())
                        if match:
                            timestamp, image_path, text = match.groups()
                            
                            if text:
                                log_data.append({
                                    "timestamp": timestamp,
                                    "type": "transcription",
                                    "content": text.strip()
                                })
                            
                            if image_path:
                                # Resolve the image path relative to the markdown file
                                full_image_path = os.path.abspath(os.path.join(log_file_dir, image_path))
                                # Get path relative to project root to be served
                                relative_image_path = os.path.relpath(full_image_path, os.getcwd())
                                # Create a URL-friendly path for the API
                                api_image_path = os.path.join('/files', relative_image_path).replace(os.path.sep, '/')

                                log_data.append({
                                    "timestamp": timestamp,
                                    "type": "image",
                                    "path": api_image_path
                                })
                
                return jsonify(log_data)
            except Exception as e:
                self.logger.error(f"Error processing Gobi log: {e}")
                return jsonify({"error": "Could not process log file"}), 500

        @self.app.route('/files/<path:filepath>')
        def serve_file(filepath):
            """Serve files from the vault root."""
            return send_from_directory(os.getcwd(), filepath)

        # Route for Vapi Integration
        @self.app.route("/chat/completions", methods=["POST"])
        def chat_completions():
            """Vapi-compatible chat completions endpoint."""
            try:
                # Get JSON data from request
                data = request.get_json()
                is_voice = False
                if data.get('call', {}).get('type', '') == 'webCall':
                    # This is a voice call
                    is_voice = True
                
                # Extract the latest user message from messages array
                messages = data.get('messages', [])
                user_messages = [msg for msg in messages if msg.get('role') == 'user']
                if not user_messages:
                    return jsonify({"error": "No user message found in messages"}), 400
                    
                message = user_messages[-1].get('content', '')
                conversation_id = data.get('call', {}).get('id')
                
                self.logger.info(f"Received chat completions request: {message[:100]}...")
                
                # Check if streaming is requested
                stream = data.get('stream', False)
                
                if stream:
                    # Return SSE streaming response
                    def generate_stream():
                        # Execute the prompt using the configured agent
                        result = self.agent.run_prompt(inline_prompt=message)
                        created = int(time.time())

                        if result and result[0]:
                            response_text = result[0]
                            if is_voice:
                                # Optimize response for voice interaction
                                response_text = self._optimize_for_voice(response_text)
                                self.logger.info(f"Generated response (optimized for voice)\n{response_text}")
                            else:
                                self.logger.info(f"Generated response: {len(response_text)} characters")
                            
                            # Split response into chunks for streaming
                            if is_voice:
                                # For voice, split by words (removes newlines)
                                words = response_text.split(' ')
                                chunk_size = 5  # Stream 5 words at a time
                                
                                for i in range(0, len(words), chunk_size):
                                    chunk_words = words[i:i + chunk_size]
                                    chunk_text = " ".join(chunk_words)
                                    
                                    # Create SSE chunk in Vapi format
                                    chunk_data = {
                                        "id": f"resp_{conversation_id}",
                                        "object": "chat.completion.chunk",
                                        "created": created,
                                        "model": "ai4pkm",
                                        "choices": [{
                                            "index": 0,
                                            "delta": {
                                                "role": "assistant",
                                                "content": chunk_text + (" " if i + chunk_size < len(words) else "")
                                            },
                                            "logprobs": None,
                                            "finish_reason": None
                                        }]
                                    }
                                    
                                    yield f"data: {json.dumps(chunk_data)}\n\n"
                            else:
                                # For text chat, stream by characters to preserve newlines
                                chunk_size = 50  # Stream 50 characters at a time
                                
                                for i in range(0, len(response_text), chunk_size):
                                    chunk_text = response_text[i:i + chunk_size]
                                    
                                    # Create SSE chunk in Vapi format
                                    chunk_data = {
                                        "id": f"resp_{conversation_id}",
                                        "object": "chat.completion.chunk",
                                        "created": created,
                                        "model": "ai4pkm",
                                        "choices": [{
                                            "index": 0,
                                            "delta": {
                                                "role": "assistant",
                                                "content": chunk_text
                                            },
                                            "logprobs": None,
                                            "finish_reason": None
                                        }]
                                    }
                                    
                                    yield f"data: {json.dumps(chunk_data)}\n\n"
                            
                            # Send final chunk to indicate completion
                            final_chunk = {
                                "id": f"resp_{conversation_id}",
                                "object": "chat.completion.chunk",
                                "created": created,
                                "model": "ai4pkm",
                                "choices": [{
                                    "index": 0,
                                    "delta": {},
                                    "logprobs": None,
                                    "finish_reason": "stop"
                                }]
                            }
                            yield f"data: {json.dumps(final_chunk)}\n\n"
                            yield "data: [DONE]\n\n"
                        else:
                            error_chunk = {
                                "id": f"resp_{conversation_id}",
                                "object": "chat.completion.chunk",
                                "created": created,
                                "model": "ai4pkm",
                                "choices": [{
                                    "index": 0,
                                    "delta": {
                                        "role": "assistant",
                                        "content": "I couldn't find information about that. Could you try asking in a different way?"
                                    },
                                    "logprobs": None,
                                    "finish_reason": None
                                }]
                            }
                            yield f"data: {json.dumps(error_chunk)}\n\n"
                            
                            final_chunk = {
                                "id": f"resp_{conversation_id}",
                                "object": "chat.completion.chunk",
                                "created": created,
                                "model": "ai4pkm",
                                "choices": [{
                                    "index": 0,
                                    "delta": {},
                                    "logprobs": None,
                                    "finish_reason": "stop"
                                }]
                            }
                            yield f"data: {json.dumps(final_chunk)}\n\n"
                            yield "data: [DONE]\n\n"
                    
                    return Response(
                        generate_stream(),
                        mimetype='text/event-stream',
                        headers={
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Headers': 'Cache-Control'
                        }
                    )
                else:
                    # Non-streaming response (original behavior)
                    result = self.agent.run_prompt(inline_prompt=message)
                    
                    if result and result[0]:
                        response_text = result[0]
                        # Optimize response for voice interaction
                        response_text = self._optimize_for_voice(response_text)
                        self.logger.info(f"Generated response: {len(response_text)} characters")
                    else:
                        response_text = "I couldn't find information about that. Could you try asking in a different way?"
                        self.logger.warning("No response generated from agent")
                    
                    # Return Vapi-compatible response format
                    return jsonify({
                        "id": f"resp_{conversation_id}",
                        "object": "chat.completion",
                        "created": time.time(),
                        "model": "ai4pkm",
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_text
                            },
                            "logprobs": None,
                            "finish_reason": "stop"
                        }]
                    })
                
            except Exception as e:
                self.logger.error(f"Error in chat completions endpoint: {e}")
                return jsonify({
                    "error": "I'm having trouble processing that request right now. Please try again."
                }), 500
    
    def _optimize_for_voice(self, text: str) -> str:
        """Optimize text response for voice interaction."""
        # Remove markdown formatting
        text = text.replace("**", "").replace("*", "").replace("_", "")
        text = text.replace("#", "").replace("`", "")
        
        # Replace common symbols with words
        text = text.replace("&", "and")
        text = text.replace("@", "at")
        text = text.replace("%", "percent")
        text = text.replace("$", "dollars")
        
        # Remove excessive line breaks and normalize spacing
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = ' '.join(lines)
        
        # Limit response length for voice (aim for ~30 seconds of speech)
        max_chars = 800
        if len(text) > max_chars:
            # Try to cut at sentence boundary
            sentences = text.split('. ')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + '. ') <= max_chars:
                    truncated += sentence + '. '
                else:
                    break
            if truncated:
                text = truncated.rstrip()
            else:
                text = text[:max_chars] + "..."
        
        return text
    
    def start_server(self):
        """Start the web API server in a separate thread."""
        if self.is_running:
            self.logger.warning("Web API server is already running")
            return
        
        def run_server():
            """Run the server in a separate thread."""
            try:
                self.logger.info(f"Starting Web API server on port {self.port}")
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.ERROR)
                
                self.app.run(
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                self.logger.error(f"Error starting web API server: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        
    def stop_server(self):
        """Stop the web API server."""
        if not self.is_running:
            return
        
        # Flask server will stop when the thread is terminated
        self.is_running = False
        self.logger.info("Web API server stopped")
    
    def is_server_running(self) -> bool:
        """Check if the server is running."""
        return self.is_running
