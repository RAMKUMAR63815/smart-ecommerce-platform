from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Notification, User
from app.services.email_service import send_email

from app.websocket.websocket import send_notification


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ==========================================
# GET ALL NOTIFICATIONS FOR A USER
# ==========================================

@router.get("/")
def get_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.timestamp.desc())
        .all()
    )

    return notifications


# ==========================================
# CREATE NOTIFICATION
# + SAVE DATABASE
# + SEND EMAIL
# + SEND WEBSOCKET
# ==========================================

@router.post("/")
async def create_notification(
    user_id: int,
    type: str,
    message: str,
    db: Session = Depends(get_db)
):

    # Check user
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # ==========================================
    # CREATE DATABASE NOTIFICATION
    # ==========================================

    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        read_status=False
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)


    # ==========================================
    # SEND EMAIL
    # ==========================================

    email_sent = False

    try:

        send_email(
            to_email=user.email,
            subject=f"Smart Ecommerce - {type}",
            body=message
        )

        email_sent = True

    except Exception as e:

        print(
            "Email sending failed:",
            e
        )


    # ==========================================
    # SEND REAL-TIME WEBSOCKET NOTIFICATION
    # ==========================================

    websocket_sent = False

    try:

        await send_notification(
            user_id=user_id,
            notification_type=type,
            message=message,
            notification_id=notification.id
        )

        websocket_sent = True

    except Exception as e:

        print(
            "WebSocket notification failed:",
            e
        )


    # ==========================================
    # RESPONSE
    # ==========================================

    return {

        "message": "Notification created successfully",

        "notification": {

            "id": notification.id,

            "user_id": notification.user_id,

            "type": notification.type,

            "message": notification.message,

            "read_status": notification.read_status,

            "timestamp": notification.timestamp

        },

        "email_sent": email_sent,

        "websocket_sent": websocket_sent

    }


# ==========================================
# MARK NOTIFICATION AS READ
# ==========================================

@router.post("/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):

    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if notification is None:

        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.read_status = True

    db.commit()

    db.refresh(notification)

    return {

        "message": "Notification marked as read",

        "notification_id": notification.id

    }