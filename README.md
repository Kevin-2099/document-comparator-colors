# 📄 Comparador Visual de Documentos

Este proyecto es una herramienta web avanzada para comparar documentos y detectar diferencias de forma visual, precisa y estructurada.

Permite comparar hasta **4 documentos o textos simultáneamente**, resaltando cambios con colores, estadísticas, navegación entre diferencias y exportación de resultados.

La comparación puede realizarse por **líneas, oraciones o párrafos**, y siempre parte de un esquema de comparación configurable por el usuario.

## ✨ Características

### 📂 Comparación múltiple

- Permite comparar hasta 4 documentos o textos
- Modos de comparación:
  - Base vs todos
  - Comparación circular entre documentos
- Entrada híbrida: archivos o texto pegado

### 🧠 Comparación inteligente

- Comparación por:
  - Línea
  - Oración
  - Párrafo
- Detección precisa de cambios con diffs avanzados
- Resaltado palabra por palabra en cambios internos

### 🎨 Resaltado visual

- 🟥 Eliminaciones
- 🟩 Inserciones
- 🟨 Modificaciones

Vista lado a lado tipo editor de diferencias

### 📊 Estadísticas automáticas

- Porcentaje de similitud
- Líneas añadidas
- Líneas eliminadas
- Líneas modificadas
- Líneas iguales

### 🔖 Navegación entre cambios

- Enlaces directos a cada diferencia
- Navegación rápida dentro del documento

### 🕒 Historial de sesión

- Guarda comparaciones realizadas
- Muestra:
  - Hora
  - Documentos usados
  - Similitud promedio

### 💾 Exportación

- Exportación a HTML
- Incluye estilos, colores y estructura completa
- Archivo listo para compartir o archivar

### ⚙️ Opciones avanzadas

- Ocultar líneas sin cambios
- Ignorar mayúsculas/minúsculas
- Ignorar espacios en blanco
- Ajuste de contexto alrededor de cambios

### 📂 Formatos soportados

- PDF (pdfplumber)
- DOCX
- ODT
- TXT
- Texto pegado directamente

### 🌍 Independiente del idioma

- Funciona con cualquier idioma
- Basado en comparación de texto, no significado

### 🌐 Interfaz web moderna

- Construida con Gradio Blocks
- Diseño por pestañas
- Vista lado a lado profesional
- Interfaz interactiva y responsive

## 🚀 Cómo usar

### 1. Cargar documentos o texto

Cada entrada permite:

- Subir archivo (PDF, DOCX, ODT, TXT)
- O pegar texto manualmente

Si ambos están presentes, el texto pegado tiene prioridad.

### 2. Configurar opciones

Opcionalmente puedes:

- Elegir granularidad (línea, oración o párrafo)
- Activar ocultar coincidencias
- Ignorar mayúsculas
- Ignorar espacios
- Seleccionar modo de comparación

### 3. Ejecutar comparación

Presiona:

🔍 Comparar

### 4. Revisar resultados

- Diferencias resaltadas por colores
- Estadísticas automáticas
- Navegación entre cambios
- Historial de sesión

### 5. Exportar

En la pestaña de exportación:

💾 Genera un archivo HTML descargable

## 📦 Librerías principales

- gradio → interfaz web
- pdfplumber → lectura avanzada de PDF
- python-docx → lectura de DOCX
- odfpy → soporte ODT
- difflib → detección de diferencias
- html / re → procesamiento de texto
- tempfile → exportación HTML

## 💼 Casos de uso

### 📑 Revisión de contratos

- Contratos legales
- Anexos
- Versiones de cláusulas

### 📊 Auditoría y control

- Versionado de documentos
- Revisiones internas
- Control de cambios

### 🧾 Gestión documental

- Informes técnicos
- Propuestas comerciales
- Documentación corporativa

## 👥 Ideal para

- Abogados
- Equipos legales
- Consultores
- Auditores
- Equipos de compliance
- Gestión documental

## ⚠️ Notas importantes

- Comparación basada en texto, no significado
- No interpreta contexto legal o semántico
- La similitud es estructural
- El rendimiento depende del tamaño de los documentos

## 📄 Licencia

Este proyecto se distribuye bajo una **licencia propietaria con acceso al código (source-available)**.

El código fuente se pone a disposición únicamente para fines de **visualización, evaluación y aprendizaje**.

❌ No está permitido copiar, modificar, redistribuir, sublicenciar, ni crear obras derivadas del software o de su código fuente sin autorización escrita expresa del titular de los derechos.

❌ El uso comercial del software, incluyendo su oferta como servicio (SaaS), su integración en productos comerciales o su uso en entornos de producción, requiere un **acuerdo de licencia comercial independiente**.

📌 El texto **legalmente vinculante** de la licencia es la versión en inglés incluida en el archivo `LICENSE`. 

Se proporciona una traducción al español en `LICENSE_ES.md` únicamente con fines informativos. En caso de discrepancia, prevalece la versión en inglés.

## Autor
Kevin-2099
