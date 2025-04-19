from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from agent_mcp.mcp_decorator import mcp_agent
from agent_runner import run_agent, langchain_worker

app = FastAPI()

class TaskRequest(BaseModel):
    input: str

@app.post("/agent")
@mcp_agent(mcp_id="Influenxers", adapter=langchain_worker)
async def run_agent_api(request: TaskRequest):
    try:
        response = run_agent(request.input)
        return {"output": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
