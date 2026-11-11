# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Un abogado penalista argentino, mayor y poco tecnico, que trabaja solo con su archivo de
causas. Usa la app en su PC con Windows y mouse (como app de escritorio, en su propia
ventana) y a veces desde el celular, en el Wi-Fi de su casa u oficina. Su trabajo con la
app: encontrar donde planteo algo en causas anteriores, armar la ficha de una causa y
redactar borradores de escritos con su propio estilo.

Hoy lo usa una sola persona (el padre del desarrollador). Si el producto se vende, se
adapta para cada abogado: nada personal de este usuario debe quedar fijo en la interfaz.

## Product Purpose

Asistente de IA sobre el archivo de causas del estudio: busca por significado dentro de
los escritos, responde citando de que documento sale cada cosa, arma fichas de causa con
linea de tiempo y redacta borradores en el estilo del abogado, listos para Word. Exito:
que el abogado lo use solo, sin ayuda, y confie en lo que lee porque puede abrir el
original.

## Positioning

El archivo, la busqueda y el historial quedan en la PC del abogado; a la nube (Gemini,
plan gratuito) solo sale el texto minimo, siempre anonimizado, y la respuesta se vuelve a
completar con los datos reales en la PC. Responde con las causas propias del abogado, no
con conocimiento general.

## Operating Context

- Archivo de causas en carpetas por causa (Word, PDF y escaneados con OCR), en la PC o en
  un disco duro externo.
- Se instala con un instalador de Windows y se abre desde un icono en el escritorio.
- El disco externo es el medio para llevar los datos de una PC a otra.
- Escritos penales argentinos: nulidades, excarcelaciones, recursos, sobreseimientos.

## Capabilities and Constraints

- Funciones: Consultar, Resumen de causa, Redactar, Historial, Archivo; acceso desde el
  celular con PIN en la red local.
- La anonimizacion es obligatoria y no se puede desactivar.
- Debe funcionar sin placa de video para consultar; IA en la nube solo gratuita.
- Sin herramientas de pago para armar el instalador; se arma con lo que trae Windows.

## Brand Commitments

- Nombre: "Asistente Legal", sin nombre de estudio.
- Simbolo: la balanza.
- Tratamiento: de usted, formal y claro ("Escriba su consulta", "Elija una causa").

## Evidence on Hand

- Archivo real del usuario (924 documentos, 65 causas): privado, nunca se muestra fuera de
  su PC ni se usa como ejemplo.
- Ejemplos ficticios en `datos/ejemplos/` para pruebas y demostraciones.
- No hay testimonios, clientes ni cifras de uso: no inventarlos.

## Product Principles

- La confianza se gana con la fuente: cada dato muestra de donde sale y se puede abrir.
- Nada del estudio sale sin ocultar: la privacidad es un estado fijo, no una opcion.
- Una persona mayor tiene que poder usarlo sola: textos claros, botones grandes, sin jerga.
- Lo que cuesta trabajo no se pierde: historial, papelera y confirmaciones antes de borrar.

## Accessibility & Inclusion

Usuario mayor con mouse: objetivos de 48 px o mas, contraste WCAG 2.2 AA, tamano de letra
ajustable (A / A+ / A++) y foco visible para teclado.
