import sys, os
# allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import pytest
from agent_api import InfluenxersAgent

@pytest.mark.asyncio
async def test_influencer_campaign_task():
    # Instantiate and initialize via decorator
    agent = InfluenxersAgent()
    await agent.connect()

    # Capture outgoing send_message
    results = []
    async def fake_send_message(target, message):
        results.append((target, message))
    agent.transport.send_message = fake_send_message

    # Craft a MCP "task" message
    msg = {
        "type": "task",
        "content": {
            "task_id": "campaign_001",
            "description": (
                "Analyze a business/social influencer campaign strategy:\n"
                "- Identify the best channels (TikTok, Instagram, YouTube)\n"
                "- Suggest 3 micro-influencer profiles\n"
                "- Outline KPIs and targeting\n"
                "- Provide a 4-week rollout plan"
            ),
            "reply_to": "dummy_target"
        }
    }

    # Run task processor in background
    task_proc = asyncio.create_task(agent.process_tasks())

    # Inject message
    await agent.handle_incoming_message(msg, message_id="msg-1")
    # Allow processing
    await asyncio.sleep(1)

    # Teardown
    task_proc.cancel()
    await asyncio.gather(task_proc, return_exceptions=True)
    await agent.disconnect()

    # Verify we sent at least one message back
    assert results, "No reply sent"
    target, message = results[0]
    assert target == "dummy_target"
    assert isinstance(message, dict)
    assert 'task_id' in message or 'result' in message or isinstance(message, str)
