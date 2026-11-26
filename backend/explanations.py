from ollama import chat, ResponseError
from template_explanations import generate_template_explanation


def generate_explanations(progression, recommendations):

    explanations = []
    previousChord = progression[-1]

    for predictedChord in recommendations:

        # Generate the rule-based explanation
        templateExplanation = generate_template_explanation(
            previousChord, predictedChord
        )

        prompt = f"""
        Current chord progression: {progression}
        Recommended next chord: {predictedChord}
        Rule-based explanation: {templateExplanation}

        Suggest how the musician might creatively use this
        recommendation to explore a particular mood or atmosphere.
        Do not explain why the chord works.
        """

        try:
            response = chat(
                model="qwen3:1.7b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a creative songwriting assistant. "
                            "Your only job is to suggest subjective artistic possibilities "
                            "to the musician. "
                            "The provided rule-based explanation is complete and does not "
                            "require any additional analysis. "
                            "Do not explain why the chord works. "
                            "Do not analyze the chord progression. "
                            "Do not mention notes, keys, scales, intervals, chord relationships, "
                            "harmonic functions, tension, resolution, or voice leading. "
                            "Do not repeat information from the rule-based explanation. "
                            "Focus exclusively on potential moods, emotions, and atmosphere. "
                            "Address the musician directly using words like 'you' and 'your'. "
                            "Frame all suggestions as creative possibilities, not guarantees. "
                            "Begin with phrases such as 'Try this if', 'You might enjoy', "
                            "or 'Consider this if'. "
                            "Do not recommend new chords. "
                            "Return only one sentence of no more than 25 words. "
                            "Do not justify your creative suggestions using musical relationships. "
                            "Do not explain why a suggested mood might occur. "
                            "Only suggest what the musician could creatively explore. "

                            "Example of an acceptable response: "
                            "'Try this if you want to explore a nostalgic or reflective atmosphere.' "

                            "Example of an unacceptable response: "
                            "'Try this because the shared notes create a nostalgic atmosphere.' "

                            "Do not include a musical justification for your suggestion. "
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                think=False
            )

            creativeExplanation = response.message.content.strip()

            # Combine the template and LLM explanations
            explanation = f"{templateExplanation} {creativeExplanation}"
        except (ConnectionError, ResponseError) as e:
            #Fallback to template explanation if Ollama is unavailable
            print(f"Ollama unavailable: {e}")
            explanation = templateExplanation

        explanations.append(explanation)

    return explanations