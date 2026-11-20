from explanations import generate_explanations

###hardcoded progression and recommendations for testing
progression = ["C", "Am", "F"]

recommendations = [
    {"chord": "G", "probability": 0.65},
    {"chord": "C", "probability": 0.15},
    {"chord": "G7", "probability": 0.08}
]

result = generate_explanations(progression, recommendations)
print(result)