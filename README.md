# Asistente Legal (penal) — papá

Asistente de IA sobre el archivo de causas del estudio. Busca **por significado** dentro
de los documentos, responde **citando de qué escrito sale** cada cosa, arma **fichas de
causa** con línea de tiempo y **redacta borradores** con el estilo de los escritos del
estudio. Se usa como **app de escritorio** y también desde el **celular**.

- La búsqueda, el índice, el historial y el dictado son **100 % locales** (el texto no sale
  de la PC).
- Solo el paso de **redactar** usa Gemini, y antes se **ocultan** nombres, DNI, domicilios,
  teléfonos, CBU y patentes.

Para instalarlo en otra PC: ver **[INSTALAR.md](INSTALAR.md)**.

## Qué hace cada parte

| Archivo | Para qué sirve |
|---|---|
| `src/app.py` | La app (Consultar, Resumen de causa, Redactar, Historial, Archivo) |
| `src/estilos.py` | Diseño: tamaños para mouse (Fitts), celular, foco visible |
| `src/buscar.py` / `src/indexar.py` | Búsqueda por significado / armado del índice |
| `src/actualizar.py` / `src/ocr.py` | Agregar documentos nuevos / leer PDF escaneados |
| `src/anonimizar.py` | Ocultar datos personales antes de la nube |
| `src/preguntar.py`, `src/ficha.py`, `src/redactar.py` | Respuestas, fichas y borradores |
| `src/celular.py`, `src/seguridad.py` | Acceso desde el celular (red local, con PIN) |
| `src/exportar.py` | Word y PDF (títulos, viñetas, negritas y tablas) |
| `abrir.vbs` / `abrir.ps1` | Abre la app en su propia ventana |
| `empaquetar.ps1` | Arma `dist\Instalar Asistente Legal.exe` |
| `instalar.ps1` | Instala todo en la PC (lo llama el instalador) |

## Para desarrollar (en esta PC)

```powershell
.\correr_app.ps1                 # la app en el navegador
.\buscar.ps1 "nulidad de allanamiento sin orden"   # búsqueda por terminal
.\actualizar.ps1                 # bajar de Drive lo nuevo e indexarlo
```

> Si Gemini se queja del nombre del modelo, corré `python src\listar_modelos.py` y
> cambiá `MODELO_GEMINI` en `src/comun.py`.

## Privacidad (importante, es penal)

- Indexar, buscar, dictar e historial **no envían nada a internet**.
- La app de escritorio escucha **solo en la propia PC**. El acceso desde el celular es una
  copia aparte, en la red local, que **siempre pide PIN**.
- Redactar con Gemini **sí** envía fragmentos, anonimizados. La anonimización es una ayuda
  fuerte, **no una garantía**: revisá siempre el resultado.
- Para datos reales conviene una **clave de plan pago**: con el plan gratuito, Google puede
  usar lo que se envía para mejorar sus productos.
