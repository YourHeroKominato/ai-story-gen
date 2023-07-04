from dotenv import load_dotenv
import os

import gradio as gr

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

load_dotenv()
openai_api_key = os.environ.get('OPENAI_API_KEY')

llm = OpenAI(
                openai_api_key=openai_api_key,
                model_name="gpt-3.5-turbo-16k"
            )

def create_ki_sho_ten_ketsu(story_idea, story_style):

    template = """
    role:
    ///
    You are a yon-koma manga artist and gag-manga writer.
    You are working for a client who wants to create a yon-koma manga based on an initial "story idea" and in a specific "story style".
    using the story telling principle of Ki Sho Ten Ketsu and yon-koma manga.
    ///

    task:
    ///
    Take the initial "story idea" and "story style", and create a !fully self-contained! four-panel manga story using a full arc of Ki Sho Ten Ketsu.
    Each Panel of the yon-koma should be comprehensible by the description, and correspond to one of the four parts of Ki Sho Ten Ketsu respectively.
    Make sure to highly customize your response for your client's story idea and supplied story style.
    Make sure to be highly specific and concrete in your descriptions. Each descriptions should describe an event that can be depicted in a single image.
    
    ///

    story idea:
    ///
    {story_idea}
    ///

    story style:
    ///
    {story_style}
    ///

    !output only in the following format!:
    {{
    "kishotenketsu": {{
        "ki": {{
            "title": "...",
            "description": "..."
        }},
        "sho": {{
            "title": "...",
            "description": "..."
        }},
        ...
    }}
    """

    prompt = PromptTemplate(
        input_variables=["story_idea", "story_style"],
        template=template,
    )

    text = prompt.format(
        story_idea = story_idea,
        story_style = story_style
    )

    return llm(text)

demo = gr.Interface(fn=create_ki_sho_ten_ketsu,
                    inputs=[
                        gr.Textbox(lines=2, placeholder="Put your basic story idea here..."),
                        gr.Textbox(lines=2, placeholder="Put a style description here..."),
                        ],
                    outputs="text")

demo.launch()   