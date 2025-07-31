# 🚁 DroneSoundDetector (DSD)

**Real-time audio stream analysis for drone detection using ML**

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)
- [WebSocket API](#-websocket-api)
- [ML Detection Model](#-ml-detection-model)
- [For Developers](#-for-developers)
- [License](#-license)

---

## 🌟 About the Project

**Problem Solved**:  
Automatic drone detection via acoustic signature without visual contact.

**Target Audience**:
- Security system developers
- ML engineers
- Computer audio enthusiasts

**Advantages**:  
✅ Real-time processing via WebSocket  
✅ Universal solution  
✅ Geolocation integration (coordinates)

---

## 🚀 Key Features

- **Audio Analysis**:
  - Sample rate: 44.1 kHz
  - Supported format: WAV (mono, 16-48 kHz)
- **ML Model**:
  - SVM with 44 features (MFCC + spectral characteristics)
  - Accuracy: 93% (on test data)
- **Alert System**:
  - Alarm-triggered geolocation tagging
  - Group notifications via WebSocket

---

## 🛠 Tech Stack

| Component       | Technologies                   |
|-----------------|--------------------------------|
| Backend         | Django + Django Channels       |
| ML Processing   | librosa, scikit-learn, joblib  |
| Audio Converter | pydub                          |
| Client API      | WebSocket + REST               |
| Deployment      | Docker                         |

---

## ⚙ Installation & Setup

### Local Setup

```bash
git clone https://github.com/Sgudkov/uavsoundanalysis.git
cd uavsoundanalysis
pip install -r requirements.txt


# Start server
python manage.py runserver 0.0.0.0:8000
```

## 🐳 Docker

### Start container

```bash
docker pull azrael45/uav:latest
docker run -p 8000:8000 azrael45/uav
```

### Demo
![Map](uavsoundanalysis/uavanalysis/docs/Map.png)  

## 🕹️ Control Button Functions

### 1. "Start Work" Button
**Purpose**: Main system activation button  
**Functionality**:
- Initializes WebSocket connection for audio stream
- Starts microphone recording and sound analysis
- Activates real-time monitoring
- Sends group notification via channels upon drone detection
- Pressing again stops monitoring (terminates WebSocket connection)

**Technical Implementation**:
```javascript
// map.js
    document.getElementById('start-work-button').addEventListener('click', function() {

        this.classList.toggle('clicked');

        // Start or stop audio streaming
        if (!startWorkButtonPressed) {
            startAudioStreaming(placemarkJson);
            startWorkButtonPressed = true;
        } else {
            stopAudioStreaming();
            startWorkButtonPressed = false;
        }

        console.log('Start work button clicked');

    });
```
### 2. "Test Alert" Button
**Purpose**: Test alert simulation  
**Functionality**:
- Turns markers list to red color
- Makes map markers blink
- Sends data to server
- Server simulates alert condition

### 3. "Stop Alert" Button
**Purpose**: Cancels alert state  
**Functionality**:
- Restores markers to default state
- Doesn't send data to server

## 🌐 WebSocket API

### Connection

```python
import websockets
import json
import base64


async def connect_to_ws():
    async with websockets.connect('ws://your-host/ws/audio') as ws:
        # Чтение аудиофайла
        with open("sample.wav", "rb") as audio_file:
            audio_data = audio_file.read()

        # Отправка данных
        await ws.send(json.dumps({
            "data": base64.b64encode(audio_data).decode('utf-8'),
            "placemarks": [
                {"id": 1, "latitude": 55.751244, "longitude": 37.618423},
                {"id": 2, "latitude": 55.752345, "longitude": 37.619534}
            ]
        }))

        # Получение ответа
        response = await ws.recv()
        print(json.loads(response))
```

### Endpoints

| Endpoint   | Purpose                       | Data Format            |
|------------|-------------------------------|------------------------|
| `/ws/`     | Main control channel          | JSON                   |
| `/ws/audio`| Audio stream transmission     | Base64 + JSON metadata |

```mermaid
graph TD
    A[WebSocket Client] --> B[Audio Stream]
    B --> C[AudioParser]
    C --> D[Convert to WAV]
    D --> E[DroneAnalyzer]
    E --> F[Feature Extraction]
    F --> G[SVM Prediction]
    G --> H{Drone?}
    H -->|Yes| I[Alert]
    H -->|No| J[Continue Monitoring]
```

## 🤖 ML Detection Model

### Prediction Example

```python
analyzer = DroneAnalyzer("drone_sample.wav")
if analyzer.is_drone():
    print("Обнаружен дрон!")
else:
    print("Фоновый шум")
```

## 💻 For Developers

### 🛠️ Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sgudkov/uavsoundanalysis.git
   cd uavsoundanalysis
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
4. **Log in**:
Логин: `admin`
Пароль: `admin`
 
## 📜 License

### MIT License

```text
Copyright (c) [2025]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
