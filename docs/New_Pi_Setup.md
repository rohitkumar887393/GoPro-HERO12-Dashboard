\# New Raspberry Pi Setup



\## Install Raspberry Pi OS



\* Flash Raspberry Pi OS Lite

\* Enable SSH

\* Boot Raspberry Pi



\---



\## Update System



```bash

sudo apt update

sudo apt upgrade -y

```



\---



\## Install Required Packages



```bash

sudo apt install git python3 python3-pip python3-venv ffmpeg nodejs npm -y

```



\---



\## Clone Repository



```bash

mkdir -p \~/Projects

cd \~/Projects



git clone https://github.com/rohitkumar887393/GoPro-HERO12-Dashboard.git

```



\---



\## Create Python Environment



```bash

cd GoPro-HERO12-Dashboard



python3 -m venv venv

source venv/bin/activate

```



\---



\## Install Python Packages



```bash

pip install -r requirements.txt

```



\---



\## Install JSMpeg Relay



```bash

cd \~



git clone https://github.com/phoboslab/jsmpeg.git

```



Verify:



```bash

ls \~/jsmpeg

```



Expected:



```text

websocket-relay.js

view-stream.html

jsmpeg.min.js

```



\---



\## Install Relay Service



```bash

sudo cp service/jsmpeg-relay.service /etc/systemd/system/

```



```bash

sudo systemctl daemon-reload

sudo systemctl enable jsmpeg-relay

sudo systemctl start jsmpeg-relay

```



Verify:



```bash

sudo systemctl status jsmpeg-relay

```



Expected:



```text

Active: active (running)

```



\---



\## Run Dashboard



```bash

cd \~/Projects/GoPro-HERO12-Dashboard



source venv/bin/activate



python app.py

```



\---



\## Open Dashboard



```text

http://<PI\_IP>:5000

```



