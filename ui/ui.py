
import streamlit as st
import requests
import json
st.set_page_config(page_title="Study Assistant", page_icon="🧠", layout="centered")
# st.title("🧠 Study Assistant")

if 'page' not in st.session_state:
    st.session_state.page = 'chat'
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


def show_quiz():
    quiz_data = st.session_state.quiz_data
    idx = st.session_state.get('quiz_idx', 0)
    score = st.session_state.get('quiz_score', 0)
    if idx < len(quiz_data):
        q = quiz_data[idx]
        st.subheader(f"Question {idx+1} of {len(quiz_data)}")
        st.write(q['question'])
        selected = st.radio("Select an option:", q['options'], key=f"quiz_{idx}", index=None)
        if st.button("Next", key=f"next_{idx}"):
            if selected == q['answer']:
                st.session_state.quiz_score = score + 1
            else:
                st.session_state.quiz_score = score
            st.session_state.quiz_idx = idx + 1
            st.rerun()
    else:
        st.success(f"Quiz Complete! Your Score: {score} / {len(quiz_data)}")
        if st.button("Back to Chat"):
            st.session_state.page = 'chat'
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_data = []
            st.rerun()

def show_study_plan(plan):
    print(plan)
    st.subheader("Your Study Plan")
    plan=json.loads(plan)
    # if isinstance(plan, str):
    #     st.write(plan.get())
    if isinstance(plan, dict):
        start = plan.get('start_date', '')
        end = plan.get('end_date', '')
        
        st.markdown(f"**Start Date:** {start}")
        st.markdown(f"**End Date:** {end}")
        daily_plan = plan.get('daily_plan', {})
        if daily_plan:
            st.markdown("---")
            st.markdown("### Daily Breakdown")
            for day, desc in daily_plan.items():
                st.markdown(f"<div style='margin-bottom:16px;'><span style='font-weight:bold;font-size:1.1em;'>{day}:</span><br><span style='margin-left:10px;'>{desc}</span></div>", unsafe_allow_html=True)
        else:
            st.info("No daily plan found.")
    if st.button("Back to Chat"):
        st.session_state.page = 'chat'
        st.rerun()

if st.session_state.page == 'chat':
    for msg in st.session_state.chat_history:
        st.chat_message(msg['role']).write(msg['content'])
    query = st.chat_input("Eg: Give me 15 questions on operating system process scheduling")
    if query:
        st.chat_message("user").write(query)
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.spinner("Processing your request..."):
            try:
                state = {}
                response = requests.post(
                    "http://localhost:8000/run_workflow",
                    json={"query": query},
                    timeout=60
                )
                print(response)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("decision") == "quiz" and result.get("quiz"):
                        st.session_state.quiz_data = result["quiz"]
                        st.session_state.page = 'quiz'
                        st.session_state.quiz_idx = 0
                        st.session_state.quiz_score = 0
                        st.rerun()
                    elif result.get("decision") == "study_plan" and result.get("plan"):
                        st.session_state.study_plan = result["plan"]
                        st.session_state.page = 'study_plan'
                        st.rerun()
                    else:
                        print(result)
                        reply = result.get("optional", {})
                        # print(type(reply))
                        # reply=json.loads(reply)
                        print(type(reply))
                        if isinstance(reply, dict):
                            response_text = reply.get("optional_response", "") or reply.get("suggestion", "") or "I'm not sure how to help with that. Could you clarify your request?"
                            suggestions_text = reply.get("suggesstions", "")
                        elif isinstance(reply, str):
                            response_text = reply
                            suggestions_text = ""
                        else:
                            response_text = "I'm not sure how to help with that. Could you clarify your request?"
                            suggestions_text = ""

                        st.chat_message("assistant").write(response_text)
                        if suggestions_text:
                            st.chat_message("assistant").write(f"💡 {suggestions_text}")

                        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                        if suggestions_text:
                            st.session_state.chat_history.append({"role": "assistant", "content": f"💡 {suggestions_text}"})
                else:
                    st.error(f"Error from backend: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
elif st.session_state.page == 'quiz':
    show_quiz()
elif st.session_state.page == 'study_plan':
    show_study_plan(st.session_state.get('study_plan', {}))

