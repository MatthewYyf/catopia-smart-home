import io
import logging
import socketserver
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput


PORT = 8080
WIDTH = 640
HEIGHT = 480


PAGE = f"""\
<html>
<head>
  <title>Catopia Camera Stream</title>
</head>
<body>
  <h1>Catopia Camera Stream</h1>
  <img src="/stream.mjpg" width="{WIDTH}" height="{HEIGHT}" />
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = bytes(buf)
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()

        elif self.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Content-Type",
                "multipart/x-mixed-replace; boundary=FRAME",
            )
            self.end_headers()

            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame

                    if frame is None:
                        continue

                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")

            except Exception as e:
                logging.warning(
                    "Removed streaming client %s: %s",
                    self.client_address,
                    str(e),
                )

        else:
            self.send_error(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    global output

    cameras = Picamera2.global_camera_info()
    print("Detected cameras:", cameras)

    if not cameras:
        raise RuntimeError(
            "No camera detected. Check ribbon cable, camera port, and run: rpicam-hello --list-cameras"
        )

    picam2 = Picamera2(0)

    video_config = picam2.create_video_configuration(
        main={"size": (WIDTH, HEIGHT)}
    )
    picam2.configure(video_config)

    output = StreamingOutput()

    picam2.start_recording(JpegEncoder(), FileOutput(output))

    try:
        address = ("0.0.0.0", PORT)
        http_server = StreamingServer(address, StreamingHandler)

        print(f"Camera stream running at:")
        print(f"  http://0.0.0.0:{PORT}/index.html")
        print(f"  http://0.0.0.0:{PORT}/stream.mjpg")
        print()
        print("Use your Pi IP from another device, for example:")
        print(f"  http://10.42.0.1:{PORT}/stream.mjpg")

        http_server.serve_forever()

    finally:
        picam2.stop_recording()


if __name__ == "__main__":
    output = None
    main()