#!/usr/bin/env python3
"""
A.T.L.A.S. Main Server
Consolidated FastAPI server and web interface
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_core_ai import AtlasOrchestrator, AtlasAIEngine, PredictoConversationalEngine
from atlas_configuration import Settings, logger, AIResponse

settings = Settings()

app = FastAPI(
    title="A.T.L.A.S. - Advanced Trading & Learning Analytics System",
    description="Professional Trading Analysis System powered by AI",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator: Optional[AtlasOrchestrator] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    type: str
    confidence: float
    context: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize A.T.L.A.S. system on startup"""
    global orchestrator
    try:
        logger.info("🚀 Starting A.T.L.A.S. system initialization...")
        orchestrator = AtlasOrchestrator()
        await orchestrator.initialize_with_progress()
        logger.info("✅ A.T.L.A.S. system fully operational!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize A.T.L.A.S.: {e}")
        orchestrator = AtlasOrchestrator(validation_mode=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global orchestrator
    if orchestrator:
        await orchestrator.cleanup()
        logger.info("A.T.L.A.S. system shutdown complete")

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the main web interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A.T.L.A.S. - Advanced Trading & Learning Analytics System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .container {
            flex: 1;
            display: flex;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            gap: 20px;
        }
        
        .chat-section {
            flex: 2;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .sidebar {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            background: rgba(0, 0, 0, 0.2);
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        
        .user-message {
            background: rgba(74, 144, 226, 0.3);
            text-align: right;
        }
        
        .ai-message {
            background: rgba(46, 204, 113, 0.3);
            white-space: pre-wrap;
        }
        
        .input-section {
            display: flex;
            gap: 10px;
        }
        
        .input-section input {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
        }
        
        .input-section input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        .input-section button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            background: #4a90e2;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .input-section button:hover {
            background: #357abd;
        }
        
        .quick-actions {
            margin-bottom: 20px;
        }
        
        .quick-actions h3 {
            margin-bottom: 10px;
            color: #4a90e2;
        }
        
        .quick-btn {
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 8px;
            border: none;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .quick-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .status {
            padding: 10px;
            border-radius: 6px;
            background: rgba(46, 204, 113, 0.2);
            border: 1px solid rgba(46, 204, 113, 0.5);
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 3px solid #4a90e2;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 A.T.L.A.S.</h1>
        <p>Advanced Trading & Learning Analytics System</p>
    </div>
    
    <div class="container">
        <div class="chat-section">
            <h2>💬 Trading Assistant</h2>
            <div id="chatContainer" class="chat-container"></div>
            <div class="input-section">
                <input type="text" id="messageInput" placeholder="Ask me about trading, stocks, or market analysis..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>A.T.L.A.S. is analyzing...</p>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="quick-actions">
                <h3>🚀 Quick Actions</h3>
                <button class="quick-btn" onclick="quickMessage('Should I buy AAPL?')">Analyze AAPL</button>
                <button class="quick-btn" onclick="quickMessage('Scan for patterns')">Pattern Scanner</button>
                <button class="quick-btn" onclick="quickMessage('What are the best trades today?')">Best Trades</button>
                <button class="quick-btn" onclick="quickMessage('Help me make $100 today')">Profit Target</button>
                <button class="quick-btn" onclick="quickMessage('Show me portfolio optimization')">Portfolio Help</button>
            </div>
            
            <div class="status">
                <h3>📊 System Status</h3>
                <p>✅ Professional Trading Analyst Online</p>
                <p>✅ Market Data Connected</p>
                <p>✅ Pattern Detection Active</p>
                <p>✅ Risk Management Ready</p>
            </div>
        </div>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function quickMessage(message) {
            document.getElementById('messageInput').value = message;
            sendMessage();
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            const chatContainer = document.getElementById('chatContainer');
            const loading = document.getElementById('loading');
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Show loading
            loading.style.display = 'block';
            
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                // Hide loading
                loading.style.display = 'none';
                
                if (response.ok) {
                    addMessage(data.response, 'ai');
                } else {
                    addMessage('Error: ' + (data.detail || 'Unknown error'), 'ai');
                }
            } catch (error) {
                loading.style.display = 'none';
                addMessage('Error: Failed to connect to A.T.L.A.S.', 'ai');
            }
        }
        
        function addMessage(message, type) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Welcome message
        window.onload = function() {
            addMessage('Hello! I\'m A.T.L.A.S., your Professional Trading Analyst. I can help you with stock analysis, trading strategies, pattern detection, and market insights. What would you like to explore today?', 'ai');
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for trading analysis"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="A.T.L.A.S. system not initialized")
    
    try:
        response = await orchestrator.process_message(request.message, request.session_id)
        return ChatResponse(
            response=response.response,
            type=response.type,
            confidence=response.confidence,
            context=response.context
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    global orchestrator
    
    if not orchestrator:
        return {"status": "initializing", "message": "A.T.L.A.S. system starting up"}
    
    status = orchestrator.get_component_status()
    return {
        "status": "operational",
        "message": "A.T.L.A.S. Professional Trading Analyst online",
        "components": status
    }

@app.get("/api/v1/scan")
async def pattern_scanner():
    """Pattern scanning endpoint"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="A.T.L.A.S. system not initialized")
    
    try:
        response = await orchestrator.process_message("scan for patterns", None)
        return {"patterns": response.response, "confidence": response.confidence}
    except Exception as e:
        logger.error(f"Pattern scanner error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Starting A.T.L.A.S. Server...")
    uvicorn.run(
        "atlas_server:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
