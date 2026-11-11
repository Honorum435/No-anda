---
title: torch CUDA mal versionado rompe transformers (Windows, RTX 2060)
date: 2026-06-04
category: build-errors
module: AsistenteLegal (indexado con GPU)
problem_type: build_error
component: tooling
symptoms:
  - "AttributeError: module 'torch' has no attribute 'float8_e8m0fnu' al importar sentence-transformers"
  - "El indexado moria con exit code 5 mostrando solo el warning de Hugging Face (prints perdidos en el buffer)"
  - "Instalar torch CUDA desde el indice cu124 bajo torch 2.6.0 e incompatibilizo transformers"
root_cause: config_error
resolution_type: dependency_update
severity: high
tags: [torch, cuda, transformers, sentence-transformers, openmp, windows, pytorch]
---

# torch CUDA mal versionado rompe transformers (Windows, RTX 2060)

## Problem
Al pasar de torch CPU a torch con CUDA (para indexar embeddings con la GPU), instalar desde el indice `cu124` bajo **torch 2.6.0**, una version vieja incompatible con el `transformers` 5.10 ya instalado. Resultado: todo lo que usa `transformers`/`sentence-transformers` dejo de importar y el indexado quedo bloqueado.

## Symptoms
- `AttributeError: module 'torch' has no attribute 'float8_e8m0fnu'` al hacer `from sentence_transformers import SentenceTransformer`.
- Antes de eso, un crash silencioso: el script terminaba con **exit code 5** mostrando solo el warning de Hugging Face, porque los `print` de progreso quedaban bufferados y se perdian en el corte.

## What Didn't Work
- **`pip install torch --index-url .../whl/cu124 --force-reinstall --no-deps`**: instalo `torch 2.6.0+cu124`. El indice `cu124` ya no recibe versiones nuevas de torch, asi que dio una version vieja sin `torch.float8_e8m0fnu`, atributo que `transformers` 5.10 referencia al importar (`modeling_utils.py`). Romper "hacia atras" no es obvio: uno espera que el build CUDA sea equivalente al CPU, pero quedo 6 minors atras (2.12 -> 2.6).
- **Correr el indexado sin `-u`**: el `exit code 5` sin traceback despistaba. En realidad era un crash nativo (OpenMP) con los prints bufferados; sin salida util no se veia donde moria.

## Solution
Dos cosas:

**1) Instalar el torch CUDA correcto (compatible con transformers).** El indice `cu128` si tiene versiones nuevas. Chequear primero, antes de bajar ~2.5 GB:

```powershell
python -m pip index versions torch --index-url https://download.pytorch.org/whl/cu128
# -> la mas nueva en cu128 era 2.11.0+cu128

python -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128 --force-reinstall --no-deps
```

Verificar:
```python
import torch
print(torch.__version__)               # 2.11.0+cu128
print(torch.cuda.is_available())       # True
print(torch.cuda.get_device_name(0))   # NVIDIA GeForce RTX 2060 SUPER
```

**2) Evitar el crash de OpenMP (exit 5) en Windows.** Setear, ANTES de importar torch:
```python
import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
```
En el proyecto va al tope de `src/comun.py`, que se importa antes que `sentence-transformers`.

## Why This Works
- `transformers` 5.10 usa `torch.float8_e8m0fnu` (dtype float8 E8M0, agregado alrededor de torch 2.7) en el import. torch 2.6.0 no lo tiene -> `AttributeError`; torch 2.11 si -> carga bien. La clave: **el build CUDA de torch tiene que ser >= la version que tu transformers espera**, y los indices viejos (`cu124`) topean en versiones viejas. Elegir el indice CUDA por la version de torch que necesitas, no solo por la version de CUDA del driver.
- El `exit code 5` era OpenMP abortando por cargar `libiomp5md.dll` dos veces (torch + scikit-learn/MKL). `KMP_DUPLICATE_LIB_OK=TRUE` tolera el duplicado. Correr con `python -u` (sin buffer) deja ver los prints hasta el punto del crash.

## Prevention
- Antes de bajar un wheel CUDA pesado, correr `pip index versions torch --index-url <indice>` y elegir un indice (`cu126`/`cu128`/...) con una version de torch **compatible con el transformers ya instalado**. `cu124` quedo congelado en torch 2.6.
- Dejar `os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")` en el modulo de config que se importa primero, para que el indexado no crashee con exit 5 en Windows.
- Ante un error opaco con exit code raro y sin traceback, re-correr con `python -u` para no perder los prints bufferados.

## Related Issues
- Gotcha del mismo proyecto: `gemini-2.0-flash` da cuota 0 en algunas cuentas de Gemini -> usar `gemini-2.5-flash` (anda en la capa gratis).
