import gradio as gr
from agent import chat_with_ai



def agent_ui(message, history):
    try:
        reply = chat_with_ai(message)
        return reply
    except Exception as e:
        return f"Error: {str(e)}"

with gr.Blocks(theme=gr.Theme.from_hub("shivalikasingh/calm_seafoam")) as demo:
    
    gr.Markdown("<h1 style='text-align: center;'> AI Assessment</h1>")
    
    gr.ChatInterface(
        fn=agent_ui,
        examples=[
            "Hello",
            "describe my products dataset use tools",
            "What is the name and price of our most expensive product?",
            "What's the current time?",
            "Describe tables."
            
        ]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)