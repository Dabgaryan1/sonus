from ollama import chat


def generate_explanations(progression, recommendations):

    prompt = f"""
    Current chord progression: {progression}
    Recommended next chords: {recommendations}

    Explain why each recommended chord might fit after the current progression.
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