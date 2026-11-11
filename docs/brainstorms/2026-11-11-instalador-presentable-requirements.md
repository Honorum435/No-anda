---
date: 2026-11-11
topic: instalador-presentable
---

# Instalador grafico y app presentable

## Resumen

Un instalador grafico para Windows con la identidad del Asistente Legal (balanza, marino,
dorado, marfil) que guia la instalacion con pasos y progreso, trae solo el archivo de
causas desde el disco externo y termina con "Abrir Asistente Legal". La app pierde "Ver que
se envio a Gemini" y recibe una pasada de pulido visual.

---

## Contexto

Hoy el instalador es un .exe que abre una ventana negra de consola con texto tecnico
durante 15 a 30 minutos. Para un abogado mayor y poco tecnico no transmite confianza ni
deja claro si algo salio mal. Ademas, pasar el archivo de causas (indice, originales y
clave) es un paso manual de copiar carpetas que hoy depende del hijo.

El papa ya tiene un disco duro externo con sus documentos: es el medio natural para
llevar los datos de una PC a la otra.

La funcion "Ver que se envio a Gemini" se considero innecesaria: la anonimizacion es
obligatoria y no hace falta auditarla desde la interfaz.

---

## Decisiones clave

- **Instalador hecho con lo que trae Windows.** No se instalan herramientas nuevas en la PC
  de desarrollo; el diseno del instalador es propio, no una plantilla generica.
- **El instalador sigue llevando solo el programa.** Los datos (indice, originales, clave)
  viajan en el disco externo, nunca dentro del .exe.
- **Los datos se buscan solos.** El instalador revisa al lado de si mismo y en los discos
  conectados; el usuario solo confirma.
- **Registro por usuario, sin administrador.** La app figura en "Agregar o quitar
  programas" sin pedir permisos; solo el acceso desde el celular pide administrador.
- **Actualizar = volver a instalar.** Correr un instalador nuevo reemplaza el programa y
  respeta los datos.

---

## Requisitos

**App**

- R1. Desaparece "Ver que se envio a Gemini" de consultas, fichas y borradores; las
  respuestas dejan de guardar lo enviado.
- R2. Pasada de pulido visual sin cambiar funciones: se mantienen los objetivos de 48 px o
  mas, el contraste AA, los tamanos de letra A / A+ / A++ y el modo celular.

**Instalador: ventana y marca**

- R3. Un solo archivo para doble clic que abre una ventana grafica con la balanza, los
  colores y el titulo serif de la app. No aparece ninguna ventana de consola.
- R4. Bienvenida: que se va a instalar, en que carpeta, cuanto tarda aproximadamente la
  primera vez y cuanto descarga; si ya esta instalado, la pantalla dice "Actualizar".
- R5. Opcion "Usarlo tambien desde el celular", desmarcada por defecto, que avisa que va a
  pedir permiso de administrador.

**Instalador: datos del estudio**

- R6. Busca la carpeta de datos del asistente al lado del instalador y en los discos
  conectados (incluido el disco externo) y muestra lo encontrado: ubicacion, tamano y
  cantidad de documentos.
- R7. Copia los datos encontrados con un clic, con "Elegir carpeta..." para indicarla a
  mano y "Seguir sin datos" (se agregan despues desde la pestana Archivo).
- R8. Si la instalacion ya tiene un archivo de causas, no lo pisa sin preguntar; la
  respuesta por defecto es conservar el existente.

**Instalador: progreso y cierre**

- R9. Pantalla de progreso con la lista de pasos y el estado de cada uno (pendiente, en
  curso, listo, con aviso), una barra general, el texto de lo que esta haciendo y un
  "Ver detalle" plegado con el registro tecnico.
- R10. Cerrar la ventana durante la instalacion pide confirmacion.
- R11. Pantalla final: "Listo" o "Instalado con avisos" con los avisos en lenguaje llano,
  boton principal "Abrir Asistente Legal" y "Cerrar".
- R12. Crea los iconos de escritorio y menu Inicio con la balanza (como hoy).
- R13. Registra la app en "Agregar o quitar programas" con nombre, icono y desinstalacion;
  desinstalar quita iconos y registro y conserva los datos.

**Instalador: accesibilidad y seguridad**

- R14. Texto legible para un usuario mayor, botones grandes, Enter activa el boton
  principal, foco visible y uso completo con teclado.
- R15. El instalador no contiene datos privados (causas, indice, historial, PIN, clave).

---

## Flujos

- F1. Primera instalacion con el disco externo
  - **Disparo:** el papa conecta el disco externo y hace doble clic en el instalador.
  - **Pasos:** bienvenida muestra los datos encontrados en el disco; confirma; progreso
    por pasos; pantalla final.
  - **Resultado:** app instalada con su archivo de causas, iconos creados, "Abrir
    Asistente Legal" la abre.
  - **Cubierto por:** R3, R4, R6, R7, R9, R11, R12, R13
- F2. Actualizacion
  - **Disparo:** el hijo le pasa un instalador nuevo.
  - **Pasos:** bienvenida dice "Actualizar"; los datos existentes se conservan.
  - **Resultado:** programa nuevo, mismos datos e historial.
  - **Cubierto por:** R4, R8

---

## Ejemplos de aceptacion

- AE1. **Cubre R6, R7.** Dado un disco externo con la carpeta de datos del asistente,
  cuando abre el instalador, entonces ve "Encontre tu archivo de causas en E:\..." con su
  tamano y lo copia con un clic.
- AE2. **Cubre R7.** Dado que no hay datos en ningun disco, cuando abre el instalador,
  entonces ve "No encontre datos" con "Elegir carpeta..." y "Seguir sin datos".
- AE3. **Cubre R6.** Dado que hay datos en dos lugares, cuando abre el instalador, entonces
  se propone el mas reciente y se puede elegir el otro.
- AE4. **Cubre R8.** Dado que ya hay un archivo de causas instalado, cuando se encuentran
  datos en el disco, entonces pregunta si reemplazar y por defecto conserva el existente.
- AE5. **Cubre R5, R11.** Dado que marco el celular y rechaza el permiso de administrador,
  entonces la instalacion termina igual y la pantalla final lo muestra como aviso.

---

## Alcance

- Firma digital del instalador (evitaria el aviso "Windows protegio tu PC"): fuera.
- Actualizaciones automaticas: fuera.
- Desinstalar borrando los datos: fuera, los datos siempre se conservan.
- Correccion automatica de la letra del disco externo: fuera; se sigue corrigiendo desde la
  pestana Archivo (el usuario la va a ajustar despues).

---

## Supuestos

- La PC destino tiene Windows 10 u 11 (traen .NET Framework 4) e internet para instalar.
- El hijo deja en el disco externo la carpeta de datos del asistente tal como esta en su PC.
- Los documentos originales pueden quedar en el disco externo; la app ya corrige rutas
  cuando la carpeta cambia de lugar.

---

## Preguntas abiertas

**Para la planificacion**

- Como reconoce el instalador una carpeta de datos valida del asistente.
- Como informa el motor de instalacion su progreso a la ventana grafica.

---

## Fuentes

- `instalar.ps1`: los 8 pasos actuales del motor de instalacion.
- `empaquetar.ps1`: arma el .exe actual con el programa embebido y el control de datos
  privados.
- `src/estilos.py` y `.streamlit/config.toml`: identidad visual y tokens de color.
- `docs/brainstorms/`: primer documento de requisitos del proyecto.
