\# Recovery Guide



Use this guide if:

\- New Raspberry Pi

\- New Laptop

\- New GoPro

\- SD Card Failure

\- Lost Project Files



\## Step 1 - Clone Repository



git clone https://github.com/rohitkumar887393/GoPro-HERO12-Dashboard.git



\## Step 2 - Install Packages



sudo apt update



sudo apt install git python3 python3-pip python3-venv ffmpeg nodejs npm -y



\## Step 3 - Create Virtual Environment



python3 -m venv venv



source venv/bin/activate



pip install -r requirements.txt



\## Step 4 - Install JSMpeg



cd \~



git clone https://github.com/phoboslab/jsmpeg.git



\## Step 5 - Install Relay Service



sudo cp service/jsmpeg-relay.service /etc/systemd/system/



sudo systemctl daemon-reload



sudo systemctl enable jsmpeg-relay



sudo systemctl start jsmpeg-relay



\## Step 6 - Run Dashboard



python app.py



\## Step 7 - Connect GoPro



Factory Reset GoPro



Connect Ethernet Adapter



Connect Ethernet Cable



\## Step 8 - Verify



ping 172.24.103.51



curl http://172.24.103.51:8080/gopro/camera/info



\## Step 9 - Open Dashboard



http://<PI\_IP>:5000



Example:



http://192.168.0.163:5000



\## Expected Result



\- GoPro powers ON

\- Preview starts automatically

\- Recording works

\- Media browser works

