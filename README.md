# Comparador de Documentos Visual con Colores

Este proyecto permite comparar 2-3 documentos similares (contratos, informes, propuestas, etc.) y resaltar sus diferencias de manera visual utilizando colores.

---

## Características

- Compara **Documento 1 con Documento 2** y, si se sube, también **Documento 1 con Documento 3**.  
- Diferencias resaltadas con **colores**:
  - **Rojo** → contenido del Documento 1  
  - **Verde** → contenido del documento comparado  
- Compatible con **PDF, DOCX y TXT**.  
- Funciona en **cualquier idioma**, ya que compara texto línea por línea.  

---

## Cómo usar

1. Subir Documento 1 (base de comparación).  
2. Subir Documento 2 (comparado con el Documento 1).  
3. Opcional: subir Documento 3 (comparado con el Documento 1).  
4. Visualizar diferencias resaltadas en colores.  

> Nota: No se comparan directamente el segundo y tercer documento.

---
## Librerías usadas

gradio → interfaz web

PyPDF2 → lectura de PDFs

python-docx → lectura de DOCX

difflib.SequenceMatcher → detección de diferencias línea por línea

html → escapar caracteres especiales en el texto

## Uso recomendado

Revisar contratos, informes o propuestas

Ideal para equipos de revisión o gestores de documentos

---
## Licencia

MIT License

---
## Autor
Kevin
