from explanations import generate_explanations

###hardcoded progression and recommendations for testing
progression = ["C", "Am", "F"]
recommendations = ["G", "Dm", "C"]

explanations = generate_explanations(progression, recommendations)

for chord, explanation in zip(recommendations, explanations):
    print(f"{chord}: {explanation}")
    print()