# Comparador de Documentos Visual con Colores

Este proyecto permite comparar hasta 4 documentos (contratos, informes, propuestas, etc.) y resaltar sus diferencias de forma visual mediante colores, facilitando la revisión y el control de versiones.

La comparación se realiza siempre tomando el Documento 1 como referencia base.

---

## Características

- 📄 Comparación múltiple

  - Compara el Documento 1 con el Documento 2.
  
  - Opcionalmente compara también con el Documento 3 y el Documento 4.
  
  - No se realizan comparaciones directas entre documentos secundarios.

- 🔍 Detección precisa de cambios

  - Comparación línea por línea.
  
  - Resaltado palabra por palabra dentro de las líneas modificadas.

- 🎨 Resaltado visual con colores

  - 🟥 Fondo rojo → texto eliminado o modificado del Documento 1.
  
  - 🟩 Fondo verde → texto insertado o modificado en el documento comparado.

- 👁️ Opción para ocultar texto sin cambios

  - Permite visualizar únicamente las diferencias, ideal para documentos extensos.

- 📂 Compatibilidad de formatos

  - PDF
  
  - DOCX
  
  - TXT

- 🌍 Independiente del idioma

  - Funciona con cualquier idioma, ya que compara texto, no significado.

- 🌐 Interfaz web sencilla
  - Construida con Gradio.
  
  - Lista para uso local o despliegue en Hugging Face Spaces.

---

## Cómo usar

1. Subir Documento 1
→ Documento base de comparación.

2. Subir Documento 2
→ Comparado con el Documento 1.

3. (Opcional) Subir Documento 3 y/o Documento 4
→ También comparados con el Documento 1.

4. (Opcional) Activar “Ocultar líneas sin cambios”
→ Para ver solo las diferencias.

Visualizar las diferencias resaltadas por colores.

---
## Librerías usadas

gradio → interfaz web

PyPDF2 → lectura de PDFs

python-docx → lectura de DOCX

difflib.SequenceMatcher → detección de diferencias línea por línea

html → escapar caracteres especiales en el texto

## Uso recomendado

- Revisión de contratos y anexos

- Comparación de versiones de informes

- Revisión de propuestas y documentos técnicos

- Ideal para:

  - Equipos legales
  
  - Gestores documentales
  
  - Equipos de revisión y auditoría

---
## Licencia

MIT License

---
## Autor
Kevin
