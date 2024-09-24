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
    st.page_link("pages/RIASEC assesment.py", label="RIASEC assessment")

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
    "I like to work on cars",
    "I like to do puzzles",
    "I am good at working independently",
    "I like to work in teams",
    "I am an ambitious person, I set goals for myself",
    "I like to organize things, (files, desks/offices)",
    "I like to build things",
    "I like to do experiments",
    "I like to read about art and music",
    "I like to teach or train people",
    "I like to try to influence or persuade people",
    "I like to have clear instructions to follow",
    "I like to take care of animals",
    "I enjoy science",
    "I enjoy creative writing",
    "I like trying to help people solve their problems",
    "I like selling things",
    "I wouldn’t mind working 8 hours per day in an office",
    "I like putting things together or assembling things",
    "I enjoy trying to figure out how things work",
    "I am a creative person",
    "I am interested in healing people",
    "I am quick to take on new responsibilities",
    "I pay attention to details 25.",
    "I like to cook",
    "I like to analyze things (problems/ situations)",
    "I like to play instruments or sing",
    "I enjoy learning about other cultures",
    "I would like to start my own business",
    "I like to do filing or typing",
    "I am a practical person",
    "I like working with numbers or charts",
    "I like acting in plays",
    "I like to get into discussions about issues",
    "I like to lead",
    "I am good at keeping records of my work",
    "I like working outdoors",
    "i’m good at math",
    "I like to draw",
    "I like helping people",
    "I like to give speeches",
    "I would like to work in an office" 
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

    # if not os.path.exists('docs'):
    #     os.makedirs('docs')

    # Save to CSV file in the 'docs' folder
    scores_df = pd.DataFrame(list(scores.items()), columns=['Type', 'Score'])
    scores_df.to_csv('docs/riasec_results.csv', mode='w', header=True, index=False)

    st.success("Your answers have been saved in the 'docs' folder.")
else:
    st.write("Please answer all questions and click Submit to see your result.")
