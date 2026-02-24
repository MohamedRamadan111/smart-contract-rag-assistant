import gradio as gr
import requests
import json

API = "http://localhost:8000"


theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill="#f8fafc",
    block_background_fill="#ffffff",
    button_primary_background_fill="linear-gradient(90deg, #4f46e5 0%, #6366f1 100%)",
    button_primary_text_color="#ffffff"
)

custom_css = """
.header { text-align: center; margin-bottom: 20px; }
.header h1 { 
    font-size: 3rem; 
    background: linear-gradient(to right, #4f46e5, #ec4899); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
}
.chat-window { height: 600px !important; overflow-y: auto; border: 1px solid #e2e8f0; }
"""

def upload_file(file):
    if file is None: return " Select a file."
    try:
        r = requests.post(f"{API}/upload", params={"file_path": file.name})
        if r.status_code == 200:
            data = r.json()
            if "error" in data: return f"❌ Error: {data['error']}"
            return f"✅ Indexed {data['chunks_indexed']} chunks."
        return f"❌ Server Error: {r.text}"
    except Exception as e:
        return f"❌ Connection Error: {e}"

def ask_question_stream(history):
    if not history: return history
    
   # Preparing the question and history for the API
    last_msg = history[-1]
    question = last_msg["content"] if isinstance(last_msg["content"], str) else str(last_msg["content"])
    
    # Converting the History into a format that the API understands
    api_history = []
    for msg in history[:-1]:
        api_history.append({"role": msg["role"], "content": str(msg["content"])})

    try:
        history.append({"role": "assistant", "content": ""})
        
        response = requests.post(
            f"{API}/ask_stream",
            json={"question": question, "history": api_history},
            stream=True
        )

        if response.status_code != 200:
            history[-1]["content"] = f"⚠️ Server Error: {response.text}"
            yield history
            return

        answer_text = ""
        sources_data = []
        first_line = True

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if first_line:
                    try:
                        sources_data = json.loads(decoded_line).get("sources", [])
                    except: pass
                    first_line = False
                else:
                    answer_text += decoded_line
                    history[-1]["content"] = answer_text
                    yield history

        if sources_data:
            refs = "\n\n<div style='font-size:0.8em; color:gray; border-top:1px solid #eee; padding-top:5px;'>📚 Sources:<ul>"
            for s in sources_data:
                if s['score'] > 2.5:  # Only highly relevant sources
                    refs += f"<li>Page {s['page']}</li>"
            refs += "</ul></div>"
            history[-1]["content"] = answer_text + refs
            yield history

    except Exception as e:
        history[-1]["content"] = f"❌ Error: {e}"
        yield history

def add_message(history, message):
    if message.strip():
        history.append({"role": "user", "content": message})
    return history, ""

#############################################################################
with gr.Blocks(title="Contract AI") as demo:
    with gr.Row():
        with gr.Column(elem_classes="header"):
            gr.HTML("<h1>Smart Contract AI</h1><p>Upload & Chat with Context Memory</p>")

    with gr.Row():
        with gr.Column(scale=1):
            upload_btn = gr.UploadButton("📂 Upload Contract", file_types=[".pdf", ".docx"])
            status = gr.Markdown()
        
        with gr.Column(scale=4):
            
            chatbot = gr.Chatbot(elem_classes="chat-window", show_label=False)
            msg = gr.Textbox(placeholder="Ask a question...", show_label=False)
            btn = gr.Button("Send", variant="primary")

    upload_btn.upload(upload_file, upload_btn, status)
    
    gr.on(
        triggers=[msg.submit, btn.click],
        fn=add_message,
        inputs=[chatbot, msg],
        outputs=[chatbot, msg]
    ).then(
        ask_question_stream, chatbot, chatbot
    )

if __name__ == "__main__":
    
    demo.queue().launch(allowed_paths=["."], theme=theme, css=custom_css)