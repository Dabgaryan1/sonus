from ollama import chat


def generate_explanations(progression, recommendations):

    prompt = f"""
    Current chord progression: {progression}
    Recommended next chords: {recommendations}

    Explain why each recommended chord might fit after the current progression.

    HARMONIC ACCURACY RULES:
        - Only describe harmonic relationships that can be
        supported by the provided chord progression.
        - Do not claim a chord creates a resolution, cadence,
        modulation, or tonic-dominant relationship unless
        the provided progression clearly supports it.
        - Do not assume a key unless it is explicitly provided.
        - Do not invent musical context, genres, or intentions.
        - If a harmonic function is uncertain, explain a
        simpler, verifiable relationship instead, such as
        shared notes or chord repetition.
        - Never invent a relationship just to provide an
        explanation.
    """
    

    response = chat(
        model="qwen3:1.7b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Your job is to examine a given chord sequence and three recommended chords to follow that sequence. "
                    "Explain why each chord was recommended concisely. "
                    "Do not invent music theory facts. "
                    "Only use known, established music theory facts. "
                    "Do not treat prediction probabilities as measures of music theory correctness. "
                    "Do not try to recommend new chords. "
                    "Only give 1-2 sentence explanations for each chord."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        think=False
    )

    explanation = response.message.content
    return explanation