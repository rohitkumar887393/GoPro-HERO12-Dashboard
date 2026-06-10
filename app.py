from flask import Flask, jsonify, request, render_template_string, send_from_directory
import requests
import threading
import time
from flask import send_file, redirect, Response

import requests
import os
import time
import subprocess

import RPi.GPIO as GPIO

app = Flask(__name__)

GOPRO_IP = "http://172.24.103.51:8080"


# Keep-alive thread (required every 3 seconds)
def keep_alive():
    while True:
        try:
            r = requests.get(
                f"{GOPRO_IP}/gopro/camera/keep_alive",
                timeout=2
            )
            print("KEEPALIVE:", r.status_code)

        except Exception as e:
            print("KEEPALIVE ERROR:", e)

        time.sleep(3)

threading.Thread(target=keep_alive, daemon=True).start()


CAMERA_POWER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(CAMERA_POWER_PIN, GPIO.OUT)

# P-MOSFET High Side:
# LOW = ON
# HIGH = OFF

GPIO.output(CAMERA_POWER_PIN, GPIO.LOW)




HTML = '''
<!DOCTYPE html>
<html>


<head>
<title>GoPro Hero12 Control</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<script src="https://cdn.jsdelivr.net/gh/phoboslab/jsmpeg@master/jsmpeg.min.js"></script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }



body { background: #111; color: #eee; font-family: Arial, sans-serif; }
header { background: #1a1a2e; padding: 16px 24px; display: flex; align-items: center; gap: 12px; border-bottom: 2px solid #00d4ff; }
header h1 { font-size: 1.4rem; color: #00d4ff; }
.status-dot { width: 12px; height: 12px; border-radius: 50%; background: #00ff88; box-shadow: 0 0 8px #00ff88; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }


.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; padding: 20px; }
.preview-card {
    grid-column: span 2;
}

.card { background: #1a1a2e; border-radius: 12px; padding: 20px; border: 1px solid #333; }
.card h2 { color: #00d4ff; margin-bottom: 16px; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }


.btn { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 0.9rem; font-weight: bold; transition: all 0.2s; width: 100%; margin-bottom: 8px; }
.btn-red { background: #e74c3c; color: white; }
.btn-red:hover { background: #c0392b; }
.btn-green { background: #27ae60; color: white; }
.btn-green:hover { background: #1e8449; }
.btn-blue { background: #2980b9; color: white; }
.btn-blue:hover { background: #1a6fa0; }
.btn-orange { background: #e67e22; color: white; }
.btn-orange:hover { background: #ca6f1e; }
.btn-gray { background: #555; color: white; }
.btn-gray:hover { background: #444; }

.compact-btn {
    width: auto !important;
    flex: 1;
    padding: 6px 10px;
    margin-bottom: 0;
    font-size: 0.8rem;
}


select { width: 100%; padding: 10px; background: #0d0d1a; color: #eee; border: 1px solid #444; border-radius: 8px; margin-bottom: 8px; font-size: 0.9rem; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.info-item { background: #0d0d1a; padding: 10px; border-radius: 8px; }
.info-label { font-size: 0.7rem; color: #888; text-transform: uppercase; }
.info-value { font-size: 1rem; color: #00d4ff; font-weight: bold; margin-top: 2px; }
.recording { animation: recpulse 1s infinite; }
@keyframes recpulse { 0%,100%{background:#e74c3c} 50%{background:#7b241c} }
#toast { position: fixed; bottom: 20px; right: 20px; background: #27ae60; color: white; padding: 12px 20px; border-radius: 8px; display: none; font-weight: bold; z-index: 999; }
.shutter-btn { height: 70px; font-size: 1.1rem; border-radius: 35px; }
.rec-indicator { text-align: center; font-size: 0.8rem; margin-top: 8px; color: #888; }
#rec-status { color: #e74c3c; font-weight: bold; }
</style>
</head>
<body>
<header>
  <div class="status-dot" id="status-dot"></div>
  <h1>🎥 GoPro Hero12 Black — Control Panel</h1>
  <span id="header-info" style="margin-left:auto;font-size:0.8rem;color:#888"></span>
</header>

<div class="grid">

  <!-- Camera Info -->

<div class="card preview-card">

<h2>📺 Live Preview</h2>

<canvas
    id="preview"
    style="
        width:100%;
        border-radius:8px;
        background:black;
    ">




</canvas>

<button
    class="btn btn-blue"
    onclick="fullscreenPreview()">
    ⛶ Full Screen Preview
</button>

    <h2>📊 Camera Status</h2>
    <div class="info-grid" id="info-grid">
      <div class="info-item"><div class="info-label">Model</div><div class="info-value" id="i-model">-</div></div>
      <div class="info-item"><div class="info-label">Firmware</div><div class="info-value" id="i-fw">-</div></div>
      <div class="info-item"><div class="info-label">Battery</div><div class="info-value" id="i-bat">-</div></div>
      <div class="info-item"><div class="info-label">SD Free</div><div class="info-value" id="i-sd">-</div></div>
      <div class="info-item"><div class="info-label">Recording</div><div class="info-value" id="i-rec">-</div></div>
      <div class="info-item"><div class="info-label">Mode</div><div class="info-value" id="i-mode">-</div></div>
    </div>
    <br>
    <button class="btn btn-gray" onclick="refreshState()">🔄 Refresh Status</button>

   </div>

  <!-- Camera Power -->


<div class="card">
    <h2>⚡ Power & Recording</h2>

    <div style="display:flex; gap:6px; margin-bottom:10px;">
        <button
            class="btn btn-green"
            style="margin-bottom:0;"
            onclick="power('on')">
            ON
        </button>

        <button
            class="btn btn-red"
            style="margin-bottom:0;"
            onclick="power('off')">
            OFF
        </button>
    </div>

    <div style="display:flex; gap:6px;">
        <button
            class="btn btn-green"
            style="margin-bottom:0;"
            onclick="startShutter()">
            REC
        </button>

        <button
            class="btn btn-red"
            style="margin-bottom:0;"
            onclick="stopShutter()">
            STOP
        </button>
    </div>

    <div class="rec-indicator">
        Status: <span id="rec-status">IDLE</span>
    </div>
</div>








  <!-- Mode Selection -->
  <div class="card">
    <h2>🎬 Mode / Preset</h2>
    <select id="preset-select">
      <option value="1000">📹 Video</option>
      <option value="1001">📷 Photo</option>
      <option value="1002">⏱ Timelapse</option>
    </select>
    <button class="btn btn-blue" onclick="setPresetGroup()">Set Mode</button>
  </div>

  <!-- Resolution -->
  <div class="card">
    <h2>📐 Video Resolution</h2>
    <select id="res-select">
      <option value="1">4K</option>
      <option value="4">2.7K</option>
      <option value="9" selected>1080p</option>
      <option value="18">4K 4:3</option>
    </select>
    <button class="btn btn-blue" onclick="setSetting(2, document.getElementById('res-select').value)">Set Resolution</button>

    <br><br>
    <h2 style="color:#00d4ff;font-size:1rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">🎞 Frame Rate</h2>
    <select id="fps-select">
      <option value="0">240fps</option>
      <option value="1">120fps</option>
      <option value="2">100fps</option>
      <option value="5">60fps</option>
      <option value="8" selected>30fps</option>
      <option value="9">25fps</option>
      <option value="10">24fps</option>
    </select>
    <button class="btn btn-blue" onclick="setSetting(3, document.getElementById('fps-select').value)">Set FPS</button>
  </div>

  <!-- Lens / FOV -->
  <div class="card">
    <h2>🔭 Video Lens</h2>
    <select id="lens-select">
      <option value="0">Wide</option>
      <option value="4">Linear</option>
      <option value="3">Superview</option>
      <option value="7">Max SuperView</option>
      <option value="8">Linear+Horizon Lock</option>
    </select>
    <button class="btn btn-blue" onclick="setSetting(121, document.getElementById('lens-select').value)">Set Lens</button>
  </div>

  <!-- HyperSmooth -->
  <div class="card">
    <h2>🎯 HyperSmooth Stabilization</h2>
    <select id="hs-select">
      <option value="0">Off</option>
      <option value="1">Low</option>
      <option value="4" selected>Auto Boost</option>
    </select>
    <button class="btn btn-blue" onclick="setSetting(135, document.getElementById('hs-select').value)">Set HyperSmooth</button>
  </div>




  <!-- Quick Controls -->
  <div class="card">
    <h2>⚡ Quick Controls</h2>
    <button class="btn btn-orange" onclick="gopro('/gopro/camera/digital_zoom?percent=0')">🔍 Zoom Reset</button>
    <button class="btn btn-gray" onclick="setDateTime()">🕐 Sync Date/Time</button>
    <button class="btn btn-gray" onclick="gopro('/gopro/camera/control/set_ui_controller?p=2')">🎮 Claim Control</button>
    <button class="btn btn-gray" onclick="gopro('/gopro/camera/control/set_ui_controller?p=0')">🎮 Release Control</button>
    <button class="btn btn-red" onclick="gopro('/gp/gpControl/command/system/sleep')">💤 Sleep Camera</button>
  </div>

</div>



<div class="card">
  <h2>📂 Media Files</h2>

  <button class="btn btn-blue"
          onclick="loadMedia()">
    Refresh Media
  </button>

  <div id="media-list"
       style="
         margin-top:12px;
         max-height:400px;
         overflow-y:auto;
       ">
  </div>
</div>





<div id="toast"></div>

<script>
const BASE = '';

function toast(msg, ok=true) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.background = ok ? '#27ae60' : '#e74c3c';
  t.style.display = 'block';
  setTimeout(() => t.style.display='none', 2500);
}



function fullscreenPreview() {

    const canvas = document.getElementById('preview');

    if (canvas.requestFullscreen) {
        canvas.requestFullscreen();
    } else if (canvas.webkitRequestFullscreen) {
        canvas.webkitRequestFullscreen();
    } else if (canvas.msRequestFullscreen) {
        canvas.msRequestFullscreen();
    }
}


async function gopro(path) {
  try {
    const r = await fetch('/api/gopro?path=' + encodeURIComponent(path));
    const d = await r.json();
    toast(path.split('/').pop() + ' ✓');
    return d;
  } catch(e) {
    toast('Error: ' + e.message, false);
  }
}




async function power(action) {

  const r = await fetch('/camera/' + action);

  const d = await r.json();

  toast('Camera Power ' + action.toUpperCase());
}
















async function startShutter() {
  await gopro('/gopro/camera/shutter/start');
  document.getElementById('rec-status').textContent = '🔴 RECORDING';
  document.getElementById('shutter-btn').style.background = '#7b241c';
}

async function stopShutter() {
  await gopro('/gopro/camera/shutter/stop');
  document.getElementById('rec-status').textContent = 'IDLE';
  document.getElementById('shutter-btn').style.background = '';
}

async function setPresetGroup() {
  const id = document.getElementById('preset-select').value;
  await gopro('/gopro/camera/presets/set_group?id=' + id);
}

async function setSetting(setting, option) {
  await gopro('/gopro/camera/setting?setting=' + setting + '&option=' + option);
}

async function startStream() {
  await gopro('/gopro/camera/stream/start');
  toast('Stream started on port 8554');
}

async function stopStream() {
  await gopro('/gopro/camera/stream/stop');
}

async function setDateTime() {
  const now = new Date();
  const date = now.getFullYear()+'_'+(now.getMonth()+1).toString().padStart(2,'0')+'_'+now.getDate().toString().padStart(2,'0');
  const time = now.getHours().toString().padStart(2,'0')+'_'+now.getMinutes().toString().padStart(2,'0')+'_'+now.getSeconds().toString().padStart(2,'0'); await gopro('/gopro/camera/set_date_time?date='+date+'&time='+time+'&tzone=330&dst=0');
  toast('Date/Time synced!');
}

async function loadMedia() {

  try {

    let r = await fetch('/gopro/media');
    let data = await r.json();

    let html = '';

    data.media.forEach(folder => {

      folder.fs.forEach(file => {

        let sizeMB =
          (parseInt(file.s) / 1024 / 1024).toFixed(1);

        html += `
          <div style="
            background:#0d0d1a;
            padding:8px;
            margin-bottom:8px;
            border-radius:8px;
          ">

            <div><b>${file.n}</b></div>

            <div style="color:#888">
              ${sizeMB} MB
            </div>


<button
  class="btn btn-green"
  onclick="downloadMedia(
    '${folder.d}',
    '${file.n}'
  )">
  Download
</button>

<button
  class="btn btn-red"
  onclick="deleteMedia(
    '${folder.d}',
    '${file.n}'
  )">
  Delete
</button>





          </div>
        `;
      });

    });

    document.getElementById(
      'media-list'
    ).innerHTML = html;

  } catch(e) {

    toast(
      'Media load failed: ' + e.message,
      false
    );

  }
}

function downloadMedia(folder, file) {

    window.open(
        `/media/browser_download?folder=${folder}&file=${file}`,
        "_blank"
    );

}



async function deleteMedia(folder, file) {

  if (!confirm(`Delete ${file} from GoPro?`)) {
    return;
  }

  try {

    await fetch(
      `/media/delete?folder=${folder}&file=${file}`
    );

    toast('Deleted: ' + file, true);

    loadMedia();

  } catch(e) {

    toast(
      'Delete failed: ' + e.message,
      false
    );

  }
}



async function refreshState() {
  try {
    const r = await fetch('/api/state');
    const d = await r.json();
    const s = d.status;
    const sets = d.settings;
    const isRec = s['8'] === 1;
    
// Battery
    document.getElementById('i-bat').textContent = s['70'] + '%';

    // SD card remaining
    const sdMB = Math.round(s['54'] / 1024);
    document.getElementById('i-sd').textContent =
        sdMB > 1024 ? (sdMB / 1024).toFixed(1) + 'GB' : sdMB + 'MB';


    document.getElementById('i-rec').textContent =
        isRec ? '🔴 YES' : '⚪ No';

    const recTime = s['13'] || 0;

    const mins = Math.floor(recTime / 60);
    const secs = recTime % 60;

    document.getElementById('rec-status').textContent =
        isRec
            ? `🔴 REC ${mins}:${secs.toString().padStart(2, '0')}`
            : 'IDLE';

    // Mode based on preset group
    const modes = {
        1000: 'Video',
        1001: 'Photo',
        1002: 'Timelapse'
    };

    const currentMode = s['96'];

    document.getElementById('i-mode').textContent =
        modes[currentMode] || currentMode || '-';



    // Info
    const ri = await fetch('/api/info');
    const info = await ri.json();

    document.getElementById('i-model').textContent =
        info.model_name || '-';

    document.getElementById('i-fw').textContent =
        info.firmware_version || '-';

    document.getElementById('header-info').textContent =
        'SN: ' + (info.serial_number || '-');

  } catch(e) {
    toast('Refresh failed: ' + e.message, false);
  }
}



new JSMpeg.Player(
    'ws://' + window.location.hostname + ':10000',
    {
        canvas: document.getElementById('preview'),
        autoplay: true,
        audio: false
    }
);



// Auto refresh every 5 seconds
refreshState();
setInterval(refreshState, 5000);




    </script>
     </body>
       </html>
   '''




@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/camera/on')
def camera_on():

    GPIO.output(CAMERA_POWER_PIN, GPIO.HIGH)

    time.sleep(5)

    try:
        requests.get(
            "http://172.24.103.51:8080/gopro/camera/control/wired_usb?p=1",
            timeout=3
        )

        time.sleep(2)

        requests.post(
            "http://172.24.103.51:8080/gopro/camera/stream/start",
            timeout=3
        )

        time.sleep(3)


        subprocess.call(
            "pkill -f 'ffmpeg.*udp://@:8554'", shell=True)


        subprocess.Popen(
            """
            ffmpeg \
            -analyzeduration 10000000 \
            -probesize 10000000 \
            -i udp://@:8554 \
            -vf scale=640:360 \
            -c:v mpeg1video \
            -b:v 1000k \
            -r 30 \
            -an \
            -f mpegts \
            http://127.0.0.1:8082/supersecret
            """,
            shell=True
        )




    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "status": "camera_on"
    })

@app.route('/camera/off')
def camera_off():

    subprocess.call("pkill -f ffmpeg", shell=True)

    GPIO.output(CAMERA_POWER_PIN, GPIO.LOW)

    return jsonify({
        "status": "camera_off"
    })

@app.route("/gopro/media")
def media_list():

    try:
        url = "http://172.24.103.51:8080/gopro/media/list"

        r = requests.get(url, timeout=10)

        return r.json()

    except Exception as e:
        return {"error": str(e)}, 500






def index():
    return render_template_string(HTML)

@app.route('/api/gopro')
def proxy():
    path = request.args.get('path', '')
    try:
        r = requests.get(f"{GOPRO_IP}{path}", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/state')
def state():
    try:
        r = requests.get(f"{GOPRO_IP}/gopro/camera/state", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/info')
def info():
    try:
        r = requests.get(f"{GOPRO_IP}/gopro/camera/info", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/media/download")
def media_download():

    folder = request.args.get("folder")
    filename = request.args.get("file")

    if not folder or not filename:
        return {"error": "missing parameters"}, 400

    save_dir = "/home/pi/Projects/GoPro/downloads"
    os.makedirs(save_dir, exist_ok=True)

    url = f"http://172.24.103.51:8080/videos/DCIM/{folder}/{filename}"

    local_file = os.path.join(save_dir, filename)

    r = requests.get(url, stream=True, timeout=120)

    with open(local_file, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

    return {
        "status": "ok",
        "saved_to": local_file
    }



@app.route("/media/browser_download")
def browser_download():

    folder = request.args.get("folder")
    filename = request.args.get("file")

    if not folder or not filename:
        return {"error": "missing parameters"}, 400

    gopro_url = (
        f"http://172.24.103.51:8080/videos/DCIM/"
        f"{folder}/{filename}"
    )

    r = requests.get(
        gopro_url,
        stream=True,
        timeout=300
    )

    return Response(
        r.iter_content(chunk_size=65536),
        content_type=r.headers.get(
            "Content-Type",
            "application/octet-stream"
        )
    )





@app.route("/media/delete")

def media_delete():

    folder = request.args.get("folder")
    filename = request.args.get("file")

    if not folder or not filename:
        return {"error": "missing parameters"}, 400

    url = (
        f"http://172.24.103.51:8080/"
        f"gopro/media/delete/file"
        f"?path={folder}/{filename}"
    )

    r = requests.delete(url, timeout=30)

    return {
        "status": "ok",
        "response": r.text
    }




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
