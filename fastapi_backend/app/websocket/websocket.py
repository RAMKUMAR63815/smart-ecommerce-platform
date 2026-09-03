from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from typing import Dict, List


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    tags=["WebSocket"]
)


# =========================================================
# CONNECTION MANAGER
# =========================================================

class ConnectionManager:

    def __init__(self):

        # user_id -> list of WebSocket connections
        #
        # Example:
        #
        # {
        #     6: [websocket1],
        #     10: [websocket2, websocket3]
        # }
        #
        self.active_connections: Dict[
            int,
            List[WebSocket]
        ] = {}


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

        self.active_connections[user_id].append(
            websocket
        )

        print()
        print("=" * 70)
        print("WEBSOCKET CONNECTED")
        print("User ID:", user_id)
        print(
            "User connections:",
            len(
                self.active_connections[user_id]
            )
        )
        print(
            "Connected users:",
            list(
                self.active_connections.keys()
            )
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

        if user_id not in self.active_connections:
            return

        if websocket in self.active_connections[user_id]:

            self.active_connections[user_id].remove(
                websocket
            )

        if not self.active_connections[user_id]:

            del self.active_connections[user_id]

        print()
        print("=" * 70)
        print("WEBSOCKET DISCONNECTED")
        print("User ID:", user_id)
        print(
            "Remaining connected users:",
            list(
                self.active_connections.keys()
            )
        )
        print("=" * 70)
        print()


    # =====================================================
    # SEND MESSAGE TO USER
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
        print(
            "Connections found:",
            len(connections)
        )
        print(
            "Event:",
            message.get("event")
        )
        print(
            "Message:",
            message
        )
        print("=" * 70)

        # -------------------------------------------------
        # USER NOT CONNECTED
        # -------------------------------------------------

        if not connections:

            print(
                f"WARNING: No active WebSocket connection "
                f"for user {user_id}"
            )

            print(
                "Currently connected users:",
                list(
                    self.active_connections.keys()
                )
            )

            print()

            return False

        # -------------------------------------------------
        # SEND MESSAGE
        # -------------------------------------------------

        sent_successfully = False

        disconnected = []

        for websocket in list(connections):

            try:

                await websocket.send_json(
                    message
                )

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

                disconnected.append(
                    websocket
                )

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
    # BROADCAST TO ALL USERS
    # =====================================================

    async def broadcast(
        self,
        message: dict
    ):

        print()
        print("=" * 70)
        print("WEBSOCKET BROADCAST")
        print("Message:", message)
        print("=" * 70)

        for user_id in list(
            self.active_connections.keys()
        ):

            await self.send_to_user(
                user_id,
                message
            )


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
    # GET CONNECTION COUNT
    # =====================================================

    def get_user_connection_count(
        self,
        user_id: int
    ):

        return len(
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

            "message":
                "WebSocket connected successfully"

        })

        print(
            f"Connection confirmation sent "
            f"to user {user_id}"
        )

        # -------------------------------------------------
        # KEEP CONNECTION ALIVE
        # -------------------------------------------------

        while True:

            try:

                data = await websocket.receive_text()

                print(
                    f"WebSocket message received "
                    f"from user {user_id}: {data}"
                )

            except WebSocketDisconnect:

                raise


    # -----------------------------------------------------
    # NORMAL DISCONNECT
    # -----------------------------------------------------

    except WebSocketDisconnect:

        print(
            f"User {user_id} disconnected"
        )

        manager.disconnect(
            user_id,
            websocket
        )


    # -----------------------------------------------------
    # OTHER ERROR
    # -----------------------------------------------------

    except Exception as e:

        print(
            f"WebSocket error for user {user_id}: {e}"
        )

        manager.disconnect(
            user_id,
            websocket
        )


# =========================================================
# ORDER CREATED
# =========================================================

async def send_order_created(
    user_id: int,
    order_id: int
):

    message = {

        "event":
            "order_created",

        "order_id":
            order_id,

        "message":
            f"Your order #{order_id} "
            f"has been created successfully."

    }

    print()
    print("SENDING ORDER CREATED UPDATE")

    print(
        f"User={user_id}, "
        f"Order={order_id}"
    )

    return await manager.send_to_user(
        user_id,
        message
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

        "event":
            "order_status_updated",

        "order_id":
            order_id,

        "status":
            status,

        "message":
            f"Your order #{order_id} "
            f"is now {status}."

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
# ORDER CANCELLED
# =========================================================

async def send_order_cancelled(
    user_id: int,
    order_id: int
):

    message = {

        "event":
            "order_cancelled",

        "order_id":
            order_id,

        "status":
            "Cancelled",

        "message":
            f"Your order #{order_id} "
            f"has been cancelled."

    }

    print()
    print("SENDING ORDER CANCELLED UPDATE")

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
    action: str,
    product_id: int | None = None,
    quantity: int | None = None
):

    message = {

        "event":
            "cart_updated",

        "cart_id":
            cart_id,

        "product_id":
            product_id,

        "quantity":
            quantity,

        "action":
            action,

        "message":
            f"Your cart was {action}."

    }

    print()
    print("SENDING CART UPDATE")

    print(
        f"User={user_id}, "
        f"Cart={cart_id}, "
        f"Product={product_id}, "
        f"Quantity={quantity}, "
        f"Action={action}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# CART ITEM REMOVED
# =========================================================

async def send_cart_removed(
    user_id: int,
    cart_id: int,
    product_id: int
):

    message = {

        "event":
            "cart_item_removed",

        "cart_id":
            cart_id,

        "product_id":
            product_id,

        "action":
            "removed",

        "message":
            "Product was removed from your cart."

    }

    print()
    print("SENDING CART REMOVE UPDATE")

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# NOTIFICATION
# =========================================================

async def send_notification(
    user_id: int,
    notification_type: str,
    message: str,
    notification_id: int | None = None
):

    notification_message = {

        "event":
            "notification",

        "notification_id":
            notification_id,

        "type":
            notification_type,

        "message":
            message

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


# =========================================================
# RETURN REQUEST
# =========================================================

async def send_return_update(
    user_id: int,
    order_id: int,
    status: str,
    return_id: int | None = None
):

    message = {

        "event":
            "return_updated",

        "return_id":
            return_id,

        "order_id":
            order_id,

        "status":
            status,

        "message":
            f"Your return request for "
            f"order #{order_id} is {status}."

    }

    print()
    print("SENDING RETURN UPDATE")

    print(
        f"User={user_id}, "
        f"Order={order_id}, "
        f"Return ID={return_id}, "
        f"Return Status={status}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# RETURN APPROVED
# =========================================================

async def send_return_approved(
    user_id: int,
    order_id: int,
    return_id: int | None = None
):

    message = {

        "event":
            "return_approved",

        "return_id":
            return_id,

        "order_id":
            order_id,

        "status":
            "approved",

        "message":
            f"Your return request for "
            f"order #{order_id} has been approved."

    }

    print()
    print("SENDING RETURN APPROVED UPDATE")

    print(
        f"User={user_id}, "
        f"Order={order_id}, "
        f"Return ID={return_id}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# RETURN REJECTED
# =========================================================

async def send_return_rejected(
    user_id: int,
    order_id: int,
    return_id: int | None = None,
    reason: str | None = None
):

    message = {

        "event":
            "return_rejected",

        "return_id":
            return_id,

        "order_id":
            order_id,

        "status":
            "rejected",

        "reason":
            reason,

        "message":
            f"Your return request for "
            f"order #{order_id} has been rejected."

    }

    print()
    print("SENDING RETURN REJECTED UPDATE")

    print(
        f"User={user_id}, "
        f"Order={order_id}, "
        f"Return ID={return_id}, "
        f"Reason={reason}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# REFUND COMPLETED
# =========================================================

async def send_refund_completed(
    user_id: int,
    order_id: int,
    refund_amount: float | None = None,
    refund_id: str | None = None
):

    message = {

        "event":
            "refund_completed",

        "order_id":
            order_id,

        "payment_status":
            "Refunded",

        "refund_amount":
            refund_amount,

        "refund_id":
            refund_id,

        "message":
            (
                f"Refund for order #{order_id} "
                f"has been completed."
            )

    }

    print()
    print("SENDING REFUND COMPLETED UPDATE")

    print(
        f"User={user_id}, "
        f"Order={order_id}, "
        f"Refund Amount={refund_amount}, "
        f"Refund ID={refund_id}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# PAYMENT UPDATE
# =========================================================

async def send_payment_update(
    user_id: int,
    order_id: int,
    payment_status: str
):

    message = {

        "event":
            "payment_updated",

        "order_id":
            order_id,

        "payment_status":
            payment_status,

        "message":
            f"Payment for order #{order_id} "
            f"is {payment_status}."

    }

    print()
    print("SENDING PAYMENT UPDATE")

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# PAYMENT REFUNDED
# =========================================================

async def send_payment_refunded(
    user_id: int,
    order_id: int,
    refund_amount: float | None = None,
    refund_id: str | None = None
):

    message = {

        "event":
            "payment_refunded",

        "order_id":
            order_id,

        "payment_status":
            "Refunded",

        "refund_amount":
            refund_amount,

        "refund_id":
            refund_id,

        "message":
            (
                f"Payment refund for order "
                f"#{order_id} has been completed."
            )

    }

    print()
    print("SENDING PAYMENT REFUNDED UPDATE")

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# INVENTORY UPDATE
# =========================================================

async def send_inventory_update(
    user_id: int,
    product_id: int,
    stock: int,
    quantity_added: int | None = None
):

    message = {

        "event":
            "inventory_updated",

        "product_id":
            product_id,

        "stock":
            stock,

        "quantity_added":
            quantity_added,

        "message":
            (
                f"Inventory updated for "
                f"product #{product_id}."
            )

    }

    print()
    print("SENDING INVENTORY UPDATE")

    print(
        f"User={user_id}, "
        f"Product={product_id}, "
        f"Stock={stock}, "
        f"Quantity Added={quantity_added}"
    )

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# RETURN + REFUND COMPLETED
# =========================================================

async def send_return_refund_completed(
    user_id: int,
    order_id: int,
    return_id: int | None = None,
    refund_amount: float | None = None,
    refund_id: str | None = None
):

    message = {

        "event":
            "return_refund_completed",

        "return_id":
            return_id,

        "order_id":
            order_id,

        "return_status":
            "refunded",

        "order_status":
            "Returned",

        "payment_status":
            "Refunded",

        "refund_amount":
            refund_amount,

        "refund_id":
            refund_id,

        "message":
            (
                f"Return and refund for order "
                f"#{order_id} have been completed."
            )

    }

    print()
    print("=" * 70)
    print("SENDING RETURN + REFUND COMPLETED UPDATE")
    print(
        f"User={user_id}, "
        f"Order={order_id}, "
        f"Return ID={return_id}"
    )
    print(
        f"Refund Amount={refund_amount}, "
        f"Refund ID={refund_id}"
    )
    print("=" * 70)

    return await manager.send_to_user(
        user_id,
        message
    )


# =========================================================
# GENERIC REAL-TIME EVENT
# =========================================================

async def send_realtime_update(
    user_id: int,
    event: str,
    message: str,
    data: dict | None = None
):

    realtime_message = {

        "event":
            event,

        "message":
            message,

        "data":
            data or {}

    }

    return await manager.send_to_user(
        user_id,
        realtime_message
    )