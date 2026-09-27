# ⚖️ Asistente Legal IA

Un asistente que "aprende" del archivo de juicios de un abogado y responde
preguntas **citando el documento exacto** de donde sacó cada dato, al estilo
NotebookLM.

No inventa: si algo no está en los documentos cargados, lo dice.

---

## Cómo funciona (en simple)

La IA no se reentrena. Se usa una técnica llamada **RAG**:

1. Se guarda cada juicio partido en pedacitos.
2. Cuando hacés una pregunta, el sistema busca los pedacitos que hablan del tema.
3. Se los pasa a la IA (Claude) y ésta responde **solo** con eso, poniendo
   numeritos `[1]` `[2]` que podés tocar para leer el pasaje original.

Es como un abogado brillante que no conoce tus casos, pero al que le ponés
sobre el escritorio las hojas exactas que necesita antes de cada respuesta.

---

## Instalación (una sola vez)

Necesitás [Node.js](https://nodejs.org) instalado.

```bash
npm install
```

Después copiá el archivo `.env.example` y renombralo a `.env`.

### Qué IA usar

**Opción A — Gemini (una sola clave, con plan gratuito).** Cubre todo: redactar
las respuestas, buscar por significado y leer PDF escaneados. La clave se saca
en [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

```
GEMINI_API_KEY=...
```

> ⚠️ En el plan **gratuito** de Google, tus prompts y los archivos que subís
> pueden usarse para mejorar sus productos, y revisores humanos pueden leerlos.
> Para expedientes con datos de clientes, tenelo presente: en el plan pago no los
> usan. Si eso es un problema, usá la Opción B o mirá *Reducir la exposición*.

**Opción B — Claude + Voyage (dos claves, ambas pagas).** Más caro, pero no
entrenan con tus datos.

```
ANTHROPIC_API_KEY=sk-ant-...     # console.anthropic.com
VOYAGE_API_KEY=pa-...            # voyageai.com
CLAUDE_MODEL=claude-haiku-4-5    # opcional: más económico
```

El proveedor se elige solo: si hay `GEMINI_API_KEY` usa Gemini, si no Claude.
Para forzarlo, poné `LLM_PROVIDER=gemini` o `LLM_PROVIDER=claude`.

Si Gemini devuelve un error 404 de modelo, los nombres cambiaron:

```bash
npm run modelos     # lista los que tu clave tiene habilitados
```

> **Sin ninguna clave también anda**, en **modo demostración**: cargás documentos,
> los buscás por palabras y ves la interfaz completa con las citas. Lo único que
> no hace es redactar la respuesta. Sirve para mostrar cómo funciona sin gastar.

---

## Usarlo en la propia computadora

```bash
npm start
```

Abrí <http://localhost:3001>. La **primera vez** te va a pedir crear el usuario
administrador (solo se puede desde esta computadora, nunca por internet).

---

## Usarlo online (desde el celular o el estudio)

La computadora hace de servidor y un **túnel** le da una dirección web pública.
Los juicios **nunca salen de la computadora**.

### 1. Instalar `cloudflared` (una sola vez)

- **Windows**: `winget install --id Cloudflare.cloudflared`
- **Mac**: `brew install cloudflared`
- **Linux**: ver la [guía oficial](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

### 2. Encender todo

```bash
npm run online
```

En la consola va a aparecer una dirección tipo:

```
https://algo-random-aca.trycloudflare.com
```

Esa es la dirección para compartir con el estudio. Funciona desde cualquier lado
mientras la computadora esté encendida y con internet.

> ⚠️ La dirección **cambia** cada vez que reiniciás. Para una fija hace falta una
> cuenta gratis de Cloudflare y un "named tunnel".

---

## Personas del estudio

En el panel izquierdo, en **👥 Personas del estudio**, podés dar de alta a cada
persona con su usuario y contraseña, o darles de baja.

También desde la terminal:

```bash
npm run usuario -- agregar maria SuContraseña123
npm run usuario -- listar
npm run usuario -- quitar maria
```

---

## Los cuatro modos

| Modo | Para qué sirve |
|---|---|
| **Preguntar** | Responde dudas puntuales sobre los casos |
| **Redactar** | Genera borradores de escritos basados en casos previos |
| **Precedentes** | Busca casos anteriores parecidos al que le describas |
| **Resumir** | Resume juicios largos de forma estructurada |

Con las casillas ☑ de la izquierda elegís **en qué documentos** buscar.

---

## Privacidad

- Los juicios y el índice viven en `server/data/`, que **nunca se sube a git**.
- A la API de Anthropic solo viajan los pedacitos necesarios para cada pregunta,
  no el archivo completo.
- El acceso está protegido por usuario y contraseña, con freno automático a los
  intentos de adivinarla.
- Las contraseñas se guardan cifradas (scrypt), nunca en texto plano.

**Importante**: es una herramienta de apoyo. El criterio profesional y la
verificación final siempre son del abogado.

---

## Comandos

| Comando | Qué hace |
|---|---|
| `npm start` | Construye y arranca la app (uso local) |
| `npm run online` | Arranca la app + el túnel público |
| `npm run dev:all` | Modo desarrollo (recarga automática) |
| `npm run usuario` | Gestión de usuarios por terminal |
| `npm run modelos` | Lista los modelos de Gemini que tu clave habilita |
