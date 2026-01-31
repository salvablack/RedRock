import streamlit as st
from groq import Groq
import time
import os  # ← agrégalo si no lo tienes

# ────────────────────────────────────────────────
# ¡NO pongas la clave aquí nunca más!
# client = Groq(api_key="gsk_...")   ← BORRA esta línea
# ────────────────────────────────────────────────

# Opción recomendada: usa st.secrets (más "streamlit way")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)

# Alternativa (si prefieres entorno variables puras):
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("No se encontró la GROQ_API_KEY en secrets. Configúrala en Streamlit Cloud → Settings → Secrets.")
    st.stop()  # detiene la app para que no siga sin clave

client = Groq(api_key=GROQ_API_KEY)

# ... el resto de tu código queda exactamente igual ...
# ────────────────────────────────────────────────

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Chat RedRock ⚡", layout="wide")
st.title("Chat con RedRock 🚀 (En beta)")

# Modelos válidos ahora (sin Mixtral)
MODEL_OPTIONS = {
    "Llama 3.3 70B Versatile (recomendado)": "llama-3.3-70b-versatile",
    "Llama 3.1 70B": "llama-3.1-70b-versatile",
    "Llama 3.1 8B Instant (ultra rápido)": "llama-3.1-8b-instant",
    "Qwen 3 32B": "qwen/qwen3-32b",
    "GPT OSS 20B": "openai/gpt-oss-20b",
    "GPT OSS 120B": "openai/gpt-oss-120b",
}

selected_model_name = st.sidebar.selectbox("Modelo", list(MODEL_OPTIONS.keys()))
selected_model = MODEL_OPTIONS[selected_model_name]

temperature = st.sidebar.slider("Temperatura (creatividad)", 0.0, 1.5, 0.7, 0.1)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pregunta a RedRock..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    groq_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=selected_model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=2048,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
                time.sleep(0.015)

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error con Groq: {str(e)}")
            st.info("Prueba cambiando de modelo o verifica tu API key/conexión.")

if st.sidebar.button("🗑️ Limpiar conversación"):
    st.session_state.messages = []
    st.rerun()