# GoPro HERO12 Dashboard

A Raspberry Pi-based dashboard for controlling and monitoring a **GoPro HERO12 Black** through a USB CDC-NCM network connection and the **Open GoPro API**.

The Raspberry Pi handles camera control, power control, and the network connection to the GoPro. The live H.264 preview stream is forwarded to a Windows laptop for viewing.

## Features

* Camera Power ON/OFF using GPIO and USB triggering
* Live H.264 Preview
* VLC / FFplay preview on Windows
* Full-screen live preview
* Record Start / Stop
* Media Browser
* Media Download
* Video Settings Control
* Camera Status Monitoring
* Battery and SD-card status
* Ethernet control through Open GoPro API
* USB CDC-NCM communication between GoPro and Raspberry Pi
* Low-processing video forwarding without FFmpeg encoding
* Flask-based web dashboard

## Architecture

```text
                         CONTROL PATH

Windows Laptop
      │
      │ Ethernet
      ▼
Raspberry Pi
      │
      │ Open GoPro API
      ▼
GoPro HERO12


                         VIDEO PATH

GoPro HERO12
      │
      │ USB CDC-NCM
      ▼
Raspberry Pi
      │
      │ UDP H.264
      ▼
Windows Laptop
      │
      ├── VLC
      └── FFplay
```

The Raspberry Pi does **not** decode or re-encode the video stream. The original GoPro H.264 stream is forwarded to the Windows laptop.

---

## Raspberry Pi Requirements

### Hardware

* Raspberry Pi
* GoPro HERO12 Black
* Ethernet connection between Raspberry Pi and Windows laptop
* USB data connection between GoPro and Raspberry Pi
* External GoPro power circuit with LM2596 buck converter
* Common ground between the GoPro USB signal and external power circuit

### Software

* Raspberry Pi OS
* Python 3
* Flask
* Requests
* RPi.GPIO
* Git
* socat

**Node.js, npm, JSMpeg, WebSocket relay, and FFmpeg are not required.**

---

## Installation

### 1. Update Raspberry Pi

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required Packages

```bash
sudo apt install -y python3 python3-pip python3-venv git socat
```

### 3. Clone Repository

```bash
mkdir -p ~/Projects
cd ~/Projects

git clone https://github.com/rohitkumar887393/GoPro-HERO12-Dashboard.git

cd GoPro-HERO12-Dashboard
```

### 4. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` is not available:

```bash
pip install flask requests RPi.GPIO
```

---

## GoPro USB Connection

Connect the GoPro HERO12 to the Raspberry Pi using the USB data connection.

The GoPro should appear as a USB network interface.

Check:

```bash
ip addr
```

Expected GoPro USB interface:

```text
enxxxxxxxxxxxx
```

Expected Raspberry Pi GoPro-side IP:

```text
172.24.103.54
```

GoPro IP:

```text
172.24.103.51
```

Verify communication:

```bash
curl http://172.24.103.51:8080/gopro/camera/info
```

The response should contain:

```json
"model_name": "HERO12 Black"
```

---

## Windows Network Configuration

The Raspberry Pi is connected to the Windows laptop through Ethernet.

Example:

```text
Raspberry Pi : 192.168.2.2
Windows      : 192.168.2.7
```

Add the GoPro network route on Windows **as Administrator**:

```cmd
route -p add 172.24.103.0 mask 255.255.255.0 192.168.2.2
```

Verify:

```cmd
route print
```

---

## Running the Dashboard

On the Raspberry Pi:

```bash
cd ~/Projects/GoPro-HERO12-Dashboard
source venv/bin/activate
python app.py
```

Open the dashboard from the Windows laptop:

```text
http://192.168.2.2:5000
```

---

## Camera Operation

From the dashboard, press **POWER ON**.

The dashboard automatically:

1. Powers the GoPro.
2. Enables wired USB control.
3. Starts the GoPro preview stream.
4. Starts the required UDP forwarding.
5. Makes the H.264 stream available to the Windows laptop.

No additional FFmpeg or JSMpeg process is required.

---

## Live Preview

### VLC

Open VLC:

**Media → Open Network Stream**

Enter:

```text
udp://@:8554
```

Press **Play**.

### FFplay

```bash
ffplay -fflags nobuffer -flags low_delay -framedrop udp://0.0.0.0:8554
```

---

## Media Access

The dashboard uses the GoPro API for media management.

Media list:

```text
/gopro/media/list
```

GoPro media URL:

```text
http://172.24.103.51:8080/videos/DCIM/
```

---

## Project Structure

```text
GoPro-HERO12-Dashboard/
│
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── ...
├── static/
│   └── ...
└── venv/
```

---

## Network Overview

```text
GoPro HERO12
     │
     │ USB CDC-NCM
     │
     ▼
Raspberry Pi
     │
     ├── OpenGoPro API
     │       │
     │       └── Camera Control
     │
     └── UDP H.264
             │
             │ Ethernet
             ▼
       Windows Laptop
             │
             ├── VLC
             └── FFplay
```

## Technologies

* **Python**
* **Flask**
* **Open GoPro API**
* **RPi.GPIO**
* **USB CDC-NCM**
* **UDP H.264**
* **socat**
* **VLC / FFplay**
* **Raspberry Pi OS**


Add your preferred project license here.
