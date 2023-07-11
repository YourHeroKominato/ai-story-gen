import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

story_idea = "The femal protagonist starts her own computer processor company, nvidia, with a dream to revolutionize the industry."
story_style = "Suspense"
art_style = "comic"

prompt = '''
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

Now, return four panel manga in Json format.
'''

# create a chat completion
chat_completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613", 
    messages=[
        {"role": "user", "content": prompt}
        ],
    functions= [
        {
            "name": "return_fourPanelManga",
            "description": "return four panel manga",
            "parameters": {
                "type": "object",
                "properties": {
                    "storyboard": {
                    "title": "...",
                    "200_words_step_by_step_thinking_for_designing_your_storyboard": "...",
                    "200_words_step_by_step_thinking_for_effectively_applying_ki_sho_ten_ketsu": "...",
                    "panels": [
                        {
                            "id": 1,
                            "type": "ki",
                            "image_generation_prompt": "...",
                            "description": "...",
                            "dialogue": "..."
                        },
                        {
                            "id": 2,
                            "type": "sho",
                            "image_generation_prompt": "...",
                            "description": "...",
                            "dialogue": "..."
                        },
                        {
                            "id": 3,
                            "type": "ten",
                            "image_generation_prompt": "...",
                            "description": "...",
                            "dialogue": "..."
                        },
                        {
                            "id": 4,
                            "type": "ketsu",
                            "image_generation_prompt": "...",
                            "description": "...",
                            "dialogue": "..."
                        }
                        ]
                    }
                }   
            }
        }
    ]
)

# Extract the function call from the model's response
function_call = chat_completion["choices"][0]["message"]["function_call"]
print(json.loads(function_call["arguments"]))