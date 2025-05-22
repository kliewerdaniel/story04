

# Persona Extraction & Story Generation

This program analyzes writing samples to extract rich psychological and stylistic personas, then uses those personas to generate reflective, stylistic stories inspired by image descriptions. It leverages an LLM-based approach and combines text and image inputs to produce authentic narrative content tailored to unique personal voices.

---

## Features

- Extracts detailed persona profiles from writing samples, including tone, mood, humor style, cognitive traits, and more.
- Caches image analysis results to speed up repeated runs.
- Generates vivid, reflective stories that reflect the persona’s full psychological and stylistic fingerprint.
- Supports configurable input folders for writing samples and images.
- Uses Ollama API and local image analysis API for LLM-powered processing.

---

## Requirements

- Python 3.8+
- Ollama Python client installed and configured
- Local image analysis server running at `http://localhost:11434/api/generate` (or update URL in code)
- `PyYAML` for YAML parsing/writing
- `requests` for HTTP requests

---

## Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/kliewerdaniel/story04.git
   cd story04
```
2.	Create and activate a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3.	Install dependencies:
```bash
pip install -r requirements.txt
```

4.	Ensure Ollama is installed and the gemma3:27b and mistral-small:24b-instruct-2501-q8_0 models are available locally.

⸻

## Usage

Run the program from the command line:
```bash
python main.py --input-texts /path/to/writing_samples --input-images /path/to/images
```

Arguments:

	--input-texts : Directory containing .txt files with writing samples to extract personas.
	--input-images: Directory containing .jpg, .png, or .jpeg images to analyze.

Program Workflow:
	1.	Extracts personas from each writing sample.
	2.	Lets you select a persona to use for story generation.
	3.	Loads or generates image descriptions according to the selected persona.
	4.	Generates a reflective, stylistic story in the voice of the persona.
	5.	Saves the generated story in the stories/ folder.

⸻

## Persona Schema

The persona YAML includes detailed fields:
	•	name: Persona’s name or identifier
	•	tone: Overall emotional tone (e.g., optimistic, melancholic)
	•	mood: Narrative mood (e.g., calm, agitated)
	•	formality: Level of formality in speech or writing
	•	key_phrases: Distinctive phrases or expressions often used
	•	description: General description of persona characteristics
	•	humor_profile: Details on humor type, delivery style, frequency, and targets
	•	values_and_themes: Core values, recurring thematic elements, worldview
	•	psychological_fingerprint: Cognitive style, emotional tendencies, inner conflicts
	•	rhetorical_style: Sentence structure, use of metaphor, persuasive tactics
	•	lexical_and_stylistic_traits: Favorite words, rhythm, punctuation style

⸻

## Caching

Image analysis results are cached in the cache/ folder to avoid repeated costly analysis calls. The program prompts you to use cached data when available.

⸻

## Logging

The program logs key steps and errors with timestamps, helping you track progress and debug issues.

⸻

##  Extending & Customizing
	•	Modify or extend the persona extraction prompt for other psychological traits.
	•	Add support for additional image formats or analysis APIs.
	•	Adapt story generation to produce different narrative styles or formats.
	•	Integrate with other LLM providers or APIs.

⸻

## Troubleshooting
	•	Ensure Ollama is correctly installed and models are downloaded.
	•	Check your input folders contain valid .txt and image files.
	•	Review logs for error messages to pinpoint issues.

⸻

## License

MIT License © 2025 Daniel Kliewer

