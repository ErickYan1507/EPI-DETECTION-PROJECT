"""Simulateur TinkerCad / Arduino pour EPI Detection
Envoie des mises à jour capteurs (motion, temp) et écoute commandes LED/detection
Usage:
  python app/simulators/tinkercad_simulator.py --server http://localhost:5000
Dépendances:
  pip install "python-socketio[client]" requests
"""

import argparse
import time
import random
import threading
import json

try:
    import socketio
except Exception:
    socketio = None

import requests

DEFAULT_SERVER = 'http://localhost:5000'

class TinkerCadSimulator:
    def __init__(self, server=DEFAULT_SERVER, mode='socketio', interval=2.0, name='tinkercad_sim'):
        self.server = server
        self.mode = mode
        self.interval = interval
        self.name = name
        self.running = False
        self.sio = None

        if self.mode == 'socketio' and socketio is None:
            raise RuntimeError('python-socketio client required for socketio mode')

    # ---------- Socket.IO client ----------
    def _setup_socket(self):
        self.sio = socketio.Client(reconnection=True)

        @self.sio.event
        def connect():
            print('[sim] Connected to', self.server)
            # register
            self.sio.emit('simulator_register', {'simulator': self.name, 'sensors': ['motion','temp','humidity'], 'leds': ['red','green']})

        @self.sio.event
        def disconnect():
            print('[sim] Disconnected from', self.server)

        @self.sio.on('led_control')
        def on_led_control(data):
            print('[sim] led_control received ->', data)
            # ack
            self.sio.emit('led_status', {'simulator': self.name, 'led': data.get('led'), 'state': data.get('state')})

        @self.sio.on('serial_command')
        def on_serial_command(data):
            # Support receiving direct serial-like commands from server
            print('[sim] serial_command received ->', data)
            # simulate response if relevant
            cmd = data.get('cmd')
            if cmd and cmd.startswith('C'):
                print('[sim] applying compliance command', cmd)
                self.sio.emit('serial_line', {'simulator': self.name, 'line': f'[CMD] Applied {cmd}'})

        @self.sio.on('detect_command')
        def on_detect_command(data):
            # Server asks simulator to display detection (maps to DETECT:...)
            print('[sim] detect_command received ->', data)
            # Echo back an ack
            self.sio.emit('serial_line', {'simulator': self.name, 'line': f"[DETECT_ACK] {json.dumps(data)}"})

    def start_socket(self):
        self._setup_socket()
        try:
            # Try default connection (websocket preferred). If it fails, retry forcing polling transport.
            try:
                self.sio.connect(self.server, wait=True)
            except Exception as e:
                print('[sim] Default Socket.IO connect failed, retrying with polling transport:', e)
                try:
                    # Force polling transport to avoid needing websocket-client package
                    self.sio.connect(self.server, wait=True, transports=['polling'])
                except Exception as e2:
                    print('[sim] Polling transport connect also failed:', e2)
                    raise
        except Exception as e:
            print('[sim] Socket.IO connect failed:', e)
            raise

    # ---------- REST fallback ----------
    def _post_rest(self, path, payload):
        try:
            url = self.server.rstrip('/') + '/' + path.lstrip('/')
            r = requests.post(url, json=payload, timeout=5)
            print(f'[sim][REST] POST {url} ->', r.status_code)
            return r
        except Exception as e:
            print('[sim][REST] POST failed:', e)
            return None

    # ---------- Simulator loop ----------
    def _generate_sensor_payload(self):
        motion = random.choice([True, False, False])  # less frequent motion
        temp = round(20 + random.random()*8, 1)
        humidity = round(40 + random.random()*30, 1)
        ts = time.time()
        payload = {
            'simulator': self.name,
            'timestamp': ts,
            'sensors': {
                'motion': motion,
                'temp': temp,
                'humidity': humidity
            }
        }
        return payload

    def _run_loop(self):
        self.running = True
        while self.running:
            payload = self._generate_sensor_payload()
            if self.mode == 'socketio':
                try:
                    self.sio.emit('sensor_update', payload)
                    # also emit serial-like lines
                    line = f"[SENSOR] temp={payload['sensors']['temp']},humidity={payload['sensors']['humidity']}"
                    self.sio.emit('serial_line', {'simulator': self.name, 'line': line})
                    if payload['sensors']['motion']:
                        self.sio.emit('serial_line', {'simulator': self.name, 'line': 'MOTION_DETECTED'})
                    print('[sim] sensor_update sent', payload)
                except Exception as e:
                    print('[sim] emit failed:', e)
            else:
                # REST mode - post to /api/iot/simulate (example)
                self._post_rest('/api/iot/simulate', payload)

            time.sleep(self.interval)

    def start(self):
        if self.mode == 'socketio':
            self.start_socket()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print('[sim] Simulator started (mode=%s, interval=%.2fs)' % (self.mode, self.interval))

    def stop(self):
        self.running = False
        if self.sio:
            try:
                self.sio.disconnect()
            except Exception:
                pass
        print('[sim] Simulator stopped')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--server', '-s', default=DEFAULT_SERVER, help='Server base URL (http://host:port)')
    p.add_argument('--mode', '-m', choices=['socketio', 'rest'], default='socketio', help='Communication mode')
    p.add_argument('--interval', '-i', type=float, default=2.0, help='Sensor update interval seconds')
    p.add_argument('--name', default='tinkercad_sim', help='Simulator name/id')
    args = p.parse_args()

    sim = TinkerCadSimulator(server=args.server, mode=args.mode, interval=args.interval, name=args.name)
    try:
        sim.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sim.stop()


if __name__ == '__main__':
    main()
