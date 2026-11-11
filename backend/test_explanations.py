from explanations import generate_explanations

###hardcoded progression and recommendations for testing
progression = ["C", "Am", "F"]

recommendations = [
    {"chord": "G", "probability": 0.52},
    {"chord": "Am", "probability": 0.28},
    {"chord": "F", "probability": 0.15}
]

result = generate_explanations(progression, recommendations)
print(result)