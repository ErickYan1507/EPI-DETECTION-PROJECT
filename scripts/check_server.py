import requests


def check(url):
    try:
        r = requests.get(url, timeout=5)
        print(url, '->', r.status_code)
    except Exception as e:
        print(url, 'error->', repr(e))


if __name__ == '__main__':
    base = 'http://localhost:5000'
    check(base)
    check(base + '/socket.io/?transport=polling&EIO=4')
    check(base + '/unified')
