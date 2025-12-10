"""
MA'AT Engine WebSocket Server (Python/FastAPI)

This is an optional backend server for real-time Ma'at validation.
The main index.html works standalone without this server.

To use this server:
1. Install dependencies: pip install fastapi uvicorn websockets
2. Run: python maat_engine_server.py
3. Uncomment the WebSocket section in index.html
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from datetime import datetime
from typing import List, Dict
import re

app = FastAPI(title="MA'AT Engine API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MA'AT Principles Database
MAAT_PRINCIPLES = [
    {"id": 1, "name": "Truth", "keywords": ["truth", "honest", "real", "authentic"], "frequency": 432},
    {"id": 2, "name": "Justice", "keywords": ["justice", "fair", "right", "equitable"], "frequency": 442},
    {"id": 3, "name": "Harmony", "keywords": ["harmony", "peace", "accord", "unity"], "frequency": 452},
    {"id": 4, "name": "Balance", "keywords": ["balance", "equilibrium", "even", "centered"], "frequency": 462},
    {"id": 5, "name": "Order", "keywords": ["order", "structure", "organize", "system"], "frequency": 472},
    {"id": 8, "name": "Morality", "keywords": ["morality", "ethics", "principle", "value"], "frequency": 502},
    {"id": 11, "name": "Wisdom", "keywords": ["wisdom", "knowledge", "insight", "understanding"], "frequency": 528},
    {"id": 23, "name": "Clarity", "keywords": ["clarity", "clear", "transparent", "lucid"], "frequency": 648},
    {"id": 32, "name": "Liberation", "keywords": ["liberation", "freedom", "release", "free"], "frequency": 738},
    # Add all 42 principles here...
]

class ValidationRequest(BaseModel):
    message: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"☥ New client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"☥ Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

def validate_with_maat(user_message: str) -> Dict:
    """
    MA'AT Validation Engine
    Replace this with your actual validation logic
    """
    words = re.findall(r'\w+', user_message.lower())
    detected_principles = []
    coherence_score = 0.5
    total_frequency = 0
    
    # Detect principles
    for principle in MAAT_PRINCIPLES:
        matches = [kw for kw in principle["keywords"] 
                  if any(kw in word or word in kw for word in words)]
        if matches:
            detected_principles.append(principle)
            coherence_score += 0.08 * len(matches)
            total_frequency += principle["frequency"]
    
    # Analyze emotional content
    positive_words = ["love", "joy", "peace", "happy", "grateful", "blessed", "hope", "light"]
    negative_words = ["hate", "anger", "fear", "conflict", "dark", "confused", "lost", "doubt"]
    
    emotional_score = 0
    for word in words:
        if any(pw in word for pw in positive_words):
            emotional_score += 0.15
        if any(nw in word for nw in negative_words):
            emotional_score -= 0.15
    
    coherence_score = min(0.95, max(0.3, coherence_score + emotional_score))
    
    # Determine emotional field
    emotional_field = "Positive" if coherence_score > 0.75 else \
                     "Neutral" if coherence_score > 0.55 else "Negative"
    
    # Calculate frequency
    avg_frequency = round(total_frequency / len(detected_principles)) if detected_principles else 528
    
    # Cosmic sync (simulated)
    import random
    lunar_sync = 0.75 + random.random() * 0.2
    galactic_sync = 0.65 + random.random() * 0.2
    
    # Generate response
    if detected_principles:
        principle_names = ", ".join([f"{p['name']} (#{p['id']})" 
                                    for p in detected_principles[:3]])
        response = f"Your thought resonates with: {principle_names}. "
        response += f"The glyph shows {emotional_field.upper()} energy. "
        
        if coherence_score > 0.8:
            response += "Excellent alignment! ✨"
        elif coherence_score > 0.6:
            response += "Good alignment. 🌟"
        else:
            response += "Refinement suggested. 💫"
    else:
        response = f"No specific principles detected. The glyph reflects {emotional_field.lower()} energy."
    
    return {
        "coherence": coherence_score * 100,
        "emotionalField": emotional_field,
        "principles": ", ".join([str(p["id"]) for p in detected_principles[:5]]) if detected_principles else "None",
        "principleNames": [p["name"] for p in detected_principles[:3]],
        "frequency": avg_frequency,
        "cosmicSync": {
            "lunar": lunar_sync,
            "galactic": galactic_sync
        },
        "stable": coherence_score > 0.5,
        "response": response,
        "recommendation": f"Focus on embodying {detected_principles[0]['name']}." if detected_principles 
                         else "Meditate on the MA'AT principles.",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/validate")
async def validate_message(request: ValidationRequest):
    """REST API endpoint for Ma'at validation"""
    result = validate_with_maat(request.message)
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Ma'at validation"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Validate with Ma'at
            result = validate_with_maat(data)
            
            # Broadcast to all clients
            await manager.broadcast(json.dumps(result))
            
            print(f"☥ Validated: \"{data[:50]}...\" -> Coherence: {result['coherence']:.1f}%")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "service": "MA'AT Engine API",
        "version": "1.0.0",
        "endpoints": {
            "POST /validate": "REST API for validation",
            "WS /ws": "WebSocket for real-time validation"
        },
        "principles": len(MAAT_PRINCIPLES),
        "status": "☥ Ready to validate thoughts in real-time"
    }

if __name__ == "__main__":
    print("=" * 60)
    print("☥ MA'AT ENGINE SERVER")
    print("=" * 60)
    print(f"☥ HTTP API: http://localhost:8000")
    print(f"☥ WebSocket: ws://localhost:8000/ws")
    print(f"☥ {len(MAAT_PRINCIPLES)} Principles loaded with sacred frequencies")
    print(f"☥ Ready to validate thoughts in real-time...")
    print("=" * 60)
    print()
    
    # For development, bind to localhost only for security.
    # To expose externally, use host="0.0.0.0" and ensure proper authentication/firewall.
    uvicorn.run(app, host="127.0.0.1", port=8000)
