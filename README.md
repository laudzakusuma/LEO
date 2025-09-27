# 🤖 L.E.O (Living Entity Online)

## ✨ Features

### Core Features
- 🎤 **Voice Interaction** - Real-time voice input/output dengan ElevenLabs
- 🌐 **Futuristic Web UI** - Interface seperti JARVIS dengan animasi Arc Reactor
- 🔊 **Audio Visualizer** - Real-time audio waveform visualization
- 💬 **Chat History** - Menyimpan riwayat percakapan

### Enhanced Tools
- 🔍 **Web Search** - Pencarian informasi dari internet
- 🎨 **Image Generation** - Generate gambar dengan DALL-E 3
- 🌤️ **Weather Information** - Info cuaca real-time
- 🌍 **Translation** - Translate text antar bahasa
- 📰 **News Updates** - Berita terkini dari berbagai kategori
- 💰 **Crypto Prices** - Harga cryptocurrency real-time
- 📊 **System Monitoring** - Monitor CPU, memory, disk usage
- 📸 **Screenshot** - Ambil screenshot
- 📝 **Notes & Reminders** - Buat catatan dan pengingat
- 🏠 **Smart Home Control** - Kontrol perangkat smart home (simulasi)
- 🔢 **Calculator** - Kalkulasi matematika
- 📧 **Email Notifications** - Kirim email notifikasi
- 🔲 **QR Code Generator** - Generate QR codes
- 📚 **Wikipedia Search** - Cari informasi dari Wikipedia

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd jarvis-ai-assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Aktivasi virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirement.txt
```

### 4. Configure Environment Variables
Buat file `.env` di root directory:

```env
# Required - ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
AGENT_ID=your_elevenlabs_agent_id_here

# Required - OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Weather API
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional - Email Notifications
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
```

### 5. Project Structure
```
jarvis-ai-assistant/
├── main.py                 # Original voice assistant
├── tools.py               # Basic tools
├── enhanced_tools.py      # Enhanced tools dengan fitur tambahan
├── app.py                 # Flask backend + WebSocket server
├── jarvis_launcher.py     # Main launcher dengan monitoring
├── templates/
│   └── index.html        # JARVIS UI (akan dibuat otomatis)
├── generated_images/      # Folder untuk gambar yang digenerate
├── notes/                # Folder untuk notes
├── .env                  # Environment variables
└── requirement.txt       # Python dependencies
```

## 🚀 Running L.E.O

### Method 1: Using L.E.O Launcher (Recommended)
```bash
python jarvis_launcher.py
```
Launcher akan otomatis:
- ✅ Check semua requirements
- ✅ Start Flask backend server
- ✅ Start WebSocket server
- ✅ Buka browser dengan UI
- ✅ Monitor system status

### Method 2: Manual Start
```bash
# Terminal 1 - Start backend
python app.py

# Terminal 2 - Buka browser
# Navigate to: http://localhost:5000
```

### Method 3: Original Voice-Only Mode
```bash
python main.py
```

## 🎮 How to Use

### Web UI Controls
1. **Start Listening** - Klik untuk mulai voice interaction
2. **Tool Cards** (Sidebar) - Klik untuk activate specific tools
3. **Theme Switcher** - Ubah warna tema (Blue/Red/Green/Purple)
4. **Export Data** - Download conversation history
5. **Clear History** - Hapus chat history

### Voice Commands Examples
- "Hey L.E.O, what's the weather today?"
- "Search for latest technology news"
- "Generate an image of a futuristic city"
- "Translate 'Hello World' to Japanese"
- "What's the Bitcoin price?"
- "Take a screenshot"
- "Set a reminder for 10 minutes"
- "Calculate 1337 * 42"
- "Search Wikipedia for artificial intelligence"

### Keyboard Shortcuts
- `Spacebar` - Toggle voice listening
- `Esc` - Stop current operation
- `Ctrl+C` - Stop L.E.O (in terminal)

## 🔧 Troubleshooting

### Common Issues

#### 1. PyAudio Installation Error
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Mac
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

#### 2. WebSocket Connection Failed
- Check if port 8765 is available
- Restart the launcher
- Check firewall settings

#### 3. Microphone Not Working
- Check microphone permissions
- Test with: `python -m speech_recognition`
- Select correct audio device in system settings

#### 4. API Keys Issues
- Verify all API keys in `.env` file
- Check API quotas/limits
- Ensure keys have proper permissions

## 🎨 UI Customization

### Change Colors
Edit CSS variables in `index.html`:
```javascript
document.documentElement.style.cssText = `
    --primary-color: #00ffff;  // Cyan
    --secondary-color: #0099ff; // Blue
`;
```

### Add New Tools
1. Create function in `enhanced_tools.py`
2. Register in `register_enhanced_tools()`
3. Add UI card in `index.html`

### Modify Animations
Edit keyframes in CSS section of `index.html`

## 📊 API Configuration

### OpenWeatherMap (Optional)
1. Sign up at https://openweathermap.org
2. Get free API key
3. Add to `.env` file

## 🔐 Security Notes
- **Never commit `.env` file** to version control
- Keep API keys secure
- Use environment variables for sensitive data
- Enable 2FA on all API accounts
- Regularly rotate API keys
- Monitor API usage for unusual activity

## 📈 Performance Optimization
- Use GPU acceleration for image processing (if available)
- Adjust audio buffer size for latency
- Enable caching for frequent requests
- Use CDN for static assets
- Optimize WebSocket message size

## 🐛 Debug Mode
Enable debug mode in `app.py`:
```python
app.run(debug=True, port=5000)
```

Check logs:
- Flask logs: Terminal running `app.py`
- Browser console: F12 → Console tab
- WebSocket messages: F12 → Network → WS tab

## 📱 Mobile Support
The UI is responsive and works on mobile devices:
- Connect to same network
- Access via: `http://[computer-ip]:5000`
- Use headphones for better audio experience

## 🚀 Future Enhancements
- [ ] Multi-language support
- [ ] Custom wake word detection
- [ ] Integration with more smart home devices
- [ ] Advanced computer vision features
- [ ] Natural language task automation
- [ ] Cloud sync for conversations
- [ ] Mobile app
- [ ] VR/AR interface
- [ ] Gesture control
- [ ] Emotion detection


## Contributing
Feel free to submit issues, fork the repository, and create pull requests.

## Support
For issues or questions:
- Check documentation first
- Search existing issues
- Create new issue with details
- Include error logs and screenshots

---


*"There is a threshold where consistent effort transforms into extraordinary results. Your job is to find it and cross it."    - Laudza Kusuma*
