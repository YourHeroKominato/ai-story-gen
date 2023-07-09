import json

import gradio as gr
import requests
from PIL import Image

import openai

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate


def create_storyboard(template, story_idea, story_style, art_style):

    prompt = PromptTemplate(
        input_variables=["story_idea", "story_style","art_style"],
        template=template,
    )

    text = prompt.format(
        story_idea = story_idea,
        story_style = story_style,
        art_style = art_style,
    )

    storyboard = llm(text)

    return storyboard

def generate_image(prompt):
    img_response = openai.Image.create(prompt = prompt, n=1, size="512x512")
    img_url = img_response['data'][0]['url']
    img = Image.open(requests.get(img_url, stream=True).raw)
    return img

def parse_storyboard(storyboard):
    storyboard = json.loads(storyboard)
    
    for panel in storyboard['storyboard']['panels']:
            if panel['type'] == 'ki':
                ki = panel['description']
                ki_image_prompt = panel['image_generation_prompt']
                ki_dialogue = panel['dialogue']
            elif panel['type'] == 'sho':
                sho = panel['description']
                sho_image_prompt = panel['image_generation_prompt']
                sho_dialogue = panel['dialogue']
            elif panel['type'] == 'ten':
                ten = panel['description']
                ten_image_prompt = panel['image_generation_prompt']
                ten_dialogue = panel['dialogue']
            elif panel['type'] == 'ketsu':
                ketsu = panel['description']
                ketsu_image_prompt = panel['image_generation_prompt']
                ketsu_dialogue = panel['dialogue']
                
    return ki, sho, ten, ketsu, ki_dialogue, sho_dialogue, ten_dialogue, ketsu_dialogue, ki_image_prompt, sho_image_prompt, ten_image_prompt, ketsu_image_prompt

def generate_panels(storyboard):
    storyboard = json.loads(storyboard)
    
    for panel in storyboard['storyboard']['panels']:
            if panel['type'] == 'ki':
                ki_image = generate_image(panel['image_generation_prompt'])
            elif panel['type'] == 'sho':
                sho_image = generate_image(panel['image_generation_prompt'])
            elif panel['type'] == 'ten':
                ten_image = generate_image(panel['image_generation_prompt'])
            elif panel['type'] == 'ketsu':
                ketsu_image = generate_image(panel['image_generation_prompt'])
                
    return ki_image, sho_image, ten_image, ketsu_image

def create_kishotenketsu(template, story_idea, story_style, art_style):
    storyboard = create_storyboard(template, story_idea, story_style, art_style)
    ki, sho, ten, ketsu, ki_dialogue, sho_dialogue, ten_dialogue, ketsu_dialogue, ki_image_prompt, sho_image_prompt, ten_image_prompt, ketsu_image_prompt = parse_storyboard(storyboard)
    ki_image, sho_image, ten_image, ketsu_image = generate_panels(storyboard)

    return storyboard, ki, sho, ten, ketsu, ki_dialogue, sho_dialogue, ten_dialogue, ketsu_dialogue, ki_image_prompt, sho_image_prompt, ten_image_prompt, ketsu_image_prompt, ki_image, sho_image, ten_image, ketsu_image


default_template = """
role:
///
You are a screenwriter, storyboard artist, and mangaka, known for creating self-contained yon-koma manga strips based on the Ki Sho Ten Ketsu narrative structure.
///

task:
///
Create a finished script for a four-panel manga where each panel correspond to an element of Ki Sho Ten Ketsu:
KI: Show the environment, the characters are in. The reader should think: "Oh, so this is how a story begins."
SHO: Something develops in that environment, building anticipation. The reader should think: "So this is how, the story will go on…"
TEN: The surprising twist: look at the event from a completely different point of view. The reader should think "Oh the Climax Whaaat? Oh my what’s gonna happen?"
KETSU: Bringing what’s expected from SHO, with unexpected TEN, leading to a unified conclusion. The reader should think: "Aha! So that’s how it is. Haha that was fun! This four panel manga is a classic four part construction executed brilliantly!"

The narrative arc should be self-contained within the four panels, with no cliffhangers or unresolved plot points.
Optimize in particular for building anticipation with the TEN and then resolving the momentum with the KETSU.
Be as concrete and specific as possible, avoiding vague, abstract or extravagant language.

Use the below given "story idea", "story style" & "art style" as a basis for creating the script.
///

story idea:
///
{story_idea}
///

story style:
///
{story_style}
///

art style:
///
{art_style}
///

response format:
///

make sure to:
- use at least 240 characters for each "description", focussing on a single shot, image or action
- the "image_generation_prompt" should follow image-generation prompt best practices, in the format of "subject(s), setting, action, art form, additional quality boosters (artstation, 4k, movie still, manga drawing etc.)", and consistently include the "art style" (and "story style")
- the "dialogue" is optional and should at most be 2 replies and less than 30 words

!!! ABOVE ALL, MAKE ABSOLUTELY SURE TO FORMAT YOUR RESPONSE EXACTLY LIKE FOLLOWING JSON-SAMPLE, replace the "..."s, and ONLY RETURN THE JSON !!!
json-sample:
{{
"storyboard": {{
    "title": "...",
    "200_words_step_by_step_thinking_for_designing_your_storyboard": "...",
    "200_words_step_by_step_thinking_for_effectively_applying_ki_sho_ten_ketsu": "...",
    "panels": [
        {{
            "id": 1,
            "type": "ki",
            "image_generation_prompt": "...",
            "description": "...",
            "dialogue": "..."
        }},
        {{
            "id": 2,
            "type": "sho",
            "image_generation_prompt": "...",
            "description": "...",
            "dialogue": "..."
        }},
        {{
            "id": 3,
            "type": "ten",
            "image_generation_prompt": "...",
            "description": "...",
            "dialogue": "..."
        }},
        {{
            "id": 4,
            "type": "ketsu",
            "image_generation_prompt": "...",
            "description": "...",
            "dialogue": "..."
        }}
    ]
}}
///
"""

def auth(openai_api_key, model_name):
    llm = OpenAI(openai_api_key=openai_api_key, model_name=model_name)
    return llm

with gr.Blocks() as demo:

    with gr.Row():
        ############## CONFIG
        gr.Markdown(value = "# Generate Yon-Koma Manga with 起承転結 (Kishotenketsu) Structure")
        openai_api_key = gr.Textbox(
            label="Paste your OpenAI API key (sk-...) here",
            lines=1,
            type="password",
            interactive=True,
            placeholder="sk-...",
            value="   "
        )
        model_name = gr.Radio(["gpt-4", "gpt-3.5-turbo-16k"], value="gpt-4", label="model", interactive=True)
        
        llm = OpenAI(openai_api_key=openai_api_key.value, model_name=model_name.value)
        
        openai_api_key.change(auth, [openai_api_key, model_name])



    with gr.Row():
        ############## INPUT
        with gr.Column(scale=1, variant='panel'):
            with gr.Row():
                story_idea = gr.Textbox(label = "Story Idea", lines=5, placeholder="Put your basic story idea here...", scale=2)
                
                story_style = gr.Textbox(label = "Story Style", lines=2, placeholder="Put a description of the desired writing-style here...", scale=1)
                art_style = gr.Textbox(label = "Art Style", lines=2, placeholder="Put a description of the art-style here...", scale=1)
            with gr.Accordion("show examples", open=True):
                gr.Examples(
                    [
                        ["A salaryman finds a mysterious object in a JR train station.", "80s joke manga", "Machiko Hasegawa's Sazae-san"],
                        ["A fox chases after a rabbit, until an unexpected hindrance occurs.", "Aesop's fable","Der Struwwelpeter"],
                        ["A Shibuya barkeeper gets visited by a dangerous guest", "Raymond Chandler's hard boiled detective story","Casablanca (1942)"],
                    ],
                    [story_idea, story_style, art_style],
                )

            btn_kishotenketsu = gr.Button("Generate Yon-Koma", variant="primary", scale=0)
            btn_storyboard = gr.Button("1. Generate Storyboard", variant="secondary", scale=0)
            btn_parse_storyboard = gr.Button("2. Parse Storyboard into the UI", variant="secondary", scale=0)
            btn_generate_panels = gr.Button("3. Generate Images", variant="secondary", scale=0)

            with gr.Accordion("edit the Prompt Template for Generating the Storyboard", open=False):
                template = gr.Textbox(
                    label="Prompt Template",
                    info="""
                        Shows the prompt which is send to the LLM.
                        values surrounded with "{" & "}" are variables that will be filled in by user-input from the boxes above.
                        """,
                    lines=50,
                    value=default_template,
                    show_label=False
                )



        ############## OUTPUT
        with gr.Column(scale=2):
            with gr.Accordion("Show Storyboard", open=False):
                storyboard = gr.Textbox(label="Storyboard", lines=30, interactive=True, show_label=False)
            
            with gr.Row():
                with gr.Column(scale=1):
                    ki = gr.Textbox(label="Ki", lines=5, interactive=True)
                with gr.Column(scale=2):
                    with gr.Row():
                        ki_image = gr.Image(label="Ki Image", scale=2)
                        ki_dialogue = gr.Textbox(label="Dialogue", lines = 2, interactive=True, scale=1)
                    with gr.Accordion("show image prompt", open=False):
                        ki_image_prompt = gr.Textbox(label="Ki Image Prompt", lines=2, interactive=True, show_label=False)
                    gr.Button("Regenerate Image", variant="secondary").click(fn=generate_image, inputs=ki_image_prompt, outputs=ki_image)
            with gr.Row():
                with gr.Column(scale=1):
                    sho = gr.Textbox(label="sho", lines=5, interactive=True)
                with gr.Column(scale=2):
                    with gr.Row():
                        sho_image = gr.Image(label="sho Image", scale=2)
                        sho_dialogue = gr.Textbox(label="Dialogue", lines = 2, interactive=True, scale=1)
                    with gr.Accordion("show image prompt", open=False):
                        sho_image_prompt = gr.Textbox(label="sho Image Prompt", lines=2, interactive=True, show_label=False)
                    gr.Button("Regenerate Image", variant="secondary").click(fn=generate_image, inputs=sho_image_prompt, outputs=sho_image)
            with gr.Row():
                with gr.Column(scale=1):
                    ten = gr.Textbox(label="ten", lines=5, interactive=True)
                with gr.Column(scale=2):
                    with gr.Row():
                        ten_image = gr.Image(label="ten Image", scale=2)
                        ten_dialogue = gr.Textbox(label="Dialogue", lines = 2, interactive=True, scale=1)
                    with gr.Accordion("show image prompt", open=False):
                        ten_image_prompt = gr.Textbox(label="ten Image Prompt", lines=2, interactive=True, show_label=False)
                    gr.Button("Regenerate Image", variant="secondary").click(fn=generate_image, inputs=ten_image_prompt, outputs=ten_image)
            with gr.Row():
                with gr.Column(scale=1):
                    ketsu = gr.Textbox(label="ketsu", lines=5, interactive=True)
                with gr.Column(scale=2):
                    with gr.Row():
                        ketsu_image = gr.Image(label="ketsu Image", scale=2)
                        ketsu_dialogue = gr.Textbox(label="Dialogue", lines = 2, interactive=True, scale=1)
                    with gr.Accordion("show image prompt", open=False):
                        ketsu_image_prompt = gr.Textbox(label="ketsu Image Prompt", lines=2, interactive=True, show_label=False)
                    gr.Button("Regenerate Image", variant="secondary").click(fn=generate_image, inputs=ketsu_image_prompt, outputs=ketsu_image)

            btn_kishotenketsu.click(fn=create_kishotenketsu, inputs=[template, story_idea, story_style, art_style], outputs=[storyboard, ki, sho, ten, ketsu, ki_dialogue, sho_dialogue, ten_dialogue, ketsu_dialogue, ki_image_prompt, sho_image_prompt, ten_image_prompt, ketsu_image_prompt, ki_image, sho_image, ten_image, ketsu_image])

            btn_storyboard.click(fn=create_storyboard, inputs=[template, story_idea, story_style, art_style], outputs=[storyboard])
            btn_parse_storyboard.click(fn=parse_storyboard, inputs=[storyboard], outputs=[ki, sho, ten, ketsu, ki_dialogue, sho_dialogue, ten_dialogue, ketsu_dialogue, ki_image_prompt, sho_image_prompt, ten_image_prompt, ketsu_image_prompt])
            btn_generate_panels.click(fn=generate_panels, inputs=[storyboard], outputs=[ki_image, sho_image, ten_image, ketsu_image])



demo.launch()