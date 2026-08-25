import {
  useEffect,
  useMemo,
  useState,
} from "react";


function NotificationUI({
  notifications,
  popupNotifications,
  onMarkAsRead,
  onMarkAllAsRead,
  onClosePopup,
  onClearPopups,
}) {

  const [open, setOpen] =
    useState(true);


  // =====================================================
  // UNREAD DATABASE NOTIFICATIONS
  // =====================================================

  const unreadCount =
    useMemo(
      () =>
        notifications.filter(
          (notification) =>
            !notification.read_status
        ).length,
      [notifications]
    );


  // =====================================================
  // AUTO CLOSE POPUPS
  // =====================================================

  useEffect(() => {

    if (
      popupNotifications.length ===
      0
    ) {
      return;
    }


    const timers =
      popupNotifications.map(
        (notification) =>
          setTimeout(
            () => {

              onClosePopup(
                notification.id
              );

            },
            5000
          )
      );


    return () => {

      timers.forEach(
        (timer) =>
          clearTimeout(timer)
      );

    };

  }, [
    popupNotifications,
    onClosePopup,
  ]);


  // =====================================================
  // ICON
  // =====================================================

  const getIcon =
    (type) => {

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
  // TITLE
  // =====================================================

  const getTitle =
    (type) => {

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
  // DATE
  // =====================================================

  const formatDate =
    (timestamp) => {

      if (!timestamp) {
        return "";
      }


      const date =
        new Date(timestamp);


      if (
        Number.isNaN(
          date.getTime()
        )
      ) {
        return "";
      }


      return date.toLocaleString();

    };


  return (

    <>

      {/* =================================================
          REAL-TIME POPUPS
          ================================================= */}

      <div
        style={{
          position:
            "fixed",

          top:
            "20px",

          right:
            "20px",

          width:
            "360px",

          zIndex:
            99999,

          display:
            "flex",

          flexDirection:
            "column",

          gap:
            "10px",
        }}
      >

        {popupNotifications.map(
          (notification) => (

            <div
              key={
                notification.id
              }
              style={{
                background:
                  "#fff",

                border:
                  "1px solid #ddd",

                borderRadius:
                  "12px",

                padding:
                  "15px",

                boxShadow:
                  "0 6px 20px rgba(0,0,0,0.2)",
              }}
            >

              <div
                style={{
                  display:
                    "flex",

                  alignItems:
                    "flex-start",

                  gap:
                    "10px",
                }}
              >

                <span
                  style={{
                    fontSize:
                      "25px",
                  }}
                >
                  {getIcon(
                    notification.type
                  )}
                </span>


                <div
                  style={{
                    flex:
                      1,
                  }}
                >

                  <strong>
                    {getTitle(
                      notification.type
                    )}
                  </strong>


                  <div
                    style={{
                      marginTop:
                        "5px",
                    }}
                  >
                    {
                      notification.message
                    }
                  </div>


                  <div
                    style={{
                      marginTop:
                        "5px",

                      fontSize:
                        "12px",

                      color:
                        "#777",
                    }}
                  >
                    {
                      formatDate(
                        notification.timestamp
                      )
                    }
                  </div>

                </div>


                <button
                  onClick={() =>
                    onClosePopup(
                      notification.id
                    )
                  }
                  style={{
                    border:
                      "none",

                    background:
                      "transparent",

                    fontSize:
                      "20px",

                    cursor:
                      "pointer",
                  }}
                >
                  ×
                </button>

              </div>

            </div>

          )
        )}

      </div>


      {/* =================================================
          NOTIFICATION PANEL
          ================================================= */}

      <div
        style={{
          position:
            "fixed",

          bottom:
            "20px",

          right:
            "20px",

          width:
            "430px",

          maxHeight:
            "650px",

          background:
            "#fff",

          border:
            "1px solid #ddd",

          borderRadius:
            "14px",

          boxShadow:
            "0 8px 30px rgba(0,0,0,0.2)",

          zIndex:
            9999,

          overflow:
            "hidden",
        }}
      >

        {/* HEADER */}

        <div
          style={{
            padding:
              "15px",

            display:
              "flex",

            justifyContent:
              "space-between",

            alignItems:
              "center",

            borderBottom:
              "1px solid #eee",
          }}
        >

          <div>

            <strong
              style={{
                fontSize:
                  "18px",
              }}
            >
              🔔 Notifications
            </strong>


            {unreadCount > 0 && (

              <span
                style={{
                  marginLeft:
                    "8px",

                  background:
                    "#dc3545",

                  color:
                    "#fff",

                  borderRadius:
                    "20px",

                  padding:
                    "3px 8px",

                  fontSize:
                    "12px",
                }}
              >
                {unreadCount}
              </span>

            )}

          </div>


          <button
            onClick={() =>
              setOpen(
                !open
              )
            }
            style={{
              border:
                "none",

              background:
                "transparent",

              cursor:
                "pointer",

              fontSize:
                "18px",
            }}
          >
            {open ? "▼" : "▲"}
          </button>

        </div>


        {open && (

          <>

            {/* ACTIONS */}

            <div
              style={{
                padding:
                  "10px 15px",

                display:
                  "flex",

                justifyContent:
                  "flex-end",

                borderBottom:
                  "1px solid #eee",
              }}
            >

              {unreadCount > 0 && (

                <button
                  onClick={
                    onMarkAllAsRead
                  }
                  style={{
                    border:
                      "none",

                    background:
                      "#198754",

                    color:
                      "#fff",

                    padding:
                      "8px 12px",

                    borderRadius:
                      "6px",

                    cursor:
                      "pointer",
                  }}
                >
                  Mark all read
                </button>

              )}

            </div>


            {/* DATABASE NOTIFICATIONS */}

            <div
              style={{
                maxHeight:
                  "530px",

                overflowY:
                  "auto",
              }}
            >

              {notifications.length ===
              0 ? (

                <div
                  style={{
                    padding:
                      "30px",

                    textAlign:
                      "center",

                    color:
                      "#777",
                  }}
                >
                  No notifications
                </div>

              ) : (

                notifications.map(
                  (notification) => (

                    <div
                      key={
                        notification.databaseId
                      }
                      style={{
                        padding:
                          "15px",

                        borderBottom:
                          "1px solid #eee",

                        background:
                          notification.read_status
                            ? "#fff"
                            : "#f5f9ff",
                      }}
                    >

                      <div
                        style={{
                          display:
                            "flex",

                          gap:
                            "10px",
                        }}
                      >

                        <div
                          style={{
                            fontSize:
                              "25px",
                          }}
                        >
                          {getIcon(
                            notification.type
                          )}
                        </div>


                        <div
                          style={{
                            flex:
                              1,
                          }}
                        >

                          <strong>
                            {getTitle(
                              notification.type
                            )}
                          </strong>


                          <div
                            style={{
                              marginTop:
                                "5px",
                            }}
                          >
                            {
                              notification.message
                            }
                          </div>


                          <div
                            style={{
                              marginTop:
                                "7px",

                              color:
                                "#777",

                              fontSize:
                                "12px",
                            }}
                          >
                            {
                              formatDate(
                                notification.timestamp
                              )
                            }
                          </div>


                          {!notification.read_status && (

                            <button
                              onClick={() =>
                                onMarkAsRead(
                                  notification.databaseId
                                )
                              }
                              style={{
                                marginTop:
                                  "10px",

                                border:
                                  "none",

                                background:
                                  "#0d6efd",

                                color:
                                  "#fff",

                                padding:
                                  "6px 10px",

                                borderRadius:
                                  "6px",

                                cursor:
                                  "pointer",
                              }}
                            >
                              Mark as read
                            </button>

                          )}

                        </div>

                      </div>

                    </div>

                  )
                )

              )}

            </div>

          </>

        )}

      </div>

    </>

  );

}


export default NotificationUI;