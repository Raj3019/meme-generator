"""
AI utility functions using Groq for text and Stability AI for images.
Optimized prompts for generating actually funny, modern memes.
"""

import json
import requests
from io import BytesIO
from PIL import Image
from groq import Groq


def generate_caption(topic: str, style: str, groq_api_key: str) -> dict:
    """
    Generate a funny meme caption using Groq's LLM.
    Strongly influenced by modern internet culture and specific humor styles.
    """
    client = Groq(api_key=groq_api_key)
    
    # FORBIDDEN TROPES: These make memes unfunny
    FORBIDDEN = [
        "Said no one ever",
        "Keep Calm and...",
        "Be like [name]",
        "One does not simply",
        "The face you make when",
        "That awkward moment",
        "Am I a joke to you?",
        "Expectation vs Reality"
    ]

    style_prompts = {
        "sarcastic": f"""Create a SARCASTIC meme about "{topic}".
Avoid 2012-era clichés. Use modern, dry, or biting sarcasm.
Pattern: Mock the 'perfect' version of {topic} with a painful reality.
Example: "I love how [topic] allows me to maintain my dignity and definitely doesn't make me look like a crying mess" """,
        
        "relatable": f"""Create a RELATABLE meme about "{topic}".
Focus on the hyperspecific, weird thoughts people have about {topic}.
Do NOT use 'When you...' generic openers.
Example: "Calculated my finances and if I stop eating and breathing by Tuesday, I can afford [topic]" """,
        
        "absurd": f"""Create an ABSURD/BRAINROT meme about "{topic}".
Use surrealism, non-sequiturs, and modern 'brain rot' lingo if it fits.
The humor comes from the sheer confusion and scale of the topic.
Keywords: skibidi, aura, fanum tax, 1000 yard stare, existential crisis.
Example: "The [topic] demon watching me eat a single grape at 4am for sustenance" """,
        
        "wholesome": f"""Create a WHOLESOME meme about "{topic}".
Subvert the 'struggle' of {topic} with an unexpectedly kind or cozy twist.
Example: "[Topic] might be hard but my dog thinks I'm a billionaire and that's enough for today" """,
        
        "dark": f"""Create a DARK HUMOR meme about "{topic}".
Existential dread, self-deprecating nihilism. 
Pattern: The topic is a minor inconvenience that you treat as a life-ending prophecy.
Example: "Added [topic] to the list of reasons why I'm moving to a cave in the woods and starting a new life as a moss enthusiast" """
    }
    
    style_prompt = style_prompts.get(style.lower(), style_prompts["sarcastic"])
    
    prompt = f"""{style_prompt}

CRITICAL RULES:
1. NEVER use these overused phrases: {', '.join(FORBIDDEN)}.
2. Don't be generic. Be HYPERSPECIFIC. Specificity is where the humor lives.
3. Don't just describe the topic. Describe the EMOTIONAL DAMAGE or the WEIRD DETAIL.
4. Top text/Bottom text should feel like a cohesive thought, not two separate labels.

TOPIC: "{topic}"
STYLE: {style.upper()}

Return ONLY valid JSON:
{{
    "top_text": "Setup text (max 8 words)",
    "bottom_text": "Punchline text (max 8 words)",
    "image_prompt": "Describe a funny, modern reaction image. A character with a very specific, weird expression or in a bizarre situation that perfectly captures the irony."
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Gen-Z meme lord. You find traditional memes 'cringe'. You only make memes that would go viral on modern Reddit or Twitter. You use irony, self-deprecation, and specific situational humor. No clichés."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=1.1, # Max creativity
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        return {
            "top_text": result.get("top_text", "").upper(),
            "bottom_text": result.get("bottom_text", "").upper(),
            "image_prompt": result.get("image_prompt", f"Highly expressive character with weird face about {topic}")
        }
    except Exception as e:
        # Better fallback
        return {
            "top_text": "ME TRYING TO BE NORMAL",
            "bottom_text": "WHILE [TOPIC] ACTIVELY RUINS MY LIFE",
            "image_prompt": f"A character with a thousand yard stare about {topic}"
        }


def generate_image_stability(prompt: str, stability_api_key: str) -> Image.Image:
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {stability_api_key}",
        "Accept": "image/*"
    }
    
    # Modernized image prompt for Stability
    enhanced_prompt = f"""Meme reaction image: {prompt}

Style requirements:
- MODERN digital illustration / 2D cartoon style
- HIGH EXPRESSION: The face must be doing something weird and funny (shock, defeat, insane joy, or blank stare)
- Clean, simple, solid-color backgrounds (no clutter)
- Leave empty space at the very top and very bottom for text
- NO TEXT in the image itself
- High contrast, meme-reaction aesthetic"""

    data = {
        "prompt": enhanced_prompt,
        "output_format": "png",
        "aspect_ratio": "1:1",
        "negative_prompt": "real photo, photorealistic, text, watermark, blurry, complex background, 3d render"
    }
    
    try:
        response = requests.post(url, headers=headers, files={"none": ""}, data=data)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            raise Exception(f"Stability error: {response.status_code}")
    except Exception as e:
        raise Exception(f"Image failed: {str(e)}")


def generate_image_stability_v1(prompt: str, stability_api_key: str) -> Image.Image:
    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    headers = {
        "Authorization": f"Bearer {stability_api_key}",
        "Accept": "image/*"
    }
    data = {
        "prompt": f"Modern meme reaction: {prompt}, simple flat illustration style, expressive, vibrant",
        "output_format": "png",
        "aspect_ratio": "1:1",
        "model": "sd3.5-large"
    }
    try:
        response = requests.post(url, headers=headers, files={"none": ""}, data=data)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        raise Exception("SD3 fail")
    except Exception as e:
        raise Exception(f"SD3 error: {str(e)}")
