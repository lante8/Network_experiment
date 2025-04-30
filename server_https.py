# server_https.py
import http.server, ssl, urllib.parse, os

PORT = 8443
USERS = {"user123": "password456"}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/login.html'):
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.end_headers()
            with open('login.html','rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/login':
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length).decode()
            form = urllib.parse.parse_qs(data)
            user = form.get('username',[''])[0]
            pwd  = form.get('password',[''])[0]
            if USERS.get(user)==pwd:
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"<h1>Accesso OK! Sei hackerato.</h1>")
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"<h1>Credenziali errate!</h1>")
        else:
            self.send_error(404)

# Assicurati di essere nella cartella con login.html, questocert.pem, questakey_rsa.pem
os.chdir(os.path.dirname(__file__))

httpd = http.server.HTTPServer(('0.0.0.0', PORT), Handler)

# Configura SSLContext per TLS 1.2 + suite RSA + ALPN HTTP/1.1
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.maximum_version = ssl.TLSVersion.TLSv1_2

# Disabilita tutti i cipher con PFS, abilita solo una TLS_RSA_WITH_AES_128_CBC_SHA
ctx.set_ciphers('AES128-SHA')

# Forza HTTP/1.1
ctx.set_alpn_protocols(['http/1.1'])

# Carica certificato e chiave RSA (quella che userai in Wireshark)
ctx.load_cert_chain(certfile="questocert.pem", keyfile="nuovakey_rsa.pem")

httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
print(f"🔐 Server HTTPS in ascolto su https://0.0.0.0:{PORT}")
httpd.serve_forever()
