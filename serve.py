#!/usr/bin/env python3
"""
Martian Map — mini serveur local
(Team Trajectory Error, NASA Space Apps 2026. SI disclosure: written with an AI assistant, Claude by Anthropic, from the team's specifications.)
 (Python 3, aucune installation requise).

  python serve.py            puis ouvrir http://localhost:8000

Il fait deux choses :
  1. il sert le site (index.html) ;
  2. il relaie (/proxy?url=...) les requêtes vers les serveurs de données NASA/USGS,
     pour contourner les blocages CORS du navigateur. Il transmet l'en-tête "Range",
     ce qui permet de ne télécharger QUE le morceau de carte demandé.

Par sécurité, seuls les domaines de la liste ALLOWED sont relayés.
"""
import http.server
import socketserver
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import os
import sys

PORT = int(os.environ.get("PORT", "8000"))
# Domaines relayés (le domaine exact ou ses sous-domaines)
ALLOWED = (
    "amazonaws.com",            # fichiers d'altitude USGS (HiRISE, CTX, MOLA) sur AWS
    "usgs.gov",                 # catalogue STAC et cartes USGS Astrogeology
    "nasa.gov",                 # Mars Trek, relevés météo des rovers
    "www-mars.lmd.jussieu.fr",  # Mars Climate Database (LMD / ESA / CNES)
)
TIMEOUT = 180  # secondes : certaines requêtes du modèle climatique sont longues
# Serveurs qui ne répondent qu'en http (pas de https) : autorisés en http, avec un délai court
HTTP_ONLY = ("astropedia.astrogeology.usgs.gov",)
SHORT_TIMEOUT = 20


def allowed(host):
    return any(host == d or host.endswith("." + d) for d in ALLOWED)


PASS_HEADERS = ("Content-Type", "Content-Length", "Content-Range", "Accept-Ranges", "Last-Modified", "ETag")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/proxy/ping":
            return self._send(200, b"pong", "text/plain")
        if self.path.startswith("/proxy?"):
            return self._proxy("GET")
        return super().do_GET()

    def do_HEAD(self):
        if self.path.startswith("/proxy?"):
            return self._proxy("HEAD")
        return super().do_HEAD()

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _proxy(self, method):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        url = (qs.get("url") or [""])[0]
        host = urllib.parse.urlparse(url).hostname or ""
        ok_scheme = url.startswith("https://") or (url.startswith("http://") and host in HTTP_ONLY)
        if not ok_scheme or not allowed(host):
            return self._send(403, f"Domaine non autorise : {host}".encode(), "text/plain")
        # certains serveurs refusent les clients qui ne ressemblent pas à un navigateur
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/124.0 Safari/537.36 MartianMap/1.0",
                   "Accept": self.headers.get("Accept", "*/*")}
        if self.headers.get("Range"):
            headers["Range"] = self.headers["Range"]
        req = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=SHORT_TIMEOUT if host in HTTP_ONLY else TIMEOUT) as r:
                # lecture partielle demandée mais ignorée par le serveur distant : on ne relaie pas un fichier géant
                size = int(r.headers.get("Content-Length") or 0)
                if self.headers.get("Range") and r.status == 200 and size > 20_000_000:
                    return self._send(502, b"Le serveur distant ne permet pas la lecture partielle (Range)", "text/plain")
                self.send_response(r.status)
                for h in PASS_HEADERS:
                    if r.headers.get(h):
                        self.send_header(h, r.headers[h])
                self.end_headers()
                if method == "GET":
                    while True:
                        chunk = r.read(65536)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
        except urllib.error.HTTPError as e:
            self._send(e.code, f"Erreur distante {e.code} pour {url}".encode(), "text/plain")
        except Exception as e:  # réseau, délai, certificat…
            sys.stderr.write(f"  [proxy] echec pour {url} : {e!r}\n")
            self._send(502, f"Proxy : {e!r}".encode(), "text/plain")

    def log_message(self, fmt, *args):
        sys.stderr.write("  " + (fmt % args) + "\n")


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with Server(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Martian Map : {url}   (Ctrl+C pour arreter)")
        if not os.environ.get("PORT"):          # en local seulement (sur un hébergeur, pas de navigateur)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        httpd.serve_forever()
