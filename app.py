import gradio as gr
from difflib import SequenceMatcher
import docx
from PyPDF2 import PdfReader
import html

def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file.name)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif file.name.endswith(".docx"):
        doc = docx.Document(file.name)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return file.read().decode("utf-8")

def highlight_changes_colors(text1, text2):
    html_diff = ""
    s = SequenceMatcher(None, text1.splitlines(), text2.splitlines())
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "equal":
            for line in text1.splitlines()[i1:i2]:
                html_diff += html.escape(line) + "<br>"
        elif tag in ["replace", "delete", "insert"]:
            for line in text1.splitlines()[i1:i2]:
                html_diff += f"<span style='color:red'>{html.escape(line)}</span><br>"
            for line in text2.splitlines()[j1:j2]:
                html_diff += f"<span style='color:green'>{html.escape(line)}</span><br>"
    return html_diff

def compare_docs_colors(doc1, doc2, doc3=None):
    text1 = extract_text(doc1)
    text2 = extract_text(doc2)
    text3 = extract_text(doc3) if doc3 else None
    
    diffs_html = highlight_changes_colors(text1, text2)
    
    if text3:
        diffs_html += "<br>--- Comparación con Documento 3 ---<br>"
        diffs_html += highlight_changes_colors(text1, text3)
    
    return diffs_html

iface = gr.Interface(
    fn=compare_docs_colors,
    inputs=[
        gr.File(label="Documento 1 (PDF, DOCX, TXT)"),
        gr.File(label="Documento 2 (PDF, DOCX, TXT)"),
        gr.File(label="Documento 3 (Opcional, PDF, DOCX, TXT)")
    ],
    outputs=[
        gr.HTML(label="Diferencias resaltadas con colores")
    ],
    title="Comparador de Documentos con Colores",
    description="Se muestran los documentos comparados. Se utilizan colores para resaltar las diferencias entre ellos."
)

iface.launch()
