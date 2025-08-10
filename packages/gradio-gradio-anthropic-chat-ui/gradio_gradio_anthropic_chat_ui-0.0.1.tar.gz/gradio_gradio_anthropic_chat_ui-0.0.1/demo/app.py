
import gradio as gr
from gradio_gradio_anthropic_chat_ui import gradio_anthropic_chat_ui


example = gradio_anthropic_chat_ui().example_value()

demo = gr.Interface(
    lambda x:x,
    gradio_anthropic_chat_ui(),  # interactive version of your component
    gradio_anthropic_chat_ui(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
