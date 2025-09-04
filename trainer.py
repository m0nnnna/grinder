import random

def generate_trainer_skills(skills):
    # Select 4 random skills (or all if fewer than 4)
    available_skills = skills['skills']
    return random.sample(available_skills, min(4, len(available_skills)))