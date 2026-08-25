import {
  useEffect,
  useRef,
} from "react";


const API_URL =
  "http://127.0.0.1:8000";


function NotificationListener({
  userId,
  onNotification,
  onExistingNotifications,
}) {

  const socketRef =
    useRef(null);

  const reconnectTimerRef =
    useRef(null);

  const manuallyClosedRef =
    useRef(false);

  const connectingRef =
    useRef(false);


  // =====================================================
  // LOAD DATABASE NOTIFICATIONS
  // =====================================================

  useEffect(() => {

    if (!userId) {

      console.warn(
        "NotificationListener: No user ID"
      );

      return;
    }


    let cancelled =
      false;


    const loadNotifications =
      async () => {

        try {

          console.log(
            "Loading existing notifications for user:",
            userId
          );


          const response =
            await fetch(
              `${API_URL}/notifications/?user_id=${userId}`
            );


          if (!response.ok) {

            console.error(
              "Failed to load notifications:",
              response.status
            );

            return;
          }


          const data =
            await response.json();


          if (!cancelled) {

            console.log(
              "Existing notifications:",
              data
            );


            onExistingNotifications(
              data
            );

          }

        }
        catch (error) {

          console.error(
            "Notification loading error:",
            error
          );

        }

      };


    loadNotifications();


    return () => {

      cancelled = true;

    };

  }, [
    userId,
    onExistingNotifications,
  ]);


  // =====================================================
  // WEBSOCKET
  // =====================================================

  useEffect(() => {

    if (!userId) {
      return;
    }


    manuallyClosedRef.current =
      false;


    const connect = () => {

      // Prevent multiple connections
      if (
        connectingRef.current ||
        (
          socketRef.current &&
          (
            socketRef.current.readyState ===
              WebSocket.OPEN ||
            socketRef.current.readyState ===
              WebSocket.CONNECTING
          )
        )
      ) {

        return;

      }


      connectingRef.current =
        true;


      const url =
        `ws://127.0.0.1:8000/ws/${userId}`;


      console.log(
        "Connecting Notification WebSocket:",
        url
      );


      const socket =
        new WebSocket(url);


      socketRef.current =
        socket;


      socket.onopen = () => {

        connectingRef.current =
          false;


        console.log(
          "Notification WebSocket connected"
        );

      };


      socket.onmessage = (event) => {

        try {

          const data =
            JSON.parse(
              event.data
            );


          console.log(
            "Notification received:",
            data
          );


          onNotification(data);

        }
        catch (error) {

          console.error(
            "Invalid WebSocket message:",
            error
          );

        }

      };


      socket.onerror = (error) => {

        console.error(
          "Notification WebSocket error:",
          error
        );

      };


      socket.onclose = () => {

        connectingRef.current =
          false;


        console.log(
          "Notification WebSocket disconnected"
        );


        socketRef.current =
          null;


        if (
          !manuallyClosedRef.current
        ) {

          clearTimeout(
            reconnectTimerRef.current
          );


          reconnectTimerRef.current =
            setTimeout(
              connect,
              3000
            );

        }

      };

    };


    connect();


    // ===================================================
    // CLEANUP
    // ===================================================

    return () => {

      manuallyClosedRef.current =
        true;


      clearTimeout(
        reconnectTimerRef.current
      );


      connectingRef.current =
        false;


      if (socketRef.current) {

        console.log(
          "Cleaning Notification WebSocket"
        );


        socketRef.current.close();


        socketRef.current =
          null;

      }

    };

  }, [
    userId,
    onNotification,
  ]);


  return null;
}


export default NotificationListener;