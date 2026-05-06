import json
import logging
import uvicorn
from fastapi import FastAPI, Request
from tools import handle_tool_call
from config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="Vapi Voice Agent Webhook")

@app.post("/webhook")
async def vapi_webhook(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from webhook payload")
        return {"error": "Invalid JSON"}

    msg = body.get("message", {})
    msg_type = msg.get("type")

    logger.debug(f"Received webhook message type: {msg_type}")

    if msg_type == "tool-calls":
        results = []
        for call in msg.get("toolCalls", []):
            fn = call.get("function", {})
            fn_name = fn.get("name")
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except json.JSONDecodeError:
                logger.error(f"Failed to parse arguments for tool {fn_name}")
                args = {}
                
            # Now asynchronously awaiting the tool call to prevent blocking the event loop
            result = await handle_tool_call(fn_name, args)
            results.append({"toolCallId": call.get("id"), "result": result})
            
        return {"results": results}

    elif msg_type == "end-of-call-report":
        ended_reason = msg.get("endedReason")
        duration = msg.get("durationSeconds")
        summary = msg.get("summary")
        logger.info(f"Call ended. Reason: {ended_reason}, Duration: {duration}s")
        logger.info(f"Call Summary: {summary}")

    return {"status": "ok"}

if __name__ == "__main__":
    # Running uvicorn directly for easy starting
    # In production, you might run `uvicorn webhook:app --host 0.0.0.0 --port 8000` from CLI
    logger.info("Starting webhook server on port 8000...")
    uvicorn.run("webhook:app", host="0.0.0.0", port=8000, reload=True)