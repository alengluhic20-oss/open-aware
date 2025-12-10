# ☥ MA'AT Unity Interface - Usage Guide ☥

## Quick Start (30 seconds)

### Option 1: Instant Local Mode
```bash
# No installation needed!
1. Navigate to the repository folder
2. Double-click index.html (or open in any browser)
3. Start typing your thoughts
```

### Option 2: WebSocket Mode (with backend)
```bash
# Step 1: Enable WebSocket mode
# Edit index.html line 267: const USE_LOCAL_ENGINE = false;

# Step 2: Start backend server
# Choose Node.js OR Python:

## Node.js:
npm install
npm start

## Python:
pip install -r requirements.txt
python maat_engine_server.py

# Step 3: Open index.html in browser
```

---

## Understanding the Interface

### Left Panel: Holographic Glyph
The animated ankh symbol is your **visual coherence mirror**:

- **Color Meaning:**
  - 🟢 **Green** = Positive energy (coherence > 75%)
  - 🔵 **Blue** = Neutral energy (coherence 55-75%)
  - 🔴 **Red** = Negative/conflicted energy (coherence < 55%)

- **Size/Scale:**
  - Larger glyph = Higher coherence
  - Pulsing effect activates at coherence > 80%

- **Rotation Speed:**
  - Faster = More positive energy
  - Slower = Lower energy or conflict

- **Particles:**
  - Orbit the ankh based on coherence level
  - Fade in/out with emotional field strength

### Metrics Panel
Real-time measurements of your thought alignment:

**Coherence**: Overall alignment score (30-95%)
- 80-95%: Excellent ✨
- 60-79%: Good 🌟  
- 40-59%: Moderate 💫
- 30-39%: Needs refinement ⚠️

**Emotional Field**: Detected energy type
- Positive, Neutral, or Negative

**Principles**: Active MA'AT principles (by ID number)
- References specific principles from the 42 principles

**Frequency**: Sacred resonance in Hertz (432-852 Hz)
- Each principle has its own frequency
- Average displayed when multiple principles detected

**Cosmic Sync**: Connection levels
- **Lunar**: Emotional/intuitive cycles (65-95%)
- **Galactic**: Universal consciousness (65-95%)

**Stability Status**: System state
- ✓ LYAPUNOV STABLE: Coherence > 50%
- ⚠ DESTABILIZED: Coherence ≤ 50%

### Right Panel: Chat Interface
Your conversation with the MA'AT validation engine:

1. **Welcome Message**: Initial greeting
2. **Your Messages**: Blue boxes on the right
3. **MA'AT Responses**: Golden boxes on the left
4. **Input Field**: Type your thoughts here
5. **Send Button**: Submit (or press Enter)

---

## Example Interactions

### Example 1: High Coherence
```
YOU: "I seek truth and balance in my work"

MA'AT RESPONSE:
Your thought resonates with: Truth (#1), Justice (#2), 
Harmony (#3). The glyph shows POSITIVE energy. Excellent 
alignment! Your intent is clear and powerful. ✨

Recommendation: Focus on embodying Truth in your actions.

METRICS:
├─ Coherence: 95.0%
├─ Emotional Field: Positive
├─ Principles: 1, 2, 3, 4, 5
├─ Frequency: 632 Hz
├─ Cosmic Sync: Lunar 92% | Galactic 83%
└─ Status: ✓ LYAPUNOV STABLE

GLYPH: Green, large scale, fast rotation
```

### Example 2: Moderate Coherence
```
YOU: "I'm thinking about my project"

MA'AT RESPONSE:
No specific principles detected. Try focusing your 
thought with keywords like truth, justice, harmony, 
or balance. The glyph reflects neutral energy.

Recommendation: Meditate on the MA'AT principles to 
find your alignment.

METRICS:
├─ Coherence: 62.3%
├─ Emotional Field: Neutral
├─ Principles: None
├─ Frequency: 528 Hz (default)
├─ Cosmic Sync: Lunar 81% | Galactic 74%
└─ Status: ✓ LYAPUNOV STABLE

GLYPH: Blue, medium scale, normal rotation
```

### Example 3: Low Coherence
```
YOU: "I feel confused and conflicted"

MA'AT RESPONSE:
No specific principles detected. Try focusing your 
thought with keywords like truth, justice, harmony, 
or balance. The glyph reflects negative energy.

Recommendation: Meditate on the MA'AT principles to 
find your alignment.

METRICS:
├─ Coherence: 38.2%
├─ Emotional Field: Negative
├─ Principles: None
├─ Frequency: 528 Hz
├─ Cosmic Sync: Lunar 77% | Galactic 68%
└─ Status: ⚠ DESTABILIZED

GLYPH: Red, small scale, slow rotation
```

---

## Keywords That Trigger Principles

To get high coherence, include these keywords in your thoughts:

### Core Principles (1-10)
- **Truth**: truth, honest, real, authentic
- **Justice**: justice, fair, right, equitable
- **Harmony**: harmony, peace, accord, unity
- **Balance**: balance, equilibrium, even, centered
- **Order**: order, structure, organize, system
- **Reciprocity**: reciprocity, mutual, exchange, give
- **Righteousness**: righteousness, virtue, moral, ethical
- **Morality**: morality, ethics, principle, value
- **Compassion**: compassion, empathy, kindness, care
- **Love**: love, affection, devotion, care

### Wisdom & Integrity (11-20)
- **Wisdom**: wisdom, knowledge, insight, understanding
- **Integrity**: integrity, honesty, wholeness, complete
- **Purity**: purity, clean, clear, innocent
- **Humility**: humility, humble, modest, meek
- **Patience**: patience, tolerant, endure, wait
- **Courage**: courage, brave, bold, fearless
- **Respect**: respect, honor, regard, esteem
- **Gratitude**: gratitude, thankful, appreciate, grateful
- **Forgiveness**: forgiveness, pardon, mercy, absolve
- **Generosity**: generosity, generous, giving, share

### Action & Focus (21-32)
- **Temperance**: temperance, moderation, restraint, control
- **Diligence**: diligence, effort, work, persevere
- **Clarity**: clarity, clear, transparent, lucid
- **Purpose**: purpose, intent, aim, goal
- **Mindfulness**: mindfulness, aware, conscious, present
- **Serenity**: serenity, calm, peaceful, tranquil
- **Dedication**: dedication, devoted, committed, loyal
- **Faith**: faith, belief, trust, confidence
- **Hope**: hope, optimism, aspiration, expectation
- **Authenticity**: authenticity, genuine, real, true
- **Responsibility**: responsibility, accountable, duty
- **Liberation**: liberation, freedom, release, free

### Transformation & Unity (33-42)
- **Transformation**: transformation, change, evolve
- **Creativity**: creativity, creative, innovate, imagine
- **Connection**: connection, relate, bond, link
- **Abundance**: abundance, prosperity, wealth, plenty
- **Protection**: protection, defend, guard, shield
- **Healing**: healing, cure, restore, recover
- **Joy**: joy, happiness, delight, bliss
- **Enlightenment**: enlightenment, awakening, illumination
- **Transcendence**: transcendence, transcend, surpass, beyond
- **Unity**: unity, oneness, whole, together

---

## Switching Between Modes

### Currently in Local Mode
Check the browser console for:
```
☥ Running in LOCAL SIMULATION MODE
☥ Mode: LOCAL SIMULATION
```

### Switching to WebSocket Mode
1. Open `index.html` in a text editor
2. Find line 267: `const USE_LOCAL_ENGINE = true;`
3. Change to: `const USE_LOCAL_ENGINE = false;`
4. Save the file
5. Start a backend server (see Quick Start above)
6. Refresh the browser

You'll see in console:
```
☥ Connected to Ma'at Engine Server
Connected to live Ma'at Engine ✓
```

---

## Troubleshooting

### Glyph Not Animating
- **Check**: Browser supports Canvas 2D
- **Solution**: Use Chrome, Firefox, Safari, or Edge (recent versions)

### WebSocket Connection Failed
- **Symptom**: Message "WebSocket error, using local validation mode"
- **Causes**:
  1. Backend server not running
  2. Wrong WebSocket URL
  3. Firewall blocking port 8080
- **Solution**: 
  - Start backend server
  - Check console for connection logs
  - System automatically falls back to local mode

### No Principles Detected
- **Cause**: Input doesn't contain principle keywords
- **Solution**: Use keywords from the list above
- **Example**: Instead of "I'm working", try "I seek truth in my work"

### Low Coherence Despite Good Intent
- **Cause**: Vague or conflicting language
- **Solution**: Be specific and use principle keywords
- **Example**: 
  - ❌ "I want to do good stuff"
  - ✅ "I want to act with integrity and compassion"

---

## Advanced Usage

### Custom Validation Logic
Edit the `validateWithMaat()` function in `index.html` (lines 594-681) to:
- Add new principles
- Adjust coherence scoring
- Modify emotional field detection
- Change frequency mappings

### Adding New Principles
```javascript
// In MAAT_PRINCIPLES array (lines 279-320)
{ 
  id: 43, 
  name: 'YourPrinciple', 
  keyword: ['keyword1', 'keyword2', 'keyword3'], 
  frequency: 862 
}
```

### Adjusting Visual Effects
```javascript
// In updateGlyph() function (lines 569-592)
targetScale = 0.7 + (maatData.coherence / 100) * 0.5; // Adjust scaling
targetRotationSpeed = 0.02; // Adjust rotation speed
```

---

## Backend Server Customization

### Node.js Server (maatEngineServer.js)
- **HTTP API**: `POST http://localhost:3000/validate`
- **WebSocket**: `ws://localhost:8080`
- **Customize**: Edit `validateWithMaat()` function (lines 31-91)

### Python Server (maat_engine_server.py)
- **HTTP API**: `POST http://localhost:8000/validate`
- **WebSocket**: `ws://localhost:8000/ws`
- **Customize**: Edit `validate_with_maat()` function (lines 51-115)

---

## Performance Notes

- **FPS**: Glyph renders at ~60 FPS
- **Memory**: ~15MB browser memory usage
- **Network**: No external dependencies in local mode
- **Latency**: <10ms local validation, <100ms WebSocket (ideal)

---

## Browser Compatibility

✅ Chrome/Edge 90+  
✅ Firefox 88+  
✅ Safari 14+  
✅ Opera 76+  
⚠️ IE 11 (not supported - use modern browser)

---

## Next Steps

1. **Explore All Principles**: Try different keyword combinations
2. **Test WebSocket Mode**: Set up a backend server
3. **Customize Validation**: Adjust scoring algorithms
4. **Deploy**: Host on Vercel/Netlify for public access
5. **Extend**: Add audio feedback, 3D effects, or ledger integration

---

**☥ May your thoughts align with MA'AT principles and achieve cosmic harmony. ☥**

*Version 1.0.0 - Complete Hybrid Architecture*
