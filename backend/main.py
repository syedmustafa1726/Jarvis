from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_v2 import JarvisAgentV2
import uuid
import json

app = FastAPI(title="JARVIS API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = JarvisAgentV2()
conversation_id = str(uuid.uuid4())

# Connected HUD clients
connected_clients = set()


class ChatRequest(BaseModel):
    message: str
    user_name: str = "Sir"


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


async def broadcast(event_type: str, data=None):
    """Send a state/event to every connected HUD."""

    message = {
        "type": event_type,
        "data": data
    }

    disconnected = set()

    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
        except Exception:
            disconnected.add(client)

    for client in disconnected:
        connected_clients.discard(client)


@app.get("/")
def root():
    return {
        "status": "JARVIS is online",
        "version": "2.1.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:

        # HUD → THINKING
        await broadcast("thinking")

        response = await agent.chat(
            request.message,
            request.user_name
        )

        # HUD → RESPONSE
        await broadcast(
            "response",
            {
                "text": response
            }
        )

        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )

    except Exception as e:

        await broadcast(
            "error",
            {
                "message": str(e)
            }
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/reset")
async def reset_conversation():

    global conversation_id

    conversation_id = str(uuid.uuid4())

    agent.history = []

    await broadcast("reset")

    return {
        "status": "Conversation reset successfully"
    }


@app.get("/history")
async def get_history():

    return {
        "history": [
            {
                "role": "user" if message.__class__.__name__ == "HumanMessage"
                else "assistant",
                "content": message.content
            }
            for message in agent.history
        ]
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    connected_clients.add(websocket)

    print("🟢 HUD connected")

    try:

        # Tell newly connected HUD the current state
        await websocket.send_text(
            json.dumps({
                "type": "connected",
                "data": {
                    "status": "online"
                }
            })
        )

        while True:

            # Listen for messages from HUD
            message = await websocket.receive_text()

            print(f"📡 HUD: {message}")

    except WebSocketDisconnect:

        print("🔴 HUD disconnected")

    except Exception as e:

        print(f"❌ WebSocket error: {e}")

    finally:

        connected_clients.discard(websocket)