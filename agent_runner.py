import os
import requests
import sys
from agent_mcp.langchain_mcp_adapter import LangchainMCPAdapter
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# === Load Environment ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# === Tool Functions with 30-Min Timeout ===

import re
import json

def extract_url_from_string(s):
    # Extract first Notion URL
    urls = re.findall(r'https:\/\/[^\s"}]+', s)
    return urls[0] if urls else ""

def ingest_product(data):
    try:
        if isinstance(data, str):
            data = {
                "username": "michelechungugc",
                "url": data.strip()
            }

        url_value = data.get("url")

        # 🛡️ Case 1: malformed dict inside a string
        if isinstance(url_value, str) and ("url:" in url_value or "notion.site" in url_value):
            print("⚠️ Cleaning 'url' string...")
            extracted_url = extract_url_from_string(url_value)
            data["url"] = extracted_url

        # 🛡️ Case 2: 'url' is a dict (super weird case)
        elif isinstance(url_value, dict):
            print("⚠️ 'url' is a dict. Extracting...")
            data["url"] = url_value.get("url", "")

        # ✅ Final cleanup
        data["url"] = str(data["url"]).strip().replace("“", "").replace("”", "").replace("'", "").replace("\"", "")

        # Debug print
        print("🔍 Final Payload:")
        print("  Username:", data["username"])
        print("  URL:", data["url"])

        headers = {"Content-Type": "application/json"}
        res = requests.post(
            "http://analytics-prototype-lb-294479199.us-east-2.elb.amazonaws.com/ingest/product",
            json=data,
            headers=headers,
            timeout=1800
        )

        print("🔍 Response:", res.status_code, res.text)
        return res.text

    except Exception as e:
        return f"❌ Ingest failed: {e}"

def scrape_tiktok(data):
    try:
        res = requests.post(
            "https://hznjnyps85.execute-api.us-east-2.amazonaws.com/prod/collect",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=1800
        )
        return res.text
    except Exception as e:
        return f"❌ Scrape failed: {e}"

def analyze_creator_style(data):
    try:
        res = requests.post(
            "http://analytics-prototype-lb-294479199.us-east-2.elb.amazonaws.com/creator/analyze/style",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=1800
        )
        return res.text
    except Exception as e:
        return f"❌ Style analysis failed: {e}"

def generate_script(data):
    try:
        res = requests.post(
            "http://analytics-prototype-lb-294479199.us-east-2.elb.amazonaws.com/suggest/script",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=1800
        )
        return res.text
    except Exception as e:
        return f"❌ Script generation failed: {e}"

def suggest_edits(data):
    try:
        res = requests.post(
            "http://analytics-prototype-lb-294479199.us-east-2.elb.amazonaws.com/suggest/edits",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=1800
        )
        return res.text
    except Exception as e:
        return f"❌ Edit suggestion failed: {e}"

# === LangChain Tools ===

tools = [
    Tool.from_function(
        name="IngestProduct",
        description=(
            "Ingest a product brief. Provide input as a JSON object with keys: "
            "'username' (e.g., 'michelechungugc') and 'url' (a public Notion link). "
            "Example: {\"username\": \"michelechungugc\", \"url\": \"https://notion.site/...\"}. "
            "If only a Notion URL is passed, the default username 'michelechungugc' will be used."
        ),
        func=ingest_product
    ),
    Tool.from_function(
        name="ScrapeTikTokInspiration",
        description="Scrape TikTok videos using keywords. Input: {'search_terms': [str]}",
        func=scrape_tiktok
    ),
    Tool.from_function(
        name="AnalyzeCreatorStyle",
        description="Analyze a creator's style. Input: {'handle': str}",
        func=analyze_creator_style
    ),
    Tool.from_function(
        name="GenerateScript",
        description="Generate a video script. Input: {'username': str}",
        func=generate_script
    ),
    Tool.from_function(
        name="SuggestEdits",
        description="Suggest edits for a TikTok video. Input: {'tiktok_url': str}",
        func=suggest_edits
    )
]

# === LangChain Agent Setup ===

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Influenxers, an AI agent helping with influencer video marketing tasks."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=openai_api_key)
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

langchain_worker = LangChainMCPAdapter(
    name="Influenxers",
    description="Influenxers is an AI agent helping with influencer video marketing tasks.",
    agent_executor=agent_executor,
    langchain_agent=agent,
    client_mode=True,
    agent_type="langchain"
)
# === Public Interface for Discord ===

def run_agent(task_text: str):
    result = agent_executor.invoke({
        "input": task_text,
        "agent_scratchpad": []
    })
    return result["output"]
