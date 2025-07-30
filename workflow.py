from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, List, Dict, Optional, Literal
import json
import re
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()
class QuizItem(BaseModel):
    question: str
    answer: str
    options: List[str]

class StudyPlan(TypedDict):
    start_date: str
    end_date: str
    daily_plan: Dict[str, str]

class FeedbackItem(TypedDict):
    score: int
    suggestions: List[str]
    next_focus: List[str]

class OptionalResponse(TypedDict):
     optional_response: str
     suggesstions:str
class StudyAssisstant(TypedDict):
    query: str
    topic: str
    count: int
    decision: Literal['study_plan', 'quiz', 'another']
    quiz: Optional[List[QuizItem]]
    plan: Optional[StudyPlan]
    optional:Optional[OptionalResponse]
    score: int

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def quiz_planner(state: StudyAssisstant):
    topic = state['topic']
    count = state['count']
    prompt = f"""
You are a helpful and intelligent quiz generator.
Your task is to create a quiz based on the topic: **{topic}**
Number of questions to generate: {count}
Return the result as a JSON object with this format:
{{
  "items": [
    {{
      "question": "...",
      "answer": "...",
      "options": ["...", "...", "...", "..."]
    }}
  ]
}}
"""
    response = model.invoke(prompt)
    content = response.content.strip()
    content = re.sub(r"```json|```", "", content)
    content = re.sub(r"```python\n?|```", "", content)
    items = []
    try:
        data = json.loads(content)
        items = data["items"]
        print(items)
    except json.JSONDecodeError:
        pass
    return {'quiz':items}

def study_plan(state: StudyAssisstant):
    topic = state['topic']
    prompt = f"""
You are an expert AI assistant that generates effective and realistic study plans for students.
Generate a detailed 7-day study plan for the topic: "{topic}".
Your output **must be** in the following JSON format:
{{
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "daily_plan": {{
    "Day 1": "Introduction to the topic...",
    "Day 2": "Deep dive into concept A...",
    ...,
    "Day 7": "Revision and practice"
  }}
}}
Rules:
- Start from today’s date as start_date.
- The plan should span 7 days.
- Use simple and clear language.
- Do **not** include any explanation or text outside the JSON format.
Now generate the study plan.
"""
    response = model.invoke(prompt)
    content = re.sub(r"```json|```", "", response.content)
    print(type(content))
    return {'plan':content}

def topic_extracter(state: StudyAssisstant):
    query = state['query']
    prompt = f"""
You are an intelligent assistant designed to classify and extract structured information from user study-related queries.
Given the following user query:
query: "{query}"
Your task is to analyze the intent and return a structured response with the following format:
- decision: Literal['study_plan', 'quiz', 'another']
Interpretation rules:
1. If the query is about preparing or taking a quiz/test:
   - decision: 'quiz'
   - topic: Identify the main topic or subject of the quiz (e.g., "binary trees", "OS scheduling").
   - count: Extract the number of quiz questions requested (e.g., "give me 5 questions"), or return a default value of 10 if not specified.
2. If the query is about planning or organizing a study session:
   - decision: 'study_plan'
   - topic: Identify the primary subject or concept the user wants to study.
3. If the query does not fall under 'quiz' or 'study_plan':
   - decision: 'another'
   - query: Return a clearer and more structured version of the query that reflects a likely learning intent (e.g., factual lookup, concept review), without asking the user to clarify.
   - Avoid asking follow-up questions. Instead, rewrite the query with a possible useful direction or framing.
Be concise, accurate, and avoid assumptions unless logically inferred from the query.
"""
    response = model.invoke(prompt)
    content = re.sub(r"```json|```", "", response.content)
    content = re.sub(r"```", "", content)
    try:
        obj = json.loads(content)
        print(obj)
    except Exception:
        obj = {}
    return obj

def check(state: dict) -> Literal["quiz_planner", "study_plan", "another"]:
    if state['decision'] == "quiz":
        return "quiz_planner"
    elif state['decision'] == 'study_plan':
        return "study_plan"
    else:
        return "another"

def another(state: StudyAssisstant): 
    query = state['query']
    prompt = f"""
You are an intelligent academic assistant integrated into a website that helps students learn effectively. 
The user has asked the following query: "{query}"

Your tasks:
1. Carefully analyze the query and identify its intent.
2. If the query is ambiguous or unrelated to direct learning (like jokes, general facts, etc.), politely reframe it into a study-related task if possible.
3. Respond in a clear, helpful, and student-friendly tone.
4. End your response with one or more actionable suggestions that guide the user back into learning activities—such as:
   - "Would you like a quiz on this topic?"
   - "Need a study plan to cover this subject?"
   - "Would you like to break this into smaller topics?"
   - "Want flashcards or practice questions?"

Return your final response strictly as a JSON object in the following format:

{{
  "optional_response": "Your intelligent and helpful answer or rephrased suggestion here.",
  "suggesstions": "Your additional website-specific follow-up suggestions here."
}}

Do not include any explanations, markdown, or extra text outside the JSON.
"""
    response = model.invoke(prompt)
    content = re.sub(r"```json|```", "", response.content)
    try:
        obj = json.loads(content)
    except Exception:
        obj = {
            "optional_response": "Sorry, I couldn't process your query clearly. Could you rephrase it or ask about a topic you'd like to study?",
            "suggesstions": "You can try: 'Give me a study plan for Python' or 'Make a quiz on World War II'."
        }
    return {'optional':obj}

def feedback(state: StudyAssisstant):
    prompt = f"""
You are an intelligent academic assistant providing feedback on a user's quiz performance.
Topic: {state["topic"]}
Score: {state["score"]} out of {state['count']}
Your task:
- Analyze the user's score and provide constructive, personalized feedback.
- If the score is low, highlight weak areas and suggest specific subtopics to revise.
- If the score is average, suggest reinforcement and practice strategies.
- If the score is high, praise the performance and recommend advanced or related topics to explore.
- Offer 2–3 practical study suggestions to improve or go deeper.
- Keep the tone encouraging and helpful.
Be concise but informative.
"""
    response = model.invoke(prompt)
    return {'feedback': response.content}

def build_workflow():
    graph = StateGraph(StudyAssisstant)
    graph.add_node("topic_extracter", topic_extracter)
    graph.add_node("quiz_planner", quiz_planner)
    graph.add_node("study_plan", study_plan)
    graph.add_node("another", another)
    # graph.add_node('feedback', feedback)
    graph.add_edge(START, "topic_extracter")
    graph.add_conditional_edges("topic_extracter", check)
    graph.add_edge("quiz_planner", END)
    # graph.add_edge('feedback', END)
    graph.add_edge("another", END)
    graph.add_edge("study_plan", END)
    workflow = graph.compile()
    return workflow

# wf=build_workflow()
# res=wf.invoke({'query':'what are trending courses'})
# print(res)
# res=study_plan({'topic':'java'})

