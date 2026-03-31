import io
import json
import logging
import socket
import socketserver
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# ─── Configuration ────────────────────────────────────────────────────────────
PICO_IP     = "10.13.47.140"  # <-- Replace with your Pico W's IP address
PICO_PORT   = 5005
STREAM_PORT = 8000
# ──────────────────────────────────────────────────────────────────────────────

# UDP socket — created once at startup and reused for every servo command
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_servo_command(axis: str, angle: float):
    """Forward a servo command to the Pico W over UDP."""
    try:
        msg = json.dumps({"axis": axis, "angle": angle}).encode()
        udp_sock.sendto(msg, (PICO_IP, PICO_PORT))
    except Exception as e:
        logging.warning("Failed to send servo command: %s", e)


PAGE = """\
<!DOCTYPE html>
<html>
<head>
  <title>CATTTTSSSSSSSSSS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #111;
      color: #eee;
      font-family: sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 24px;
      padding: 24px;
      min-height: 100vh;
    }

    h1 { font-size: 1.2rem; font-weight: 400; opacity: 0.7; }

    img {
      width: 100%;
      max-width: 640px;
      border-radius: 12px;
      border: 1px solid #333;
      display: block;
    }

    .controls {
      display: flex;
      gap: 60px;
      justify-content: center;
      align-items: center;
      width: 100%;
      max-width: 640px;
    }

    .joystick-wrap {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
    }

    /*
      position:relative is required so nipplejs absolutely positions
      the knob inside this div, not relative to the page.
      Without it the knob escapes and floats over the video feed.
      overflow:hidden clips it cleanly at the circle edge.
    */
    .joystick-zone {
      position: relative;
      width: 140px;
      height: 140px;
      background: #1e1e1e;
      border-radius: 50%;
      border: 2px solid #444;
      overflow: hidden;
    }

    .label {
      font-size: 0.8rem;
      opacity: 0.5;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
  </style>
</head>
<body>
  <h1>CAT STREAMMMMM</h1>
  <img src="/stream.mjpg" />

  <div class="controls">

    <div class="joystick-wrap">
      <span class="label">Pan</span>
      <div class="joystick-zone" id="zone-pan"></div>
    </div>

    <div class="joystick-wrap">
      <span class="label">Tilt</span>
      <div class="joystick-zone" id="zone-tilt"></div>
    </div>

  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.10.1/nipplejs.min.js"></script>
  <script>
    // Servo degrees of travel from centre to full joystick deflection
    const RANGE = 80;

    // Send at most one command per axis every 50 ms
    const THROTTLE_MS = 50;
    let lastSend = { pan: 0, tilt: 0 };

    function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

    function sendServo(axis, angle) {
      const now = Date.now();
      if (now - lastSend[axis] < THROTTLE_MS) return;
      lastSend[axis] = now;
      fetch('/servo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ axis, angle })
      }).catch(() => {});
    }

    // ── Pan: horizontal only ─────────────────────────────────────────────────
    // nipplejs lockY snaps the knob to the bottom on first click, so instead
    // we let it move freely and pin the knob vertically to 50% ourselves.
    const panManager = nipplejs.create({
      zone:        document.getElementById('zone-pan'),
      mode:        'static',
      position:    { left: '50%', top: '50%' },
      color:       '#4a9eff',
      size:        110,
      lockY: true,
      dynamicPage: true
    });

    panManager.on('move', (evt, data) => {
      const knob = document.querySelector('#zone-pan .front');
      if (knob) knob.style.top = '50%';
      const x = data.vector ? data.vector.x : 0;
      sendServo('pan', clamp(90 + Math.round(x * RANGE), 0, 180));
    });
    panManager.on('end', () => sendServo('pan', 90));

    // ── Tilt: vertical only (lockX keeps the knob on the Y axis) ────────────
    const tiltManager = nipplejs.create({
      zone:     document.getElementById('zone-tilt'),
      mode:     'static',
      position: { left: '50%', top: '50%' },
      color:    '#ff6b4a',
      size:     110,
      lockX:    true
    });

    tiltManager.on('move', (evt, data) => {
      // nipplejs: +y = up, -y = down — invert so up raises the servo angle
      const y = data.vector ? -data.vector.y : 0;
      sendServo('tilt', clamp(90 + Math.round(y * RANGE), 0, 180));
    });
    tiltManager.on('end', () => sendServo('tilt', 90));

  </script>
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suppress per-frame stream logs to keep the terminal readable
        if '/stream.mjpg' not in (args[0] if args else ''):
            super().log_message(format, *args)

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s',
                                self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/servo':
            length = int(self.headers.get('Content-Length', 0))
            try:
                body  = self.rfile.read(length)
                cmd   = json.loads(body)
                axis  = cmd.get('axis')
                angle = float(cmd.get('angle', 90))

                if axis in ('pan', 'tilt') and 0 <= angle <= 180:
                    send_servo_command(axis, angle)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
            except Exception as e:
                logging.warning('Bad servo request: %s', e)
                self.send_response(400)
                self.end_headers()
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


# ── Start camera and server ───────────────────────────────────────────────────
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

print(f"Streaming on   http://0.0.0.0:{STREAM_PORT}")
print(f"Servo commands UDP {PICO_IP}:{PICO_PORT}")

try:
    address = ('', STREAM_PORT)
    httpd = StreamingServer(address, StreamingHandler)
    httpd.serve_forever()
finally:
    picam2.stop_recording()
    udp_sock.close()