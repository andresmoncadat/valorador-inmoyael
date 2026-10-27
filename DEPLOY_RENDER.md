# Publicar el Valorador InmoYael en Render (gratis)

La app ya está lista para desplegar. Son ~10 minutos. Lo hacemos juntos:
yo te voy diciendo cada paso; tú haces los que necesitan tu cuenta.

## Lo que necesitas (gratis)
1. Una cuenta en **GitHub** → https://github.com/signup
2. Una cuenta en **Render** → https://render.com (entra con "Sign in with GitHub")

## Pasos
1. **Sube el código a GitHub**
   - Crea un repositorio nuevo (ej. `valorador-inmoyael`).
   - Sube estos 4 archivos: `servidor.py`, `index.html`, `requirements.txt`, `render.yaml`.
   - (Andrés tiene estos archivos; también se pueden subir arrastrándolos en la web de GitHub.)

2. **Conecta Render**
   - En Render → **New** → **Web Service** → elige tu repositorio.
   - Render leerá `render.yaml` solo. Si pregunta:
     - Runtime: **Python**
     - Build command: `pip install -r requirements.txt`
     - Start command: `python3 servidor.py`
     - Plan: **Free**
   - Pulsa **Create Web Service**.

3. **Listo**
   - En 2-3 minutos tendrás un enlace tipo `https://valorador-inmoyael.onrender.com`.
   - Ese enlace se lo pasas al equipo. (El plan gratis "duerme": la 1ª visita tarda ~30 s.)

## (Opcional) Tu dominio: valorador.inmoyael.com
4. En Render → el servicio → **Settings** → **Custom Domains** → añade `valorador.inmoyael.com`.
   Render te dirá un destino CNAME.
5. En **Hostinger** → tu dominio → **Zona DNS** → añade un registro **CNAME**:
   - Nombre: `valorador`
   - Apunta a: (el valor que te dé Render)
6. Espera unos minutos → `https://valorador.inmoyael.com` con candado automático.

## (Opcional) Redacción con IA (Claude)
Para que Claude redacte el análisis, en Render → **Environment** → añade:
`ANTHROPIC_API_KEY = tu-clave`  (y ampliamos el `servidor.py` para usarla).
