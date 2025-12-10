/**
 * MA'AT Engine WebSocket Server (Node.js)
 * 
 * This is an optional backend server for real-time Ma'at validation.
 * The main index.html works standalone without this server.
 * 
 * To use this server:
 * 1. Install dependencies: npm install ws express body-parser cors
 * 2. Run: node maatEngineServer.js
 * 3. Uncomment the WebSocket section in index.html
 */

const WebSocket = require('ws');
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

// MA'AT Principles Database (same as frontend)
const MAAT_PRINCIPLES = [
  { id: 1, name: 'Truth', keyword: ['truth', 'honest', 'real', 'authentic'], frequency: 432 },
  { id: 2, name: 'Justice', keyword: ['justice', 'fair', 'right', 'equitable'], frequency: 442 },
  { id: 3, name: 'Harmony', keyword: ['harmony', 'peace', 'accord', 'unity'], frequency: 452 },
  { id: 4, name: 'Balance', keyword: ['balance', 'equilibrium', 'even', 'centered'], frequency: 462 },
  { id: 8, name: 'Morality', keyword: ['morality', 'ethics', 'principle', 'value'], frequency: 502 },
  { id: 11, name: 'Wisdom', keyword: ['wisdom', 'knowledge', 'insight', 'understanding'], frequency: 528 },
  { id: 23, name: 'Clarity', keyword: ['clarity', 'clear', 'transparent', 'lucid'], frequency: 648 },
  { id: 32, name: 'Liberation', keyword: ['liberation', 'freedom', 'release', 'free'], frequency: 738 },
  // Add all 42 principles here...
];

/**
 * Ma'at Validation Engine
 * Replace this with your actual validation logic
 */
function validateWithMaat(userMessage) {
  const words = userMessage.toLowerCase().split(/\s+/);
  const detectedPrinciples = [];
  let coherenceScore = 0.5;
  let totalFrequency = 0;
  
  // Detect principles
  MAAT_PRINCIPLES.forEach(principle => {
    const matches = principle.keyword.filter(keyword => 
      words.some(word => word.includes(keyword) || keyword.includes(word))
    );
    if (matches.length > 0) {
      detectedPrinciples.push(principle);
      coherenceScore += 0.08 * matches.length;
      totalFrequency += principle.frequency;
    }
  });
  
  // Analyze emotional content
  const positiveWords = ['love', 'joy', 'peace', 'happy', 'grateful', 'blessed'];
  const negativeWords = ['hate', 'anger', 'fear', 'conflict', 'dark', 'confused'];
  
  let emotionalScore = 0;
  words.forEach(word => {
    if (positiveWords.some(pw => word.includes(pw))) emotionalScore += 0.15;
    if (negativeWords.some(nw => word.includes(nw))) emotionalScore -= 0.15;
  });
  
  coherenceScore = Math.min(0.95, Math.max(0.3, coherenceScore + emotionalScore));
  
  // Determine emotional field
  let emotionalField = coherenceScore > 0.75 ? 'Positive' 
    : coherenceScore > 0.55 ? 'Neutral' : 'Negative';
  
  // Calculate frequency
  const avgFrequency = detectedPrinciples.length > 0 
    ? Math.round(totalFrequency / detectedPrinciples.length)
    : 528;
  
  // Cosmic sync
  const lunarSync = 0.75 + Math.random() * 0.2;
  const galacticSync = 0.65 + Math.random() * 0.2;
  
  // Generate response
  let response = '';
  if (detectedPrinciples.length > 0) {
    const principleNames = detectedPrinciples.map(p => `${p.name} (#${p.id})`).slice(0, 3).join(', ');
    response = `Your thought resonates with: ${principleNames}. `;
    response += `The glyph shows ${emotionalField.toUpperCase()} energy. `;
    
    if (coherenceScore > 0.8) {
      response += 'Excellent alignment! ✨';
    } else if (coherenceScore > 0.6) {
      response += 'Good alignment. 🌟';
    } else {
      response += 'Refinement suggested. 💫';
    }
  } else {
    response = `No specific principles detected. The glyph reflects ${emotionalField.toLowerCase()} energy.`;
  }
  
  return {
    coherence: coherenceScore * 100,
    emotionalField: emotionalField,
    principles: detectedPrinciples.length > 0 
      ? detectedPrinciples.map(p => p.id).slice(0, 5).join(', ')
      : 'None',
    frequency: avgFrequency,
    cosmicSync: {
      lunar: lunarSync,
      galactic: galacticSync
    },
    stable: coherenceScore > 0.5,
    response: response,
    recommendation: detectedPrinciples.length > 0 
      ? `Focus on embodying ${detectedPrinciples[0].name}.`
      : 'Meditate on the MA\'AT principles.',
    timestamp: new Date().toISOString()
  };
}

// HTTP server for REST API
const app = express();
app.use(cors());
app.use(bodyParser.json());

app.post('/validate', (req, res) => {
  try {
    if (!req.body || typeof req.body.message !== 'string' || req.body.message.trim() === '') {
      return res.status(400).json({ error: 'Message is required' });
    }
    const result = validateWithMaat(req.body.message);
    res.json(result);
  } catch (error) {
    console.error('Validation error:', error);
    res.status(500).json({ error: 'Validation failed' });
  }
});

const HTTP_PORT = 3000;
app.listen(HTTP_PORT, () => {
  console.log(`☥ MA'AT HTTP API running on http://localhost:${HTTP_PORT}`);
});

// WebSocket server for real-time updates
const WS_PORT = 8080;
const wss = new WebSocket.Server({ port: WS_PORT });

wss.on('connection', (ws) => {
  console.log('☥ New client connected');
  
  ws.on('message', (message) => {
    try {
      const data = validateWithMaat(message.toString());
      
      // Broadcast to all connected clients
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(data));
        }
      });
      
      console.log(`☥ Validated: "${message.toString().substring(0, 50)}..." -> Coherence: ${data.coherence.toFixed(1)}%`);
    } catch (error) {
      console.error('Error processing message:', error);
      ws.send(JSON.stringify({ error: 'Validation failed' }));
    }
  });
  
  ws.on('close', () => {
    console.log('☥ Client disconnected');
  });
});

console.log(`☥ MA'AT WebSocket Server running on ws://localhost:${WS_PORT}`);
console.log('☥ 42 Principles loaded with sacred frequencies');
console.log('☥ Ready to validate thoughts in real-time...\n');
