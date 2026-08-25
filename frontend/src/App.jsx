import { useCallback, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Products from "./pages/Products";
import Cart from "./pages/Cart";
import Orders from "./pages/Orders";

import NotificationListener from "./components/NotificationListener";
import NotificationUI from "./components/NotificationUI";

function App() {
  const userId = 6;

  const [notifications, setNotifications] = useState([]);
  const [popupNotifications, setPopupNotifications] = useState([]);

  // Load notifications from database
  const handleExistingNotifications = useCallback((data) => {
    if (!Array.isArray(data)) return;

    const unread = data
      .filter((item) => !item.read_status)
      .map((item) => ({
        id: item.id,
        databaseId: item.id,
        type: item.type || "notification",
        message: item.message,
        timestamp: item.timestamp,
        read_status: item.read_status,
      }));

    setNotifications(unread);
  }, []);

  // WebSocket notifications
  const handleNotification = useCallback((data) => {
    if (data.event === "connected") return;

    if (data.event === "notification") {
      const notificationId =
        data.notification_id || data.id;

      setNotifications((prev) => {
        const exists = prev.some(
          (n) => n.id === notificationId
        );

        if (exists) return prev;

        return [
          {
            id: notificationId,
            databaseId: notificationId,
            type: data.type || "notification",
            message: data.message,
            timestamp: data.timestamp,
            read_status: false,
          },
          ...prev,
        ];
      });

      setPopupNotifications((prev) => [
        ...prev,
        {
          id: `popup-${notificationId}`,
          type: data.type,
          message: data.message,
          timestamp: data.timestamp,
        },
      ]);
    }
  }, []);

  // Mark one notification read
  const markAsRead = useCallback(
    async (notificationId) => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/notifications/read?notification_id=${notificationId}`,
          {
            method: "POST",
          }
        );

        if (!response.ok) {
          console.error("Failed");
          return;
        }

        setNotifications((prev) =>
          prev.filter(
            (n) => n.id !== notificationId
          )
        );
      } catch (err) {
        console.error(err);
      }
    },
    []
  );

  // Mark all read
  const markAllAsRead = useCallback(async () => {
    for (const notification of notifications) {
      await markAsRead(notification.id);
    }
  }, [notifications, markAsRead]);

  // Close popup
  const closePopup = useCallback((id) => {
    setPopupNotifications((prev) =>
      prev.filter((p) => p.id !== id)
    );
  }, []);

  const clearPopups = useCallback(() => {
    setPopupNotifications([]);
  }, []);

  return (
    <BrowserRouter>

      <NotificationListener
        userId={userId}
        onNotification={handleNotification}
        onExistingNotifications={
          handleExistingNotifications
        }
      />

      <NotificationUI
        notifications={notifications}
        popupNotifications={popupNotifications}
        onMarkAsRead={markAsRead}
        onMarkAllAsRead={markAllAsRead}
        onClosePopup={closePopup}
        onClearPopups={clearPopups}
      />

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/products" element={<Products />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/orders" element={<Orders />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;