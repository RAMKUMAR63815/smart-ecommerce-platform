
import React, { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function NotificationUI({
  notifications = [],
  onClose,
  onClear
}) {

  const [isOpen, setIsOpen] = useState(false);

  const [loadingId, setLoadingId] =
    useState(null);


  // =====================================================
  // UNREAD COUNT
  // =====================================================

  const unreadCount =
    notifications.filter(
      (notification) =>
        notification.read_status !== true
    ).length;


  // =====================================================
  // MARK NOTIFICATION AS READ
  // =====================================================

  const markAsRead = async (notification) => {

    // Cart and order-status notifications may not
    // have a database notification ID.
    if (!notification.notification_id) {

      console.log(
        "No database notification ID:",
        notification.id
      );

      onClose(notification.id);

      return;
    }


    try {

      setLoadingId(
        notification.notification_id
      );


      const response = await fetch(
        `${API_URL}/notifications/read`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            notification_id:
              notification.notification_id
          })
        }
      );


      if (!response.ok) {

        const errorText =
          await response.text();

        console.error(
          "Mark notification read failed:",
          response.status,
          errorText
        );

        return;
      }


      console.log(
        "Notification marked as read:",
        notification.notification_id
      );


      // Remove from popup after reading
      onClose(notification.id);

    } catch (error) {

      console.error(
        "Error marking notification as read:",
        error
      );

    } finally {

      setLoadingId(null);

    }

  };


  // =====================================================
  // MARK ALL DATABASE NOTIFICATIONS AS READ
  // =====================================================

  const markAllAsRead = async () => {

    const unreadNotifications =
      notifications.filter(
        (notification) =>
          notification.read_status !== true &&
          notification.notification_id
      );


    for (
      const notification
      of unreadNotifications
    ) {

      try {

        await fetch(
          `${API_URL}/notifications/read`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
              notification_id:
                notification.notification_id
            })
          }
        );

      } catch (error) {

        console.error(
          "Error marking notification as read:",
          error
        );

      }

    }


    // Clear the visible notifications
    onClear();

  };


  // =====================================================
  // NOTIFICATION ICON
  // =====================================================

  const getIcon = (type) => {

    switch (type) {

      case "payment":
        return "💳";

      case "order":
        return "📦";

      case "cart":
        return "🛒";

      default:
        return "🔔";

    }

  };


  // =====================================================
  // NOTIFICATION TITLE
  // =====================================================

  const getTitle = (type) => {

    switch (type) {

      case "payment":
        return "Payment Notification";

      case "order":
        return "Order Update";

      case "cart":
        return "Cart Updated";

      default:
        return "Notification";

    }

  };


  // =====================================================
  // DATE FORMAT
  // =====================================================

  const formatDate = (timestamp) => {

    if (!timestamp) {
      return "";
    }


    try {

      return new Date(
        timestamp
      ).toLocaleString();

    } catch {

      return "";

    }

  };


  // =====================================================
  // UI
  // =====================================================

  return (

    <>

      {/* =================================================
          NOTIFICATION BELL
          ================================================= */}

      <div
        style={{
          position: "fixed",
          top: "20px",
          right: "25px",
          zIndex: 9999
        }}
      >

        <button
          onClick={() =>
            setIsOpen(
              (previous) =>
                !previous
            )
          }

          style={{
            width: "52px",
            height: "52px",
            borderRadius: "50%",
            border: "none",
            background: "#2563eb",
            color: "white",
            fontSize: "24px",
            cursor: "pointer",
            position: "relative",
            boxShadow:
              "0 4px 12px rgba(0,0,0,0.2)"
          }}
        >

          🔔


          {/* UNREAD BADGE */}

          {unreadCount > 0 && (

            <span
              style={{
                position: "absolute",
                top: "-5px",
                right: "-5px",
                background: "#ef4444",
                color: "white",
                borderRadius: "50%",
                minWidth: "22px",
                height: "22px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "12px",
                fontWeight: "bold",
                padding: "2px"
              }}
            >

              {unreadCount > 99
                ? "99+"
                : unreadCount}

            </span>

          )}

        </button>


        {/* =================================================
            NOTIFICATION PANEL
            ================================================= */}

        {isOpen && (

          <div
            style={{
              position: "absolute",
              top: "62px",
              right: "0",
              width: "380px",
              maxHeight: "600px",
              background: "white",
              borderRadius: "12px",
              boxShadow:
                "0 8px 30px rgba(0,0,0,0.2)",
              overflow: "hidden",
              border:
                "1px solid #e5e7eb"
            }}
          >

            {/* HEADER */}

            <div
              style={{
                padding: "16px",
                borderBottom:
                  "1px solid #e5e7eb",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between"
              }}
            >

              <div>

                <h3
                  style={{
                    margin: 0,
                    fontSize: "18px"
                  }}
                >
                  Notifications
                </h3>

                <small
                  style={{
                    color: "#6b7280"
                  }}
                >
                  {unreadCount} unread
                </small>

              </div>


              {unreadCount > 0 && (

                <button
                  onClick={
                    markAllAsRead
                  }

                  style={{
                    border: "none",
                    background: "none",
                    color: "#2563eb",
                    cursor: "pointer",
                    fontSize: "13px"
                  }}
                >
                  Mark all read
                </button>

              )}

            </div>


            {/* =================================================
                EMPTY
                ================================================= */}

            {notifications.length === 0 ? (

              <div
                style={{
                  padding: "40px 20px",
                  textAlign: "center",
                  color: "#6b7280"
                }}
              >

                <div
                  style={{
                    fontSize: "40px",
                    marginBottom: "10px"
                  }}
                >
                  🔕
                </div>

                <p>
                  No notifications
                </p>

              </div>

            ) : (

              <div
                style={{
                  maxHeight: "480px",
                  overflowY: "auto"
                }}
              >

                {notifications.map(
                  (notification) => (

                    <div
                      key={
                        notification.id
                      }

                      style={{
                        padding: "15px",
                        borderBottom:
                          "1px solid #f1f5f9",

                        background:
                          notification.read_status
                            ? "white"
                            : "#eff6ff",

                        display: "flex",
                        gap: "12px"
                      }}
                    >

                      {/* ICON */}

                      <div
                        style={{
                          fontSize: "25px"
                        }}
                      >

                        {getIcon(
                          notification.type
                        )}

                      </div>


                      {/* CONTENT */}

                      <div
                        style={{
                          flex: 1
                        }}
                      >

                        <div
                          style={{
                            fontWeight: "600",
                            marginBottom: "5px"
                          }}
                        >

                          {getTitle(
                            notification.type
                          )}

                        </div>


                        <div
                          style={{
                            fontSize: "14px",
                            color: "#374151",
                            marginBottom: "6px"
                          }}
                        >

                          {
                            notification.message
                          }

                        </div>


                        {notification.timestamp && (

                          <div
                            style={{
                              fontSize: "11px",
                              color: "#9ca3af"
                            }}
                          >

                            {formatDate(
                              notification.timestamp
                            )}

                          </div>

                        )}


                        {/* MARK READ */}

                        {!notification.read_status &&
                          notification.notification_id && (

                            <button
                              onClick={() =>
                                markAsRead(
                                  notification
                                )
                              }

                              disabled={
                                loadingId ===
                                notification.notification_id
                              }

                              style={{
                                marginTop: "8px",
                                border: "none",
                                background:
                                  "#2563eb",
                                color: "white",
                                padding:
                                  "6px 10px",
                                borderRadius:
                                  "6px",
                                cursor:
                                  "pointer",
                                fontSize:
                                  "12px"
                              }}
                            >

                              {loadingId ===
                              notification.notification_id
                                ? "Saving..."
                                : "Mark as read"}

                            </button>

                          )}

                      </div>


                      {/* CLOSE */}

                      <button
                        onClick={() =>
                          onClose(
                            notification.id
                          )
                        }

                        style={{
                          border: "none",
                          background: "none",
                          color: "#9ca3af",
                          cursor: "pointer",
                          fontSize: "18px",
                          alignSelf: "flex-start"
                        }}
                      >
                        ×
                      </button>

                    </div>

                  )
                )}

              </div>

            )}


            {/* FOOTER */}

            {notifications.length > 0 && (

              <div
                style={{
                  padding: "10px",
                  borderTop:
                    "1px solid #e5e7eb",
                  textAlign: "center"
                }}
              >

                <button
                  onClick={onClear}

                  style={{
                    border: "none",
                    background: "none",
                    color: "#ef4444",
                    cursor: "pointer"
                  }}
                >
                  Clear notifications
                </button>

              </div>

            )}

          </div>

        )}

      </div>

    </>

  );

}

export default NotificationUI;

