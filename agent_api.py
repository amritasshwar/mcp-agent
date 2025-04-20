from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import os
import agent_mcp
import asyncio
from agent_mcp.mcp_decorator import mcp_agent, DEFAULT_MCP_SERVER
from agent_mcp.mcp_transport import HTTPTransport
from agent_mcp.langchain_mcp_adapter import LangchainMCPAdapter
from agent_runner import run_agent, agent_executor, agent

app = FastAPI()

class TaskRequest(BaseModel):
    input: str

@mcp_agent(mcp_id="Influenxers")
class InfluenxersAgent(LangchainMCPAdapter):
    def __init__(self):
        super().__init__(
            name="Influenxers",
            transport=HTTPTransport.from_url(DEFAULT_MCP_SERVER),
            client_mode=False,           # server mode
            langchain_agent=agent,
            agent_executor=agent_executor
        )
    
async def start_influencer_agent_network_listener():
    # Create and initialize the email agent
    influencer_agent = InfluenxersAgent()
    
    # Connect to the MCP network
    await influencer_agent.connect()
    print("Influencer agent is connected and ready to receive tasks")
    

    # Start message and task processors
    await influencer_agent.run()

    try:
        # Wait for interrupt - the adapter handles message processing
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down influencer agent...")
        await influencer_agent.disconnect()

@app.on_event("startup")
async def startup():
    task = asyncio.create_task(start_influencer_agent_network_listener())


@app.post("/agent")
async def run_agent_api(request: TaskRequest):
    try:
        response = run_agent(request.input)
        return {"output": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
