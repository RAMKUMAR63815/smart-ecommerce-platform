import React, {
  useEffect,
  useRef
} from "react";


function NotificationListener({
  userId,
  onNotification
}) {

  const socketRef = useRef(null);

  const reconnectTimerRef =
    useRef(null);


  useEffect(() => {

    if (!userId) {

      console.log(
        "NotificationListener: No user ID"
      );

      return;
    }


    let shouldReconnect = true;


    const connectWebSocket = () => {

      if (!shouldReconnect) {
        return;
      }


      // -------------------------------------------------
      // DON'T CREATE DUPLICATE SOCKET
      // -------------------------------------------------

      if (
        socketRef.current &&
        (
          socketRef.current.readyState ===
            WebSocket.OPEN ||
          socketRef.current.readyState ===
            WebSocket.CONNECTING
        )
      ) {

        console.log(
          "Notification WebSocket already active"
        );

        return;
      }


      const wsUrl =
        `ws://127.0.0.1:8000/ws/${userId}`;


      console.log(
        "Connecting Notification WebSocket:",
        wsUrl
      );


      const ws =
        new WebSocket(wsUrl);


      socketRef.current = ws;


      // =================================================
      // OPEN
      // =================================================

      ws.onopen = () => {

        console.log(
          "Notification WebSocket connected"
        );

      };


      // =================================================
      // MESSAGE
      // =================================================

      ws.onmessage = (event) => {

        try {

          const data =
            JSON.parse(event.data);


          console.log(
            "Notification received:",
            data
          );


          // ------------------------------------------------
          // CONNECTION CONFIRMATION
          // ------------------------------------------------

          if (
            data.event === "connected"
          ) {

            console.log(
              "WebSocket connection confirmed"
            );

            return;
          }


          // ------------------------------------------------
          // SEND TO APP
          // ------------------------------------------------

          if (onNotification) {

            onNotification(data);

          }

        } catch (error) {

          console.error(
            "Invalid WebSocket message:",
            event.data,
            error
          );

        }

      };


      // =================================================
      // ERROR
      // =================================================

      ws.onerror = (error) => {

        console.error(
          "Notification WebSocket error:",
          error
        );

      };


      // =================================================
      // CLOSE
      // =================================================

      ws.onclose = () => {

        console.log(
          "Notification WebSocket disconnected"
        );


        if (
          socketRef.current === ws
        ) {

          socketRef.current = null;

        }


        if (!shouldReconnect) {
          return;
        }


        console.log(
          "Reconnecting Notification WebSocket..."
        );


        reconnectTimerRef.current =
          setTimeout(
            connectWebSocket,
            3000
          );

      };

    };


    // =================================================
    // CONNECT
    // =================================================

    connectWebSocket();


    // =================================================
    // CLEANUP
    // =================================================

    return () => {

      console.log(
        "Cleaning Notification WebSocket"
      );


      shouldReconnect = false;


      if (
        reconnectTimerRef.current
      ) {

        clearTimeout(
          reconnectTimerRef.current
        );

        reconnectTimerRef.current =
          null;

      }


      const ws =
        socketRef.current;


      socketRef.current =
        null;


      if (ws) {

        ws.onopen = null;

        ws.onmessage = null;

        ws.onerror = null;

        ws.onclose = null;


        if (
          ws.readyState ===
            WebSocket.OPEN ||
          ws.readyState ===
            WebSocket.CONNECTING
        ) {

          ws.close();

        }

      }

    };

  }, [
    userId,
    onNotification
  ]);


  return null;
}


export default NotificationListener;