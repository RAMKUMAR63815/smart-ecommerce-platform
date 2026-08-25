from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List


router = APIRouter(
    tags=["WebSocket"]
)


# =========================================================
# CONNECTION MANAGER
# =========================================================

class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    # =====================================================
    # CONNECT
    # =====================================================

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket
    ):

        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)

        print()
        print("=" * 70)
        print("WEBSOCKET CONNECTED")
        print("User ID:", user_id)
        print(
            "User connections:",
            len(self.active_connections[user_id])
        )
        print(
            "Connected users:",
            list(self.active_connections.keys())
        )
        print("=" * 70)
        print()


    # =====================================================
    # DISCONNECT
    # =====================================================

    def disconnect(
        self,
        user_id: int,
        websocket: WebSocket
    ):

        if user_id in self.active_connections:

            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        print()
        print("=" * 70)
        print("WEBSOCKET DISCONNECTED")
        print("User ID:", user_id)
        print(
            "Remaining connected users:",
            list(self.active_connections.keys())
        )
        print("=" * 70)
        print()


    # =====================================================
    # SEND TO USER
    # =====================================================

    async def send_to_user(
        self,
        user_id: int,
        message: dict
    ):

        connections = self.active_connections.get(
            user_id,
            []
        )

        print()
        print("=" * 70)
        print("WEBSOCKET SEND REQUEST")
        print("User ID:", user_id)
        print("Connections found:", len(connections))
        print("Event:", message.get("event"))
        print("Message:", message)
        print("=" * 70)

        # -------------------------------------------------
        # NO CONNECTION
        # -------------------------------------------------

        if not connections:

            print(
                f"WARNING: No active WebSocket connection "
                f"for user {user_id}"
            )

            print(
                "Currently connected users:",
                list(self.active_connections.keys())
            )

            print()

            return False

        # -------------------------------------------------
        # SEND
        # -------------------------------------------------

        sent_successfully = False
        disconnected = []

        for websocket in connections:

            try:

                await websocket.send_json(message)

                print(
                    f"SUCCESS: WebSocket message sent "
                    f"to user {user_id}"
                )

                sent_successfully = True

            except Exception as e:

                print(
                    f"ERROR: WebSocket send failed "
                    f"for user {user_id}: {e}"
                )

                disconnected.append(websocket)

        # -------------------------------------------------
        # REMOVE DEAD CONNECTIONS
        # -------------------------------------------------

        for websocket in disconnected:

            self.disconnect(
                user_id,
                websocket
            )

        print(
            "WebSocket send result:",
            sent_successfully
        )

        print()

        return sent_successfully


    # =====================================================
    # CHECK USER CONNECTION
    # =====================================================

    def is_user_connected(
        self,
        user_id: int
    ):

        return bool(
            self.active_connections.get(
                user_id,
                []
            )
        )


    # =====================================================
    # GET CONNECTED USERS
    # =====================================================

    def get_connected_users(self):

        return list(
            self.active_connections.keys()
        )


# =========================================================
# GLOBAL MANAGER
# =========================================================

manager = ConnectionManager()


# =========================================================
# WEBSOCKET ENDPOINT
# =========================================================

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int
):

    await manager.connect(
        user_id,
        websocket
    )

    try:

        # -------------------------------------------------
        # CONNECTION CONFIRMATION
        # -------------------------------------------------

        await websocket.send_json({
            "event": "connected",
            "user_id": user_id,
            "message": "WebSocket connected successfully"
        })

        print(
            f"Connection confirmation sent to user {user_id}"
        )

        # -------------------------------------------------
        # KEEP CONNECTION ALIVE
        # -------------------------------------------------

        while True:

            data = await websocket.receive_text()

            print(
                f"WebSocket message received "
                f"from user {user_id}: {data}"
            )

    except WebSocketDisconnect:

        print(
            f"User {user_id} disconnected"
        )

        manager.disconnect(
            user_id,
            websocket
        )

    except Exception as e:

        print(
            f"WebSocket error for user {user_id}: {e}"
        )

        manager.disconnect(
            user_id,
            websocket
        )


# =========================================================
# ORDER STATUS UPDATE
# =========================================================

async def send_order_update(
    user_id: int,
    order_id: int,
    status: str
):

    message = {

        "event": "order_status_updated",

        "order_id": order_id,

        "status": status,

        "message":
            f"Your order #{order_id} is now {status}."
    }

    print()
    print("SENDING ORDER STATUS UPDATE")
    print(
        f"User={user_id}, "
        f"Order={order_id}, "
        f"Status={status}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# CART UPDATE
# =========================================================

async def send_cart_update(
    user_id: int,
    cart_id: int,
    action: str
):

    message = {

        "event": "cart_updated",

        "cart_id": cart_id,

        "action": action,

        "message":
            f"Your cart was {action}."
    }

    print()
    print("SENDING CART UPDATE")
    print(
        f"User={user_id}, "
        f"Cart={cart_id}, "
        f"Action={action}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# GENERAL NOTIFICATION
# =========================================================

async def send_notification(
    user_id: int,
    notification_type: str,
    message: str,
    notification_id: int | None = None
):

    notification_message = {

        "event": "notification",

        "notification_id": notification_id,

        "type": notification_type,

        "message": message
    }

    print()
    print("SENDING NOTIFICATION")
    print(
        f"User={user_id}, "
        f"Type={notification_type}, "
        f"Notification ID={notification_id}"
    )

    return await manager.send_to_user(
        user_id,
        notification_message
    )