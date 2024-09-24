import streamlit as st
import pandas as pd
import os

# Hide sidebar items
st.markdown(
    """
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True
)

# Sidebar navigation
with st.sidebar:
    st.markdown("## Navigation")
    st.page_link("rag_app.py", label="Home")
    st.page_link("pages/Profile.py", label="Profile")
    st.page_link("pages/RIASEC.py", label="RIASEC Assessment")

# RIASEC Test function
def assess_ria_sec(answers):
    types = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
    scores = {t: 0 for t in types}

    # Assume each question corresponds to a certain personality type
    for i, ans in enumerate(answers):
        scores[types[i % len(types)]] += ans

    # Determine the dominant RIASEC type
    dominant_type = max(scores, key=scores.get)
    return dominant_type, scores

# Define 12 questions (each question is linked to one of the RIASEC types)
questions = [
    "I like working with tools or machines.",          # Realistic
    "I enjoy studying complex problems.",              # Investigative
    "I like creating art or music.",                   # Artistic
    "I enjoy helping others and teaching.",            # Social
    "I like persuading others to my viewpoint.",       # Enterprising
    "I enjoy organizing information and details.",     # Conventional
    "I prefer working outdoors rather than in an office.", # Realistic
    "I am curious and enjoy learning new things.",     # Investigative
    "I enjoy performing or expressing myself creatively.", # Artistic
    "I like planning and following structured activities.", # Conventional
    "I am good at leading and managing others.",       # Enterprising
    "I enjoy working with people in groups.",          # Social
]

st.title("RIASEC Personality Assessment")

# Input answers for the 12 questions (Likert scale: 1 to 5)
answers = []
for q in questions:
    answers.append(st.slider(q, 1, 5, 3))  # Default slider value set to 3 (neutral)

# Submit button
if st.button("Submit"):
    # Assess the RIASEC type
    dominant_type, scores = assess_ria_sec(answers)

    # Show result
    st.write(f"Your dominant RIASEC type is: **{dominant_type}**")
    st.write("Scores by type:")
    st.write(scores)

    # Create the 'docs' folder if it doesn't exist
    if not os.path.exists('docs'):
        os.makedirs('docs')

    # Save to CSV file in the 'docs' folder with the format Realistic,score, etc.
    scores_df = pd.DataFrame(list(scores.items()), columns=['Type', 'Score'])
    scores_df.to_csv('docs/riasec_results.csv', mode='a', header=False, index=False)

    st.success("Your answers have been saved in the 'docs' folder.")
else:
    st.write("Please answer all questions and click Submit to see your result.")
