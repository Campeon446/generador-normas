import streamlit as st
import os
from google import genai
from audio_recorder_streamlit import audio_recorder
from docx import Document
import io

st.set_page_config(page_title="Generador de Normas y Procedimientos Oficiales", layout="wide")

# ==========================================
# SISTEMA DE AUTENTICACIÓN (LOGIN)
# ==========================================
def verificar_password():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if st.session_state["autenticado"]:
        return True

    st.title("🔒 Acceso Restringido - Generador de Normas")
    st.markdown("Este sistema maneja información confidencial. Por favor, ingrese la contraseña de acceso.")
    
    with st.form("login_form"):
        password_ingresada = st.text_input("Contraseña de Acceso", type="password")
        submit_login = st.form_submit_button("Ingresar")
        
        if submit_login:
            CONTRASENA_VALIDA = "Admin2026*" 
            if password_ingresada == CONTRASENA_VALIDA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Acceso denegado.")
    return False

if not verificar_password():
    st.stop()

# ==========================================
# FUNCIÓN AUXILIAR PARA CREAR ARCHIVO WORD
# ==========================================
def crear_documento_word(texto_norma):
    doc = Document()
    doc.add_heading("NORMA Y PROCEDIMIENTO OFICIAL", level=0)
    
    for linea in texto_norma.split("\n"):
        linea_limpia = linea.strip()
        if linea_limpia.startswith("# "):
            doc.add_heading(linea_limpia.replace("# ", ""), level=1)
        elif linea_limpia.startswith("## "):
            doc.add_heading(linea_limpia.replace("## ", ""), level=2)
        elif linea_limpia.startswith("### "):
            doc.add_heading(linea_limpia.replace("### ", ""), level=3)
        elif linea_limpia.startswith("- ") or linea_limpia.startswith("* "):
            doc.add_paragraph(linea_limpia.replace("- ", "").replace("* ", ""), style='List Bullet')
        elif linea_limpia:
            doc.add_paragraph(linea_limpia)
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==========================================
# APLICACIÓN PRINCIPAL
# ==========================================
st.title("🏛️ Generador de Normas y Procedimientos")
st.markdown("Describa el proceso mediante texto o voz. La IA generará la norma oficial y podrás descargarla directamente en Word.")

with st.sidebar:
    st.header("Seguridad y Configuración")
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()
        
    st.divider()
    st.header("Configuración de IA")
    st.success("✅ Conexión con Inteligencia Artificial activada de forma segura.")
    api_key_input = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# --- FORMULARIO DINÁMICO ---
st.subheader("1. Datos Generales de la Norma")
c1, c2 = st.columns(2)
with c1:
    titulo_norma = st.text_input("Título de la Norma / Procedimiento", placeholder="Ej: NORMA PARA EL OTORGAMIENTO DE CRÉDITOS...", key="k_titulo")
    area_emisora = st.text_input("Área Emisora", placeholder="Ej: Gerencia Económico Financiera", key="k_area")
with c2:
    aprobacion_ref = st.text_input("Referencia de Aprobación", placeholder="Ej: Res (D) N° XXXXX", key="k_ref")
    edicion_num = st.text_input("Edición / Versión", value="1", key="k_edicion")

st.subheader("2. Método de Entrada de Información")
tipo_entrada = st.radio("¿Cómo desea ingresar los detalles del procedimiento?", ["Escribir texto", "Grabar / Subir Audio"], key="k_tipo")

descripcion_libre = ""
audio_bytes = None
mime_type = None

if tipo_entrada == "Escribir texto":
    descripcion_libre = st.text_area(
        "Describa los lineamientos, etapas, plazos o el proceso a normalizar:",
        height=150,
        placeholder="Ej: Describa las reglas para el otorgamiento de créditos...",
        key="k_desc"
    )
else:
    st.markdown("🔊 **Opción A: Grabar ahora en la PC** (Si la red lo permite, presione el ícono de micrófono)")
    audio_grabado = audio_recorder(text="Presionar para grabar", recording_color="#e80000", neutral_color="#6aa36f", icon_size="2x")
    
    st.markdown("📂 **Opción B: Subir un archivo de voz** (Recomendado - Sube audios de WhatsApp, celular o grabadora)")
    audio_subido = st.file_uploader("Suba un archivo de audio (.mp3, .wav, .m4a)", type=["wav", "mp3", "m4a", "ogg"])
    
    if audio_grabado:
        audio_bytes = audio_grabado
        mime_type = "audio/wav"
        st.success("¡Audio grabado en vivo correctamente!")
    elif audio_subido:
        audio_bytes = audio_subido.read()
        mime_type = audio_subido.type
        st.success("¡Archivo de audio cargado correctamente!")

# Botón dinámico de procesamiento
submitted = st.button("📜 Generar Norma Oficial y Diagrama")

if submitted:
    if not titulo_norma:
        st.error("Por favor, ingrese el Título de la Norma.")
    elif tipo_entrada == "Escribir texto" and not descripcion_libre:
        st.error("Por favor, ingrese la descripción escrita del proceso.")
    elif tipo_entrada == "Grabar / Subir Audio" and not audio_bytes:
        st.error("Por favor, grabe o suba un archivo de audio antes de enviar la solicitud.")
    elif not api_key_input:
        st.error("Error de configuración: No se encontró la API Key en los secretos del sistema.")
    else:
        with st.spinner("Procesando información y generando la norma oficial..."):
            try:
                client = genai.Client(api_key=api_key_input)
                
                if tipo_entrada == "Grabar / Subir Audio":
                    contenido_prompt = [
                        {
                            "mime_type": mime_type,
                            "data": audio_bytes
                        },
                        f"Escucha este audio que describe un procedimiento. Redacta la norma titulada '{titulo_norma}' del área '{area_emisora}'."
                    ]
                else:
                    contenido_prompt = f"Toma la siguiente descripción operativa escrita:\n{descripcion_libre}"

                prompt_sistema = f"""
                Eres un analista experto en normalización de procesos corporativos e institucionales (estilo ANCAP / administración pública).
                Debes redactar un documento formal basándote en:
                - Título: {titulo_norma}
                - Área Emisora: {area_emisora}
                - Referencia de Aprobación: {aprobacion_ref}
                - Edición: {edicion_num}
                
                El documento DEBE estructurarse estrictamente con el siguiente formato y orden jerárquico:
                1. Encabezado de Control
                2. Estructura obligatoria por secciones numéricas:
                   - 1. OBJETIVO
                   - 2. ALCANCE
                   - 3. DOCUMENTOS DE REFERENCIA
                   - 4. GLOSARIO
                   - 5. ÁMBITO DE APLICACIÓN
                   - 6. DESCRIPCIÓN (desarrollada de forma decimal estricta: 6.1, 6.1.1, i, ii, 6.2, etc.).
                
                3. Adicionalmente, incluye al final un diagrama de flujo en sintaxis **Mermaid.js** (`flowchart TD`) con la simbología técnica correcta (óvalos inicio/fin, rectángulos actividades, rombos decisiones de Sí/No).
                
                Separa la salida en dos bloques exactos:
                --- NORMA ---
                (Aquí redacta todo el texto del documento en Markdown limpio).
                --- MERMAID ---
                (Aquí coloca únicamente el código puro para Mermaid empezando con flowchart TD).
                """
                
                if tipo_entrada == "Grabar / Subir Audio":
                    contents_to_send = [prompt_sistema, contenido_prompt[0], contenido_prompt[1]]
                else:
                    contents_to_send = [prompt_sistema + "\n\n" + contenido_prompt]

                response = client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=contents_to_send,
                )
                
                texto_respuesta = response.text
                
                if "--- NORMA ---" in texto_respuesta and "--- MERMAID ---" in texto_respuesta:
                    partes = texto_respuesta.split("--- MERMAID ---")
                    norma_generada = partes[0].replace("--- NORMA ---", "").strip()
                    mermaid_generado = partes[1].replace("```mermaid", "").replace("```", "").strip()
                else:
                    norma_generada = texto_respuesta
                    mermaid_generado = "flowchart TD\n    Start([Inicio]) --> P1[Proceso Principal] --> End([Fin])"

                st.success("¡Norma oficial generada con éxito!")
                
                st.session_state["norma_generada"] = norma_generada
                st.session_state["mermaid_generado"] = mermaid_generado
                st.session_state["titulo_norma"] = titulo_norma

            except Exception as e:
                st.error(f"Ocurrió un error al procesar la solicitud: {e}")

# ==========================================
# MOSTRAR RESULTADOS
# ==========================================
if "norma_generada" in st.session_state:
    st.divider()
    st.header("📄 Documento Oficial de la Norma")
    st.markdown(st.session_state["norma_generada"])
    
    archivo_word = crear_documento_word(st.session_state["norma_generada"])
    nombre_archivo = f"{st.session_state['titulo_norma'].replace(' ', '_')}.docx"
    
    st.download_button(
        label="📥 Descargar Documento en formato Word (.docx)",
        data=archivo_word,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    st.divider()
    st.header("📊 Diagrama de Flujo del Procedimiento")
    st.markdown("Representación gráfica basada en la normativa generada:")
    st.markdown(f"```mermaid\n{st.session_state['mermaid_generado']}\n```")
    
    # --- NUEVO BOTÓN DE REINICIO QUE VACÍA TODO ---
    st.divider()
    if st.button("🔄 Comenzar Nuevo Procedimiento"):
        # 1. Borramos los documentos y diagramas generados
        for key in ["norma_generada", "mermaid_generado", "titulo_norma"]:
            if key in st.session_state:
                del st.session_state[key]
        
        # 2. Forzamos que las cajas de texto queden totalmente en blanco
        st.session_state["k_titulo"] = ""
        st.session_state["k_area"] = ""
        st.session_state["k_ref"] = ""
        st.session_state["k_edicion"] = "1"
        st.session_state["k_desc"] = ""
        
        st.rerun()
