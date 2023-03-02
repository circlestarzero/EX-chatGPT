from urllib.parse import urlparse, parse_qs
import http.server
import socketserver
import socket
import requests
import json
cookies = {
    # YOUR COOKIE
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}


HOST = '127.0.0.1'  # Localhost
PORT = 1111  # Port number
TIMEOUT = 5  # 5 second timeout


class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        query = query_params.get('query', [''])[0]
        params = {
            'input': query,
            'format': 'plaintext',
            'output': 'JSON',
            'appid': 'YOUR_APP_ID', #GET from WolframAlpha
        }
        responseFromWolfram = requests.get(
            'https://api.wolframalpha.com/v2/query', params=params, cookies=cookies, headers=headers)
        pods = responseFromWolfram.json()['queryresult']['pods'][:5]
        print(pods)
        pods = json.dumps(pods)
        response = f"{pods}".encode()
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header('content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(response))

while True:
    with socketserver.TCPServer((HOST, PORT), MyHandler) as httpd:
        httpd.socket.settimeout(TIMEOUT)
        print(f"Serving at port {PORT}")
        try:
            httpd.serve_forever()
        except socket.timeout:
            print(f"Timeout after {TIMEOUT} seconds")
