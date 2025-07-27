# Study Assistant

A modular AI-powered assistant for personalized study planning and quiz generation.

## Features
- **Topic Extraction:** Understands user queries and extracts relevant study topics.
- **Quiz Planner:** Generates custom quizzes based on selected topics and question count.
- **Study Plan Generator:** Creates detailed, day-wise study plans tailored to user needs.
- **Feedback:** Provides constructive feedback based on quiz performance.

## System Flow
```
Start
  ↓
topic_extracter
  ↓ (Based on `decision`: quiz or study_plan)
 ┌────────────┐
 │            ↓
quiz_planner  study_plan
 │            │
 ↓            ↓
feedback     End
  ↓
 End
```

## Example Use Case
A user interacts with the assistant, inputs a topic, and chooses between a quiz or a study plan. The assistant dynamically adapts to the user's learning preference, providing quizzes or structured study plans, and feedback for improvement.

## How to Run
1. **Notebook Workflow:**
   - Open `quiz.ipynb` in Jupyter and run the cells to interact with the assistant.
2. **Web UI (Streamlit):**
   - Run `streamlit run ui.py` for the main assistant interface.
   - Run `streamlit run exam.py` for the quiz interface.
3. **API Integration:**
   - Start the FastAPI server: `python workflow_api.py`
   - The Streamlit UI will communicate with the workflow via the API.

## File Structure
- `quiz.ipynb` — Main notebook with workflow logic
- `ui.py` — Streamlit UI for user queries
- `exam.py` — Streamlit quiz interface
- `workflow_api.py` — FastAPI server to bridge UI and workflow
- `study_topics.md` — Documentation of modules and flow

## Requirements
- Python 3.8+
- Jupyter Notebook
- Streamlit
- FastAPI, Uvicorn
- nbformat, nbclient

Install dependencies:
```
pip install streamlit fastapi uvicorn nbformat nbclient
```

## Credits
Developed as a modular, extensible study assistant for personalized learning.
