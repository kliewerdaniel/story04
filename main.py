import os
import glob
import base64
import json
import requests
import yaml
import argparse
import logging
import ollama
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PERSONA_FOLDER = "personas"
CACHE_FOLDER = "cache"
STORIES_FOLDER = "stories"

def list_text_files(folder):
    return sorted(glob.glob(os.path.join(folder, "*.txt")))

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def write_yaml(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

def write_text(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def extract_persona_from_text(text):
    prompt = f"""You are a world-class psychological analyst and computational literary theorist embedded in an advanced LLM. Your objective is to deeply analyze the following writing sample to reverse-engineer a nuanced and data-rich representation of the author’s psychological and narrative persona.

You will return your analysis in **valid YAML format**, structured with the following fields. Your analysis must be interpretive, sensitive to subtlety, and grounded in psychological realism.

---
PersonaSchema:
  name: >
    A plausible name that reflects the personality, cultural tone, and emotional charge of the writing sample.
    
  tone: >
    The dominant tonal signature. Choose or blend from tones such as irreverent, clinical, melancholic, earnest, ironic, poetic, paranoid, lyrical, didactic, satirical, etc.

  mood: >
    The emotional current beneath the surface. Describe both dominant and oscillating moods, if applicable (e.g., anxious but defiant, quietly elated, aggressively calm).

  formality: >
    Degree of linguistic formality or casualness. Use natural language labels like academic, relaxed, self-deprecating, ceremonial, streetwise, metaphysical, etc.

  perspective:
    pronouns: [first-person, second-person, third-person, mixed]
    narrative_distance: >
      Close, medium, or distant — describe how intimately or impersonally the narrator relates to the subject matter.
    temporal_orientation: >
      Does the writer dwell in memory, anticipate the future, or focus on the now?

  rhetorical_style:
    sentence_structure: >
      Comment on syntax (e.g., long and winding, clipped, recursive, breathless, minimalist).
    use_of_analogy: >
      Does the writer favor metaphor, simile, allegory, abstraction, or concrete literalism?
    persuasive_tactics: >
      Are they arguing, confessing, musing, venting, storytelling, or dialoguing with an internal voice?

  humor_profile:
    humor_type: [dark, dry, absurdist, slapstick, sarcastic, punny, self-deprecating, surreal, wordplay, observational, etc.]
    humor_target: >
      What is the typical subject of the humor? (e.g., the self, institutions, humanity, absurdity of life, physical reality)
    delivery_style: >
      Describe the delivery style — e.g., deadpan, explosive, meandering, sneaky punchlines, staccato one-liners, nested irony.
    frequency: >
      How often does humor appear? (saturated, sparse but sharp, consistent thread, rare)
    implicit_emotion: >
      What emotion underpins the humor? (e.g., anger, joy, despair, defiance, curiosity)

  values_and_themes:
    core_values: [list 3–5 values or beliefs inferred from the writing: e.g., justice, beauty, autonomy, defiance, connection, tradition]
    recurring_themes: [list 3–5 recurring themes or topics the author gravitates toward]
    implicit_worldview: >
      What implicit beliefs about human nature, society, or reality are embedded in the writing?

  lexical_and_stylistic_traits:
    favorite_words: [list 5–10 distinctive or repeated words]
    taboo_words: [if any, words the author avoids or handles cautiously]
    rhythm_and_pacing: >
      Describe how the language flows — musical, abrupt, rambling, staccato, breath-like?
    punctuation_signature: >
      Does the author use unconventional punctuation (e.g., em-dashes, ellipses, no punctuation, excessive commas)?
    capitalization_habits: >
      Any stylistic habits (e.g., all caps for emphasis, i instead of I, etc.)

  psychological_fingerprint:
    openness_to_experience: [1-10]
    conscientiousness: [1-10]
    extraversion: [1-10]
    agreeableness: [1-10]
    neuroticism: [1-10]
    cognitive_style: >
      Describe whether the writer seems more intuitive, logical, abstract, embodied, concrete, or poetic.
    inner_conflict: >
      Any evidence of internal contradictions or psychological tension?

  key_phrases: [list 5–10 phrases that uniquely capture the author’s voice or themes]
  
  summary_description: >
    A vivid, 4-6 sentence paragraph summarizing the narrator’s voice, tone, humor, psychology, and implied context. Include metaphor if useful.

---

Use deep psychological and literary reasoning to infer this schema from the sample.

Writing Sample:
{text}
Respond only with valid YAML, no explanation or preamble.
"""
    try:
        response = ollama.generate(
            model="gemma3:27b",
            prompt=prompt,
            format="json"
        )
        return yaml.safe_load(response["response"])
    except Exception as e:
        logging.error(f"Failed to extract persona: {e}")
        return {
            "name": "Default Persona",
            "tone": "Neutral",
            "mood": "Calm",
            "formality": "Neutral",
            "key_phrases": ["clear", "structured", "neutral"],
            "description": "A balanced and neutral narrator with an even tone."
        }

def generate_personas_from_input_folder(input_folder):
    os.makedirs(PERSONA_FOLDER, exist_ok=True)
    text_files = list_text_files(input_folder)
    persona_files = []
    for txt_file in text_files:
        text = read_file(txt_file)
        persona = extract_persona_from_text(text)
        base_name = os.path.splitext(os.path.basename(txt_file))[0]
        persona_path = os.path.join(PERSONA_FOLDER, base_name + ".yaml")
        write_yaml(persona_path, persona)
        persona_files.append(persona_path)
        logging.info(f"Generated persona: {persona_path}")
    return persona_files

def list_yaml_files(folder):
    return sorted(glob.glob(os.path.join(folder, "*.yaml")))

def load_yaml(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def list_image_files(folder_path):
    exts = ["*.jpg", "*.png", "*.jpeg"]
    image_files = []
    for ext in exts:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))
    return sorted(image_files)

def analyze_image(image_path, persona, force=False):
    os.makedirs(CACHE_FOLDER, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    cache_path = os.path.join(CACHE_FOLDER, f"{base_name}.json")

    if os.path.exists(cache_path) and not force:
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
            logging.info(f"Loaded cached analysis: {base_name}")
            return cached["description"]

    # Read and encode the image
    with open(image_path, "rb") as img_file:
        image_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    prompt = (
        f"Imagine you're viewing this photo. Describe what you see with these constraints:\n\n"
        f"Persona Name: {persona.get('name', 'Unknown')}\n"
        f"Tone: {persona.get('tone', 'Neutral')}\n"
        f"Mood: {persona.get('mood', 'Calm')}\n"
        f"Formality: {persona.get('formality', 'Neutral')}\n"
        f"Key Phrases: {', '.join(persona.get('key_phrases', []))}\n\n"
        f"Write a vivid and stylistically interesting description of the image."
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:27b",
                "prompt": prompt,
                "images": [image_b64],
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        description = result.get("response", "")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"description": description}, f)
        logging.info(f"Saved analysis: {cache_path}")
        return description
    except Exception as e:
        logging.error(f"Failed image analysis: {e}")
        return None

def load_all_cached_analyses():
    if not os.path.exists(CACHE_FOLDER):
        return []
    files = sorted(glob.glob(os.path.join(CACHE_FOLDER, "*.json")))
    analyses = []
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "description" in data:
                    analyses.append(data["description"])
        except Exception as e:
            logging.error(f"Error loading {fpath}: {e}")
    return analyses

def generate_story_from_analyses(analyses, persona):
    if not analyses:
        logging.error("No analyses available for story generation.")
        return None
    prompt = "Here are image descriptions:\n\n"
    for i, analysis in enumerate(analyses, start=1):
        prompt += f"Image {i}: {analysis}\n\n"
    prompt += (
        f"Write a reflective and stylistically distinctive story in the voice of {persona.get('name', 'Unknown')},\n"
        f"capturing a tone of '{persona.get('tone', 'Neutral')}' and a prevailing mood of '{persona.get('mood', 'Calm')}'.\n\n"
        f"Adopt a writing style that mirrors their rhetorical style:\n"
        f"- Use sentence structures that are {persona.get('rhetorical_style', {}).get('sentence_structure', 'balanced')}.\n"
        f"- Employ analogies or metaphor as {persona.get('rhetorical_style', {}).get('use_of_analogy', 'sparse or literal')}.\n"
        f"- Let the persuasive tone feel like they are {persona.get('rhetorical_style', {}).get('persuasive_tactics', 'contemplating or storytelling')}.\n\n"
        f"Integrate the persona’s humor subtly into the narrative:\n"
        f"- Use humor that is primarily {persona.get('humor_profile', {}).get('humor_type', 'dry or self-deprecating')},\n"
        f"  with delivery that is {persona.get('humor_profile', {}).get('delivery_style', 'meandering or ironic')},\n"
        f"  and underlying emotion of {persona.get('humor_profile', {}).get('implicit_emotion', 'bittersweet')}.\n"
        f"- Let it target {persona.get('humor_profile', {}).get('humor_target', 'existential absurdities or the narrator themselves')}.\n"
        f"- Adjust frequency to be {persona.get('humor_profile', {}).get('frequency', 'threaded or occasional')}.\n\n"
        f"Honor the narrator’s worldview and values:\n"
        f"- Let their worldview reflect beliefs about {persona.get('values_and_themes', {}).get('implicit_worldview', 'the complexity of human nature')}.\n"
        f"- Reinforce core values like {', '.join(persona.get('values_and_themes', {}).get('core_values', ['authenticity', 'resilience']))}.\n"
        f"- Weave in recurring themes such as {', '.join(persona.get('values_and_themes', {}).get('recurring_themes', ['identity', 'loss', 'connection']))}.\n\n"
        f"Mimic stylistic and lexical traits:\n"
        f"- Use favorite words such as {', '.join(persona.get('lexical_and_stylistic_traits', {}).get('favorite_words', ['dissonance', 'hollow', 'flicker']))}.\n"
        f"- Reflect a writing rhythm that is {persona.get('lexical_and_stylistic_traits', {}).get('rhythm_and_pacing', 'flowing but irregular')},\n"
        f"  and a punctuation style that is {persona.get('lexical_and_stylistic_traits', {}).get('punctuation_signature', 'elliptical or expressive')}.\n\n"
        f"Embed psychological subtext:\n"
        f"- Allow the cognitive style to guide the internal logic — whether {persona.get('psychological_fingerprint', {}).get('cognitive_style', 'intuitive or poetic')}.\n"
        f"- Hint at inner tensions such as: {persona.get('psychological_fingerprint', {}).get('inner_conflict', 'longing for clarity vs embracing ambiguity')}.\n\n"
        f"Include key phrases like:\n"
        f"\"{', '.join(persona.get('key_phrases', [])[:3])}\" somewhere in the narration.\n\n"
        f"Make the story introspective, emotionally layered, and authentic to this persona's unique literary fingerprint."
    )
    try:
        response = ollama.generate(
            model="mistral-small:24b-instruct-2501-q8_0",
            prompt=prompt
        )
        return response["response"]
    except Exception as e:
        logging.error(f"Story generation failed: {e}")
        return None

def save_story(story_text, persona_name):
    os.makedirs(STORIES_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{persona_name.replace(' ', '_').lower()}_story_{timestamp}.txt"
    filepath = os.path.join(STORIES_FOLDER, filename)
    write_text(filepath, story_text)
    logging.info(f"Saved story: {filepath}")
    return filepath

def select_persona_file(persona_files):
    print("Choose a persona:")
    for i, file in enumerate(persona_files, 1):
        print(f"{i}: {os.path.basename(file)}")
    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(persona_files):
            return persona_files[int(choice) - 1]
        print("Invalid choice.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-texts", required=True)
    parser.add_argument("--input-images", required=True)
    args = parser.parse_args()

    persona_files = generate_personas_from_input_folder(args.input_texts)
    if not persona_files:
        logging.error("No persona files found.")
        return

    persona_file = select_persona_file(persona_files)
    persona = load_yaml(persona_file)

    images = list_image_files(args.input_images)
    if not images:
        logging.error("No images found.")
        return

    use_cache = input("Use cached descriptions? (y/n): ").lower().startswith("y")
    analyses = load_all_cached_analyses() if use_cache else []
    if not use_cache or not analyses:
        analyses = [analyze_image(img, persona) for img in images if analyze_image(img, persona)]

    story = generate_story_from_analyses(analyses, persona)
    if story:
        save_story(story, persona.get("name", "Unknown"))

if __name__ == "__main__":
    main()
