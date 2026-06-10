\# New GoPro HERO12 Setup



\## Factory Reset



On GoPro:





Preferences

→ Reset

→ Factory Reset





Recommended before first use.







\## Connect Ethernet



Hardware:





GoPro HERO12

&#x20;     ↓

GoPro Ethernet Adapter

&#x20;     ↓

Ethernet Cable

&#x20;     ↓

Raspberry Pi



\## Verify Network Connection



On Raspberry Pi:



```bash

ping 172.24.103.51





\## Verify Open GoPro API



```bash

curl http://172.24.103.51:8080/gopro/camera/info





Expected:



```json

{

&#x20; "model\_name": "HERO12 Black"

}



\## Verify Camera State



```bash

curl http://172.24.103.51:8080/gopro/camera/state









\## Enable Wired USB Control



```bash

curl "http://172.24.103.51:8080/gopro/camera/control/wired\_usb?p=1"



\## Start Live Stream



```bash

curl -X POST \\

http://172.24.103.51:8080/gopro/camera/stream/start



\## Verify UDP Stream



On Raspberry Pi:



```bash

ffplay udp://@:8554

```



Expected:



```text

Live GoPro video visible

```



\---



\## Verify Dashboard Preview



Open:



```text

http://<PI\_IP>:5000

```



Press:



```text

POWER ON

```



Expected:



```text

GoPro boots

↓

Preview starts automatically

↓

Video visible in dashboard

```



\---



\## Troubleshooting



\### Camera Not Reachable



```bash

ping 172.24.103.51





If failed:



\* Check Ethernet cable

\* Reboot GoPro

\* Factory Reset GoPro



\---



\### Preview Not Working



Verify relay:



```bash

sudo systemctl status jsmpeg-relay

```



Verify ffmpeg:



```bash

ps aux | grep ffmpeg

```



Verify stream:



```bash

curl http://172.24.103.51:8080/gopro/camera/state

```



\---



\## Working Sequence



```text

Power Raspberry Pi

&#x20;       ↓

Relay starts automatically

&#x20;       ↓

Open Dashboard

&#x20;       ↓

Press POWER ON

&#x20;       ↓

GoPro boots

&#x20;       ↓

Preview starts automatically

&#x20;       ↓

Record / Download / Control Camera

```



