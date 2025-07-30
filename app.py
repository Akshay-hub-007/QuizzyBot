import asyncio
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from workflow import build_workflow, StudyAssisstant

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class QueryRequest(BaseModel):
    query: str

workflow = build_workflow()

@app.post("/run_workflow")
async def run_workflow(req: QueryRequest):
    state={}
    state['query'] = req.query
    print(req.query)
    # Run the workflow
    try:
        result = workflow.invoke(state)
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


