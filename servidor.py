#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Valorador InmoYael — datos REALES, fuentes gratis y legales.
  dirección  -> Catastro (Consulta_DNPLOC) -> referencia catastral
  referencia -> Catastro (Consulta_DNPRC)   -> m2, año, uso, clase
  referencia -> Catastro (Consulta_CPMRC)   -> coordenadas
El entorno (OpenStreetMap/Overpass) lo pide el navegador directamente.
Sin scraping de portales. Sin APIs de pago.
"""
import http.server, socketserver, urllib.parse, urllib.request, re, json, os

PORT = int(os.environ.get("PORT", "8795"))
HERE = os.path.dirname(os.path.abspath(__file__))
CAT = "https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/"
UA = {"User-Agent": "InmoYael-Valorador-Demo/1.0 (prueba interna)"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

def first(tag, x):
    m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), x, re.S)
    return m.group(1).strip() if m else ""

def consulta_catastro(p):
    prov = (p.get("provincia", ["MADRID"])[0] or "MADRID").upper()
    muni = (p.get("municipio", [""])[0] or "").upper()
    rc = (p.get("rc", [""])[0] or "").strip().upper().replace(" ", "")
    nunidades = None

    if not rc:
        sigla = (p.get("sigla", ["CL"])[0] or "CL").upper()
        calle = (p.get("calle", [""])[0] or "").upper()
        numero = (p.get("numero", [""])[0] or "").strip()
        q = urllib.parse.urlencode({
            "Provincia": prov, "Municipio": muni, "Sigla": sigla,
            "Calle": calle, "Numero": numero,
            "Bloque": "", "Escalera": "", "Planta": "", "Puerta": "",
        })
        loc = fetch(CAT + "OVCCallejero.asmx/Consulta_DNPLOC?" + q)
        err = first("des", loc)
        pares = re.findall(r"<pc1>([^<]+)</pc1>\s*<pc2>([^<]+)</pc2>", loc)
        if not pares:
            return {"error": "No se encontró esa dirección en Catastro. Revisa municipio, tipo de vía, nombre y número."
                             + (" (" + err + ")" if err else "")}
        # Elegir la parcela principal: la que agrupa más unidades (el edificio de viviendas)
        from collections import Counter
        best = Counter(pares).most_common(1)[0][0]
        rc = best[0] + best[1]
        nunidades = len(pares)

    rc14 = rc[:14]

    def dnprc(rcx):
        return fetch(CAT + "OVCCallejero.asmx/Consulta_DNPRC?" +
                     urllib.parse.urlencode({"Provincia": "", "Municipio": "", "RC": rcx}))

    if len(rc) >= 20:
        dnp = dnprc(rc); rc_show = rc
    else:
        dnp = dnprc(rc14); rc_show = rc14
        if not first("sfc", dnp):
            # Es un edificio: Catastro devuelve la lista de unidades -> entrar en una vivienda
            units = re.findall(r"<rc>\s*<pc1>([^<]+)</pc1>\s*<pc2>([^<]+)</pc2>\s*"
                               r"<car>([^<]+)</car>\s*<cc1>([^<]+)</cc1>\s*<cc2>([^<]+)</cc2>", dnp)
            chosen = None
            for u in units[:8]:
                rc20 = "".join(u)
                ux = dnprc(rc20)
                if first("luso", ux) == "Residencial":
                    dnp, chosen = ux, rc20
                    break
            if chosen is None and units:
                rc20 = "".join(units[0]); dnp, chosen = dnprc(rc20), rc20
            if chosen:
                rc_show = chosen

    err = first("des", dnp)
    sfc = first("sfc", dnp)
    if not sfc and err:
        return {"error": "Catastro: " + err}

    tv, nv, pnp = first("tv", dnp), first("nv", dnp), first("pnp", dnp)
    np, nm = first("np", dnp), first("nm", dnp)

    cp = fetch(CAT + "OVCCoordenadas.asmx/Consulta_CPMRC?" +
               urllib.parse.urlencode({"Provincia": "", "Municipio": "", "SRS": "EPSG:4326", "RC": rc14}))
    lon, lat, ldt = first("xcen", cp), first("ycen", cp), first("ldt", cp)

    return {
        "rc": rc_show,
        "direccion": (" ".join(x for x in [tv, nv, pnp] if x)).strip() or ldt,
        "municipio": nm or muni, "provincia": np or prov,
        "clase": {"UR": "Urbano", "RU": "Rústico"}.get(first("cn", dnp), first("cn", dnp)),
        "uso": first("luso", dnp),
        "sup_construida": sfc,
        "anio": first("ant", dnp),
        "lat": lat, "lon": lon, "ldt": ldt,
        "nunidades": nunidades,
        "fuente": "Sede Electrónica del Catastro (datos no protegidos)",
    }

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
                self._send(200, f.read(), "text/html")
        elif u.path == "/api/catastro":
            try:
                data = consulta_catastro(urllib.parse.parse_qs(u.query))
            except Exception as e:
                data = {"error": "No se pudo consultar Catastro: " + str(e)}
            self._send(200, json.dumps(data, ensure_ascii=False), "application/json")
        else:
            self._send(404, "no encontrado", "text/plain")

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), H) as httpd:
        print("Valorador InmoYael (demo) en http://localhost:%d" % PORT)
        print("(accesible también por red local y por túnel/nube)")
        httpd.serve_forever()
