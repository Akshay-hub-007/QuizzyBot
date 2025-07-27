

# Streamlit Quiz App
import streamlit as st

# Example quiz data
QUIZZES = [
    {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "options": ["Paris", "London", "Berlin", "Madrid"]
    },
    {
        "question": "What is 2 + 2?",
        "answer": "4",
        "options": ["3", "4", "5", "6"]
    },
    {
        "question": "Which is a mammal?",
        "answer": "Dolphin",
        "options": ["Shark", "Dolphin", "Octopus", "Trout"]
    }
]

st.set_page_config(page_title="Quiz App", page_icon="📝", layout="centered")
st.title("📝 Quiz App")

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.answers = []

idx = st.session_state.idx

if idx < len(QUIZZES):
    quiz = QUIZZES[idx]
    st.subheader(f"Question {idx+1} of {len(QUIZZES)}")
    st.write(quiz['question'])
    selected = st.radio("Select an option:", quiz['options'], key=idx, index=None)
    if st.button("Next"):
        st.session_state.answers.append(selected)
        if selected == quiz['answer']:
            st.session_state.score += 1
        st.session_state.idx += 1
        st.rerun()
else:
    st.success(f"Quiz Complete! Your Score: {st.session_state.score} / {len(QUIZZES)}")
    st.write("\n**Your Answers:**")
    for i, quiz in enumerate(QUIZZES):
        st.write(f"Q{i+1}: {quiz['question']}")
        st.write(f"Your answer: {st.session_state.answers[i]}")
        st.write(f"Correct answer: {quiz['answer']}")
        st.write("---")
    if st.button("Restart Quiz"):
        st.session_state.idx = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.rerun()
