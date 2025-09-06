# Voice AI Assistant with ElevenLabs & OpenAI

Proyek ini adalah implementasi **Voice AI Assistant** menggunakan **ElevenLabs Conversational AI**, **OpenAI (DALL·E 3 & GPT)**, serta beberapa tools tambahan (pencarian web, generate HTML, simpan data ke TXT, dan generate gambar).  
Assistant ini berjalan secara **real-time** dengan input/output audio.

---

## 📂 Struktur Proyek
```
├── main.py            # Entry point aplikasi (menjalankan sesi percakapan)
├── tools.py           # Kumpulan tools custom yang bisa dipanggil AI Agent
├── requirement.txt    # Daftar dependencies Python
```

---

## ⚙️ Instalasi

1. Clone repository ini:
   ```bash
   git clone <repo-url>
   cd <nama-folder>
   ```

2. Buat dan aktifkan virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirement.txt
   ```

---

## 🔑 Konfigurasi

Buat file `.env` di root folder dengan isi seperti berikut:

```env
# ElevenLabs API
ELEVENLABS_API_KEY=your_elevenlabs_api_key
AGENT_ID=your_agent_id

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
```

---

## 🚀 Menjalankan Aplikasi

Jalankan perintah berikut untuk memulai Voice AI Assistant:

```bash
python main.py
```

Jika berhasil, aplikasi akan:
- Memulai sesi percakapan dengan **ElevenLabs Conversational AI**  
- Mendengarkan suara pengguna (via microphone)  
- Mengeluarkan respon suara (Text-to-Speech)  
- Bisa menggunakan tools tambahan seperti:
  - 🔍 **searchWeb** → pencarian informasi lewat DuckDuckGo  
  - 📝 **saveToTxt** → menyimpan teks ke file `.txt`  
  - 🌐 **createHtmlFile** → membuat file HTML sederhana  
  - 🖼️ **generateImage** → generate gambar dengan OpenAI DALL·E 3  

---

## 🛠️ Tools yang Tersedia

### 1. Web Search
```python
searchWeb({"query": "Berita teknologi terbaru"})
```

### 2. Save to TXT
```python
saveToTxt({"filename": "catatan.txt", "data": "Halo dunia"})
```

### 3. Create HTML File
```python
createHtmlFile({"filename": "index.html", "title": "Hello", "data": "Konten di sini"})
```

### 4. Generate Image
```python
generateImage({
    "prompt": "Pemandangan gunung dengan gaya lukisan",
    "filename": "mountain.png",
    "size": "1024x1024"
})
```

---

## 📦 Dependencies
Semua requirements ada di `requirement.txt`:
- elevenlabs  
- pyaudio  
- openai  
- dotenv  
- pillow  
- langchain_community  

---

## 📝 Catatan
- Aplikasi ini membutuhkan **microphone** dan **speaker** untuk interaksi real-time.  
- Pastikan API key **valid** sebelum menjalankan.  
- Gambar hasil generate akan disimpan di folder `generated_images/`.  
