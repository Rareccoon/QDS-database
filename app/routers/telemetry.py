from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.security import decode_access_token


router = APIRouter(
    tags=["Telemetry"]
)


@router.websocket("/ws/telemetry")
async def telemetry_websocket(
    websocket: WebSocket
):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(
            code=1008,
            reason="Authentication required"
        )
        return

    payload = decode_access_token(token)

    if payload is None:
        await websocket.close(
            code=1008,
            reason="Invalid or expired token"
        )
        return

    await websocket.accept()

    try:
        await websocket.send_json(
            {
                "event": "connected",
                "message": "Telemetry connection established",
                "user_id": payload.get("sub"),
                "role": payload.get("role")
            }
        )

        while True:
            message = await websocket.receive_text()

            if message == "ping":
                await websocket.send_json(
                    {
                        "event": "pong"
                    }
                )

    except WebSocketDisconnect:
        pass