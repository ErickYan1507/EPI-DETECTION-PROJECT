import base64
import requests

def main():
    p = 'static/uploads/demo_visualization.jpg'
    try:
        with open(p, 'rb') as f:
            b = f.read()
        b64 = 'data:image/jpeg;base64,' + base64.b64encode(b).decode()
        r = requests.post('http://127.0.0.1:5000/api/detect', json={'image': b64}, timeout=15)
        print('STATUS', r.status_code)
        print(r.text)
    except Exception as e:
        print('ERROR', e)

if __name__ == '__main__':
    main()
