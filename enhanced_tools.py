# enhanced_tools.py - Fitur-fitur tambahan untuk AI Assistant
import os
import json
import requests
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from googletrans import Translator
import feedparser
import yfinance as yf
import subprocess
import wikipedia
import pyautogui
import cv2
import numpy as np
from geopy.geocoders import Nominatim
import pyttsx3
import speech_recognition as sr
import pygame
import qrcode
from PIL import Image
import io
import base64
from elevenlabs.conversational_ai.conversation import ClientTools
from dotenv import load_dotenv

load_dotenv()

# Initialize services
translator = Translator()
geolocator = Nominatim(user_agent="jarvis-ai")
tts_engine = pyttsx3.init()
recognizer = sr.Recognizer()
pygame.mixer.init()

# Enhanced tools for JARVIS-like features

def play_audio(file_path: str):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue


def get_weather(parameters: Dict[str, Any]) -> str:
    """Get weather information for a location"""
    location = parameters.get("location", "Jakarta")
    
    try:
        # Get coordinates
        loc = geolocator.geocode(location)
        if not loc:
            return f"Location {location} not found"
        
        # OpenWeatherMap API (you need to add API key to .env)
        api_key = os.getenv("OPENWEATHER_API_KEY", "")
        if not api_key:
            return "Weather API key not configured"
        
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={loc.latitude}&lon={loc.longitude}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        
        return f"Weather in {location}: {weather}, Temperature: {temp}°C (feels like {feels_like}°C), Humidity: {humidity}%"
    except Exception as e:
        return f"Error getting weather: {str(e)}"

def translate_text(parameters: Dict[str, Any]) -> str:
    """Translate text between languages"""
    text = parameters.get("text", "")
    target_lang = parameters.get("target", "en")
    source_lang = parameters.get("source", "auto")
    
    try:
        result = translator.translate(text, src=source_lang, dest=target_lang)
        return f"Translation: {result.text} (from {result.src} to {target_lang})"
    except Exception as e:
        return f"Translation error: {str(e)}"

def get_news(parameters: Dict[str, Any]) -> str:
    """Get latest news from various sources"""
    category = parameters.get("category", "technology")
    
    feeds = {
        "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
    }
    
    try:
        feed_url = feeds.get(category, feeds["technology"])
        feed = feedparser.parse(feed_url)
        
        news_items = []
        for entry in feed.entries[:5]:  # Get top 5 news
            news_items.append(f"• {entry.title}")
        
        return f"Latest {category} news:\n" + "\n".join(news_items)
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def set_reminder(parameters: Dict[str, Any]) -> str:
    """Set a reminder/alarm"""
    message = parameters.get("message", "Reminder")
    time_str = parameters.get("time", "")
    
    try:
        # Parse time (simple implementation)
        if "minute" in time_str:
            minutes = int(''.join(filter(str.isdigit, time_str)))
            remind_time = datetime.now() + timedelta(minutes=minutes)
        elif "hour" in time_str:
            hours = int(''.join(filter(str.isdigit, time_str)))
            remind_time = datetime.now() + timedelta(hours=hours)
        else:
            remind_time = datetime.now() + timedelta(minutes=5)
        
        # Save reminder to file (simple implementation)
        with open("reminders.json", "a") as f:
            reminder = {
                "message": message,
                "time": remind_time.isoformat(),
                "created": datetime.now().isoformat()
            }
            f.write(json.dumps(reminder) + "\n")
        
        return f"Reminder set for {remind_time.strftime('%Y-%m-%d %H:%M:%S')}: {message}"
    except Exception as e:
        return f"Error setting reminder: {str(e)}"

def get_system_info(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get system information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return {
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "memory_available": f"{memory.available / (1024**3):.2f} GB",
            "disk_usage": f"{disk.percent}%",
            "disk_free": f"{disk.free / (1024**3):.2f} GB",
            "network_sent": f"{network.bytes_sent / (1024**2):.2f} MB",
            "network_recv": f"{network.bytes_recv / (1024**2):.2f} MB",
            "platform": platform.platform(),
            "processor": platform.processor()
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_math(parameters: Dict[str, Any]) -> str:
    """Perform mathematical calculations"""
    expression = parameters.get("expression", "")
    
    try:
        # Safe evaluation of mathematical expressions
        import ast
        import operator as op
        
        operators = {
            ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
            ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg
        }
        
        def eval_expr(expr):
            return eval(expr, {"__builtins__": None}, {})
        
        result = eval_expr(expression)
        return f"Result: {expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

def take_screenshot(parameters: Dict[str, Any]) -> str:
    """Take a screenshot"""
    filename = parameters.get("filename", f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved as {filename}"
    except Exception as e:
        return f"Screenshot error: {str(e)}"

def search_wikipedia(parameters: Dict[str, Any]) -> str:
    """Search Wikipedia for information"""
    query = parameters.get("query", "")
    
    try:
        result = wikipedia.summary(query, sentences=3)
        return f"Wikipedia: {result}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {', '.join(e.options[:5])}"
    except Exception as e:
        return f"Wikipedia search error: {str(e)}"

def get_crypto_price(parameters: Dict[str, Any]) -> str:
    """Get cryptocurrency prices"""
    symbol = parameters.get("symbol", "BTC-USD")
    
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        current_price = data['Close'].iloc[-1]
        
        info = ticker.info
        market_cap = info.get('marketCap', 'N/A')
        volume = info.get('volume24Hr', 'N/A')
        
        return f"{symbol} Price: ${current_price:.2f}, Market Cap: ${market_cap:,}, 24h Volume: ${volume:,}"
    except Exception as e:
        return f"Error fetching crypto price: {str(e)}"

def control_smart_home(parameters: Dict[str, Any]) -> str:
    """Control smart home devices (simulation)"""
    device = parameters.get("device", "")
    action = parameters.get("action", "")
    
    devices = {
        "lights": ["on", "off", "dim", "bright"],
        "temperature": ["increase", "decrease", "set"],
        "security": ["arm", "disarm", "status"],
        "music": ["play", "pause", "next", "previous"]
    }
    
    if device in devices and action in devices[device]:
        return f"Smart Home: {device} {action} executed successfully"
    else:
        return f"Smart Home: Unknown device or action"

def generate_qr_code(parameters: Dict[str, Any]) -> str:
    """Generate QR code"""
    data = parameters.get("data", "")
    filename = parameters.get("filename", "qrcode.png")
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        
        return f"QR code generated and saved as {filename}"
    except Exception as e:
        return f"QR code generation error: {str(e)}"

def send_email_notification(parameters: Dict[str, Any]) -> str:
    """Send email notification"""
    recipient = parameters.get("recipient", "")
    subject = parameters.get("subject", "JARVIS Notification")
    message = parameters.get("message", "")
    
    try:
        sender_email = os.getenv("EMAIL_ADDRESS", "")
        sender_password = os.getenv("EMAIL_PASSWORD", "")
        
        if not sender_email or not sender_password:
            return "Email credentials not configured"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        text = msg.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        
        return f"Email sent to {recipient}"
    except Exception as e:
        return f"Email error: {str(e)}"

def run_system_command(parameters: Dict[str, Any]) -> str:
    """Run system command (be careful with this)"""
    command = parameters.get("command", "")
    
    # Whitelist safe commands
    safe_commands = ["ls", "dir", "pwd", "date", "time", "whoami", "hostname"]
    
    if not any(command.startswith(cmd) for cmd in safe_commands):
        return "Command not in safe list"
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
        return f"Command output:\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Command error: {str(e)}"

def create_note(parameters: Dict[str, Any]) -> str:
    """Create and save a note"""
    title = parameters.get("title", "Note")
    content = parameters.get("content", "")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"notes/{title}_{timestamp}.md"
        
        os.makedirs("notes", exist_ok=True)
        
        with open(filename, "w") as f:
            f.write(f"# {title}\n\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(content)
        
        return f"Note saved as {filename}"
    except Exception as e:
        return f"Note creation error: {str(e)}"

def analyze_image(parameters: Dict[str, Any]) -> str:
    """Analyze image using OpenCV (basic analysis)"""
    image_path = parameters.get("image_path", "")
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Image not found"
        
        height, width, channels = img.shape
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces (if opencv haarcascades are available)
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            num_faces = len(faces)
        except:
            num_faces = "N/A"
        
        # Calculate brightness
        brightness = np.mean(gray)
        
        return f"Image Analysis:\n- Dimensions: {width}x{height}\n- Channels: {channels}\n- Faces detected: {num_faces}\n- Avg brightness: {brightness:.2f}"
    except Exception as e:
        return f"Image analysis error: {str(e)}"

# Register all enhanced tools
def register_enhanced_tools(client_tools: ClientTools):
    """Register all enhanced tools with the client"""
    client_tools.register("getWeather", get_weather)
    client_tools.register("translateText", translate_text)
    client_tools.register("getNews", get_news)
    client_tools.register("setReminder", set_reminder)
    client_tools.register("getSystemInfo", get_system_info)
    client_tools.register("calculateMath", calculate_math)
    client_tools.register("takeScreenshot", take_screenshot)
    client_tools.register("searchWikipedia", search_wikipedia)
    client_tools.register("getCryptoPrice", get_crypto_price)
    client_tools.register("controlSmartHome", control_smart_home)
    client_tools.register("generateQRCode", generate_qr_code)
    client_tools.register("sendEmail", send_email_notification)
    client_tools.register("runCommand", run_system_command)
    client_tools.register("createNote", create_note)
    client_tools.register("analyzeImage", analyze_image)