import gradio as gr
from difflib import SequenceMatcher
import docx
import pdfplumber
import html as html_lib
import re
import os
import tempfile
from datetime import datetime

# ── ODT support (opcional) ──────────────────────────────────────────────────
try:
    from odf import text as odftext, teletype
    from odf.opendocument import load as odf_load
    ODT_SUPPORT = True
except ImportError:
    ODT_SUPPORT = False

# ── Constantes ──────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB    = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

comparison_history: list[dict] = []

# ── Estilos CSS ──────────────────────────────────────────────────────────────
CSS_STYLES = """
    body { font-family: sans-serif; }
    .stats-box {
        display: flex; flex-wrap: wrap; gap: 12px;
        padding: 12px; background: #f8f9fa; border-radius: 8px;
        margin-bottom: 12px; border: 1px solid #dee2e6;
    }
    .stat-item { padding: 4px 12px; border-radius: 4px; font-size: 14px; }
    .stat-item.sim  { background: #e3f2fd; }
    .stat-item.add  { background: #e8f5e9; }
    .stat-item.del-s{ background: #ffebee; }
    .stat-item.mod  { background: #fff8e1; }
    .stat-item.eq   { background: #f3e5f5; }

    .change-nav {
        margin-bottom: 10px; padding: 8px 14px;
        background: #fffde7; border: 1px solid #f9a825;
        border-radius: 6px; font-size: 13px; line-height: 2.2;
    }
    .nav-link {
        display: inline-block; margin: 2px; padding: 2px 9px;
        background: #1976d2; color: white !important;
        border-radius: 3px; text-decoration: none; font-size: 12px;
    }
    .nav-link:hover { background: #0d47a1; }

    .diff-container { overflow-x: auto; }
    .diff-table {
        width: 100%; border-collapse: collapse;
        font-family: 'Courier New', monospace; font-size: 13px;
    }
    .diff-table thead th {
        background: #343a40; color: white;
        padding: 8px 12px; text-align: left;
        position: sticky; top: 0; z-index: 1;
    }
    .diff-table td {
        padding: 3px 8px; vertical-align: top;
        border-bottom: 1px solid #f0f0f0;
        white-space: pre-wrap; word-break: break-word;
    }
    .diff-table td.ln {
        color: #aaa; text-align: right; width: 38px; min-width: 38px;
        user-select: none; background: #fafafa;
        border-right: 1px solid #e0e0e0;
        padding: 3px 6px; font-size: 11px;
    }
    tr.row-deleted  td { background: #fff5f5; }
    tr.row-inserted td { background: #f0fff4; }
    tr.row-modified td { background: #fffff0; }
    tr.row-omitted  td {
        background: #f0f0f0; color: #999;
        text-align: center; font-style: italic; padding: 6px;
    }
    span.del { background: #ffb3b3; border-radius: 2px; padding: 0 2px; }
    span.ins { background: #b3ffb3; border-radius: 2px; padding: 0 2px; }

    .section-title {
        font-size: 16px; font-weight: bold;
        margin: 22px 0 10px; padding: 10px 14px;
        background: #343a40; color: white; border-radius: 6px;
    }
    .or-divider {
        text-align: center; color: #bbb; font-size: 12px;
        margin: 6px 0; letter-spacing: 3px;
    }
"""
CSS_TAG = f"<style>{CSS_STYLES}</style>"


# ══════════════════════════════════════════════════════════════════════════════
#  Resolución de entrada: texto pegado tiene prioridad sobre archivo
# ══════════════════════════════════════════════════════════════════════════════
def resolve_input(file, pasted: str, slot_num: int) -> tuple[str | None, str]:
    """
    Devuelve (texto_crudo, nombre) para un slot.
    Prioridad: texto pegado > archivo subido.
    Devuelve (None, '') si el slot está vacío.
    """
    # ── Texto pegado ──────────────────────────────────────────────────────────
    if pasted and pasted.strip():
        return pasted.strip(), f"Texto {slot_num}"

    # ── Archivo subido ────────────────────────────────────────────────────────
    if not file or not hasattr(file, "name"):
        return None, ""

    try:
        if os.path.getsize(file.name) > MAX_FILE_SIZE_BYTES:
            return (
                f"Error: El archivo supera el límite de {MAX_FILE_SIZE_MB} MB.",
                f"Documento {slot_num}",
            )
    except OSError:
        pass

    try:
        name_lower = file.name.lower()
        if name_lower.endswith(".pdf"):
            with pdfplumber.open(file.name) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)

        elif name_lower.endswith(".docx"):
            doc = docx.Document(file.name)
            text = "\n".join(p.text for p in doc.paragraphs)

        elif name_lower.endswith(".odt"):
            if not ODT_SUPPORT:
                return "Error: instala odfpy con:  pip install odfpy", f"Documento {slot_num}"
            doc = odf_load(file.name)
            text = "\n".join(
                teletype.extractText(p) for p in doc.getElementsByType(odftext.P)
            )

        else:  # TXT / otros
            try:
                file.seek(0)
            except Exception:
                pass
            text = file.read().decode("utf-8", errors="ignore")

        return text, os.path.basename(file.name)

    except Exception as exc:
        return f"Error leyendo el archivo: {exc}", f"Documento {slot_num}"


# ══════════════════════════════════════════════════════════════════════════════
#  Normalización
# ══════════════════════════════════════════════════════════════════════════════
def normalize_text(text: str, ignore_case: bool, ignore_whitespace: bool) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    if ignore_case:
        text = text.lower()
    if ignore_whitespace:
        text = re.sub(r"\s+", " ", text).strip()
    return text


# ══════════════════════════════════════════════════════════════════════════════
#  Granularidad
# ══════════════════════════════════════════════════════════════════════════════
def split_by_granularity(text: str, granularity: str) -> list[str]:
    if granularity == "Oración":
        parts = re.split(r"(?<=[.!?¿¡])\s+", text)
        return [s.strip() for s in parts if s.strip()]
    elif granularity == "Párrafo":
        parts = re.split(r"\n\s*\n", text)
        return [p.strip() for p in parts if p.strip()]
    return text.splitlines()


# ══════════════════════════════════════════════════════════════════════════════
#  Diff por palabra
# ══════════════════════════════════════════════════════════════════════════════
def word_diff(line1: str, line2: str, side: str) -> str:
    w1, w2 = line1.split(), line2.split()
    matcher = SequenceMatcher(None, w1, w2)
    out = ""
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if side == "left":
            chunk = html_lib.escape(" ".join(w1[i1:i2]))
            if tag == "equal":
                out += chunk + " "
            elif tag in ("replace", "delete"):
                out += f"<span class='del'>{chunk}</span> "
        else:
            chunk = html_lib.escape(" ".join(w2[j1:j2]))
            if tag == "equal":
                out += chunk + " "
            elif tag in ("replace", "insert"):
                out += f"<span class='ins'>{chunk}</span> "
    return out.strip()


# ══════════════════════════════════════════════════════════════════════════════
#  Pares de líneas desde opcodes
# ══════════════════════════════════════════════════════════════════════════════
def build_line_pairs(lines1, lines2, opcodes):
    pairs = []
    left_n = right_n = 1
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            for k in range(i2 - i1):
                pairs.append((left_n + k, right_n + k, "equal",
                               lines1[i1 + k], lines2[j1 + k]))
            left_n  += i2 - i1
            right_n += j2 - j1
        elif tag == "replace":
            max_k = max(i2 - i1, j2 - j1)
            for k in range(max_k):
                l1  = lines1[i1 + k] if i1 + k < i2 else ""
                l2  = lines2[j1 + k] if j1 + k < j2 else ""
                ln1 = (left_n  + k) if i1 + k < i2 else None
                ln2 = (right_n + k) if j1 + k < j2 else None
                pairs.append((ln1, ln2, "replace", l1, l2))
            left_n  += i2 - i1
            right_n += j2 - j1
        elif tag == "delete":
            for k in range(i2 - i1):
                pairs.append((left_n + k, None, "delete", lines1[i1 + k], ""))
            left_n += i2 - i1
        elif tag == "insert":
            for k in range(j2 - j1):
                pairs.append((None, right_n + k, "insert", "", lines2[j1 + k]))
            right_n += j2 - j1
    return pairs


# ══════════════════════════════════════════════════════════════════════════════
#  HTML de diff lado a lado
# ══════════════════════════════════════════════════════════════════════════════
def generate_diff_html(
    text1, text2, name1, name2,
    hide_equal, context_lines, granularity,
) -> tuple[str, float]:
    lines1 = split_by_granularity(text1, granularity)
    lines2 = split_by_granularity(text2, granularity)

    matcher = SequenceMatcher(None, lines1, lines2)
    opcodes = list(matcher.get_opcodes())

    added    = sum(j2 - j1 for t, i1, i2, j1, j2 in opcodes if t == "insert")
    deleted  = sum(i2 - i1 for t, i1, i2, j1, j2 in opcodes if t == "delete")
    modified = sum(max(i2-i1, j2-j1) for t, i1, i2, j1, j2 in opcodes if t == "replace")
    equal    = sum(i2 - i1 for t, i1, i2, j1, j2 in opcodes if t == "equal")
    similarity = matcher.ratio() * 100

    stats_html = f"""
    <div class='stats-box'>
        <span class='stat-item sim'>🔍 Similitud: <strong>{similarity:.1f}%</strong></span>
        <span class='stat-item add'>➕ Añadidas: <strong>{added}</strong></span>
        <span class='stat-item del-s'>➖ Eliminadas: <strong>{deleted}</strong></span>
        <span class='stat-item mod'>✏️ Modificadas: <strong>{modified}</strong></span>
        <span class='stat-item eq'>✅ Iguales: <strong>{equal}</strong></span>
    </div>"""

    line_pairs = build_line_pairs(lines1, lines2, opcodes)

    show_set: set[int] = set()
    if hide_equal:
        for idx, (_, _, tag, _, _) in enumerate(line_pairs):
            if tag != "equal":
                for c in range(
                    max(0, idx - context_lines),
                    min(len(line_pairs), idx + context_lines + 1),
                ):
                    show_set.add(c)

    rows = ""
    change_count = 0
    prev_hidden  = False

    for idx, (ln1, ln2, tag, t1, t2) in enumerate(line_pairs):
        if hide_equal and tag == "equal" and idx not in show_set:
            if not prev_hidden:
                rows += (
                    "<tr class='row-omitted'>"
                    "<td colspan='4'>· · · líneas sin cambios omitidas · · ·</td>"
                    "</tr>"
                )
                prev_hidden = True
            continue
        prev_hidden = False

        change_id = row_class = ""

        if tag == "equal":
            lc = html_lib.escape(t1)
            rc = html_lib.escape(t2)
        elif tag == "replace":
            change_count += 1
            change_id, row_class = f"change-{change_count}", "row-modified"
            lc = word_diff(t1, t2, "left")
            rc = word_diff(t1, t2, "right")
        elif tag == "delete":
            change_count += 1
            change_id, row_class = f"change-{change_count}", "row-deleted"
            lc = f"<span class='del'>{html_lib.escape(t1)}</span>"
            rc = ""
        else:  # insert
            change_count += 1
            change_id, row_class = f"change-{change_count}", "row-inserted"
            lc = ""
            rc = f"<span class='ins'>{html_lib.escape(t2)}</span>"

        id_attr = f'id="{change_id}"' if change_id else ""
        rows += (
            f"<tr class='{row_class}' {id_attr}>"
            f"<td class='ln'>{ln1 or ''}</td><td class='code'>{lc}</td>"
            f"<td class='ln'>{ln2 or ''}</td><td class='code'>{rc}</td>"
            "</tr>"
        )

    nav_html = ""
    if change_count:
        links = " ".join(
            f"<a href='#change-{i}' class='nav-link'>{i}</a>"
            for i in range(1, change_count + 1)
        )
        nav_html = f"<div class='change-nav'>🔖 <strong>{change_count} cambio(s):</strong> {links}</div>"

    table_html = f"""
    {stats_html}{nav_html}
    <div class='diff-container'>
    <table class='diff-table'>
        <thead><tr>
            <th class='ln'>#</th><th>📄 {html_lib.escape(name1)}</th>
            <th class='ln'>#</th><th>📄 {html_lib.escape(name2)}</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table></div>"""

    return table_html, similarity


# ══════════════════════════════════════════════════════════════════════════════
#  Historial
# ══════════════════════════════════════════════════════════════════════════════
def format_history_html(history: list[dict]) -> str:
    if not history:
        return "<p style='color:#999;font-style:italic'>Sin comparaciones previas en esta sesión.</p>"
    out = ""
    for i, item in enumerate(reversed(history)):
        num = len(history) - i
        out += (
            f"<div style='margin-bottom:8px;padding:10px;background:#f8f9fa;"
            f"border-radius:6px;border-left:4px solid #1976d2;font-size:13px'>"
            f"<strong>#{num}</strong> · {item['time']}<br>"
            f"📄 {' · '.join(item['docs'])}<br>"
            f"🔍 Similitud promedio: <strong>{item['similarity']:.1f}%</strong>"
            "</div>"
        )
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  Función principal
# ══════════════════════════════════════════════════════════════════════════════
def compare_docs(
    doc1, paste1,
    doc2, paste2,
    doc3, paste3,
    doc4, paste4,
    hide_equal, context_lines,
    ignore_case, ignore_whitespace,
    granularity, comparison_mode,
):
    slots = [
        (doc1, paste1, 1),
        (doc2, paste2, 2),
        (doc3, paste3, 3),
        (doc4, paste4, 4),
    ]
    texts: list[str] = []
    names: list[str] = []

    for file, pasted, num in slots:
        raw, name = resolve_input(file, pasted, num)
        if raw is None:
            continue
        if raw.startswith("Error"):
            return CSS_TAG + f"<p style='color:red'>⚠️ {raw}</p>", "", ""
        texts.append(normalize_text(raw, ignore_case, ignore_whitespace))
        names.append(name)

    if len(texts) < 2:
        return (
            CSS_TAG + "<p style='color:red'>⚠️ Introduce al menos dos entradas válidas para comparar.</p>",
            "", "",
        )

    pairs = (
        [(0, j) for j in range(1, len(texts))]
        if comparison_mode == "Base vs. Todos"
        else ([(0, 1)] if len(texts) == 2 else [(j, (j+1) % len(texts)) for j in range(len(texts))])
    )

    result_body = ""
    sims: list[float] = []

    for a, b in pairs:
        result_body += (
            f"<div class='section-title'>"
            f"📄 {html_lib.escape(names[a])} &nbsp;↔&nbsp; {html_lib.escape(names[b])}"
            "</div>"
        )
        diff_html, sim = generate_diff_html(
            texts[a], texts[b], names[a], names[b],
            hide_equal, int(context_lines), granularity,
        )
        result_body += diff_html
        sims.append(sim)

    avg_sim = sum(sims) / len(sims)
    comparison_history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "docs": names,
        "similarity": avg_sim,
    })

    return CSS_TAG + result_body, format_history_html(comparison_history), result_body


# ══════════════════════════════════════════════════════════════════════════════
#  Exportar HTML
# ══════════════════════════════════════════════════════════════════════════════
def export_html(result_body: str):
    if not result_body:
        return None
    page = (
        "<!DOCTYPE html><html lang='es'><head>"
        "<meta charset='UTF-8'><title>Comparación de Documentos</title>"
        f"<style>{CSS_STYLES}</style></head>"
        "<body style='padding:24px;max-width:1400px;margin:0 auto'>"
        "<h1>📄 Comparación de Documentos</h1>"
        f"<p style='color:#666;font-size:13px'>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>"
        f"{result_body}</body></html>"
    )
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
    tmp.write(page)
    tmp.close()
    return tmp.name


# ══════════════════════════════════════════════════════════════════════════════
#  Helper: construye un slot de entrada (archivo + textarea)
# ══════════════════════════════════════════════════════════════════════════════
def make_input_slot(label: str, required: bool = True):
    suffix = " ✱" if required else " (opcional)"
    with gr.Column():
        gr.Markdown(f"**{label}{suffix}**")
        file_comp = gr.File(
            label="📎 Subir archivo (PDF, DOCX, ODT, TXT)",
            file_types=[".pdf", ".docx", ".odt", ".txt"],
        )
        gr.HTML("<div class='or-divider'>── o ──</div>")
        text_comp = gr.Textbox(
            label="📋 Pegar texto directamente",
            placeholder="Pega aquí el contenido del documento…",
            lines=6,
            max_lines=20,
        )
    return file_comp, text_comp


# ══════════════════════════════════════════════════════════════════════════════
#  Interfaz Gradio
# ══════════════════════════════════════════════════════════════════════════════
with gr.Blocks(title="Comparador Visual de Documentos", theme=gr.themes.Soft()) as iface:

    gr.Markdown("""
    # 📄 Comparador Visual de Documentos
    Soporta **PDF · DOCX · ODT · TXT** y **texto pegado** — hasta 4 entradas con vista lado a lado.
    &nbsp;&nbsp;
    <span style='background:#ffb3b3;padding:2px 8px;border-radius:3px'>Eliminaciones</span>
    &nbsp;
    <span style='background:#b3ffb3;padding:2px 8px;border-radius:3px'>Inserciones</span>
    <br><small style='color:#888'>En cada slot puedes subir un archivo <em>o</em> pegar texto directamente. Si usas ambos, el texto pegado tiene prioridad.</small>
    """)

    with gr.Row():
        doc1, paste1 = make_input_slot("Documento 1", required=True)
        doc2, paste2 = make_input_slot("Documento 2", required=True)

    with gr.Row():
        doc3, paste3 = make_input_slot("Documento 3", required=False)
        doc4, paste4 = make_input_slot("Documento 4", required=False)

    with gr.Row():
        with gr.Column():
            granularity = gr.Radio(
                ["Línea", "Oración", "Párrafo"], value="Línea",
                label="🔬 Granularidad de comparación",
            )
            comparison_mode = gr.Radio(
                ["Base vs. Todos", "Comparación circular"],
                value="Base vs. Todos",
                label="🔄 Modo de comparación",
                info="Base vs. Todos: entrada 1 contra cada una. Circular: 1↔2, 2↔3...",
            )
        with gr.Column():
            hide_equal        = gr.Checkbox(label="Ocultar líneas sin cambios", value=False)
            ignore_case       = gr.Checkbox(label="Ignorar mayúsculas/minúsculas", value=False)
            ignore_whitespace = gr.Checkbox(label="Ignorar espacios en blanco", value=False)
            context_lines     = gr.Slider(
                0, 10, value=3, step=1,
                label="Líneas de contexto alrededor de cada cambio",
            )

    compare_btn  = gr.Button("🔍 Comparar", variant="primary", size="lg")
    result_state = gr.State("")

    with gr.Tabs():
        with gr.TabItem("📊 Resultado"):
            result_output = gr.HTML()

        with gr.TabItem("💾 Exportar"):
            gr.Markdown("Descarga el resultado como página HTML autocontenida.")
            export_btn  = gr.Button("💾 Generar archivo HTML", variant="secondary")
            export_file = gr.File(label="Archivo generado")

        with gr.TabItem("🕒 Historial de sesión"):
            history_output = gr.HTML(
                "<p style='color:#999;font-style:italic'>Sin comparaciones previas.</p>"
            )

    compare_btn.click(
        fn=compare_docs,
        inputs=[
            doc1, paste1, doc2, paste2,
            doc3, paste3, doc4, paste4,
            hide_equal, context_lines,
            ignore_case, ignore_whitespace,
            granularity, comparison_mode,
        ],
        outputs=[result_output, history_output, result_state],
    )

    export_btn.click(
        fn=export_html,
        inputs=[result_state],
        outputs=[export_file],
    )

if __name__ == "__main__":
    iface.launch()
