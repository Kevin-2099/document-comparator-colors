import gradio as gr
from difflib import SequenceMatcher
import docx
from PyPDF2 import PdfReader
import html

# =========================
# Función para extraer texto de un archivo
# =========================
def extract_text(file):
    if not file or not hasattr(file, "name"):
        return None  # Archivo no subido o inválido
    try:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file.name)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text
        elif file.name.endswith(".docx"):
            doc = docx.Document(file.name)
            return "\n".join([p.text for p in doc.paragraphs])
        else:  # txt u otros
            return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Error leyendo el archivo: {e}"

# ======================================
# Función para resaltar cambios por palabra
# ======================================
def highlight_word_diff(line1, line2):
    matcher = SequenceMatcher(None, line1.split(), line2.split())
    result = ""
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            result += " ".join(line1.split()[i1:i2]) + " "
        elif tag == "replace":
            result += f"<span style='background-color:#ffcccc'>{' '.join(line1.split()[i1:i2])}</span> "
            result += f"<span style='background-color:#ccffcc'>{' '.join(line2.split()[j1:j2])}</span> "
        elif tag == "delete":
            result += f"<span style='background-color:#ffcccc'>{' '.join(line1.split()[i1:i2])}</span> "
        elif tag == "insert":
            result += f"<span style='background-color:#ccffcc'>{' '.join(line2.split()[j1:j2])}</span> "
    return result.strip()

# =========================================
# Función para resaltar cambios entre textos
# =========================================
def highlight_changes_colors(text1, text2):
    html_diff = ""
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    s = SequenceMatcher(None, lines1, lines2)
    
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "equal":
            for l1 in lines1[i1:i2]:
                html_diff += html.escape(l1) + "<br>"
        else:
            max_lines = max(i2-i1, j2-j1)
            for k in range(max_lines):
                l1 = lines1[i1+k] if i1+k < i2 else ""
                l2 = lines2[j1+k] if j1+k < j2 else ""
                html_diff += highlight_word_diff(l1, l2) + "<br>"
    return html_diff

# =========================================
# Función principal para comparar varios docs
# =========================================
def compare_docs(doc1, doc2, doc3=None, doc4=None, hide_equal=False):
    docs = [doc1, doc2, doc3, doc4]
    texts = []
    for f in docs:
        t = extract_text(f)
        if t is not None:
            texts.append(t)
    
    if len(texts) < 2:
        return "<p style='color:red'>Sube al menos dos documentos válidos para comparar.</p>"
    
    diffs_html = ""
    base_text = texts[0]
    for idx, t in enumerate(texts[1:], start=2):
        diffs_html += f"<h3>Comparación Documento 1 ↔ Documento {idx}</h3>"
        diff = highlight_changes_colors(base_text, t)
        if hide_equal:
            diff_lines = [line for line in diff.split("<br>") if "background-color" in line]
            diff = "<br>".join(diff_lines)
        diffs_html += diff + "<hr>"
    
    return diffs_html

# =========================================
# Interfaz Gradio
# =========================================
iface = gr.Interface(
    fn=compare_docs,
    inputs=[
        gr.File(label="Documento 1 (PDF, DOCX, TXT)"),
        gr.File(label="Documento 2 (PDF, DOCX, TXT)"),
        gr.File(label="Documento 3 (Opcional, PDF, DOCX, TXT)"),
        gr.File(label="Documento 4 (Opcional, PDF, DOCX, TXT)"),
        gr.Checkbox(label="Ocultar líneas sin cambios", value=False)
    ],
    outputs=[gr.HTML(label="Diferencias resaltadas")],
    title="Comparador Visual de Documentos",
    description="""
    Comparación visual de documentos PDF, DOCX o TXT. 
    Los cambios se resaltan con colores: 
    <span style='background-color:#ffcccc'>eliminaciones</span>, 
    <span style='background-color:#ccffcc'>inserciones</span>. 
    Se puede ocultar texto sin cambios para ver solo diferencias.
    """
)

iface.launch()
