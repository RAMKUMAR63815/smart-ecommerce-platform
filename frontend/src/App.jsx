import React, {
  useCallback,
  useState
} from "react";

import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Products from "./pages/Products";
import Cart from "./pages/Cart";
import Orders from "./pages/Orders";
import Dashboard from "./pages/Dashboard";
import OrderDetails from "./pages/OrderDetails";
import Payment from "./pages/Payment";
import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentCancelled from "./pages/PaymentCancelled";

import NotificationListener from "./components/NotificationListener";
import NotificationUI from "./components/NotificationUI";


function App() {

  // =====================================================
  // LOGGED-IN USER
  // =====================================================

  // TEMPORARY TEST USER
  // Current testing user is 6.
  //
  // Later replace this with the actual
  // logged-in user ID from localStorage / JWT.

  const userId = 6;


  // =====================================================
  // NOTIFICATIONS STATE
  // =====================================================

  const [notifications, setNotifications] =
    useState([]);


  // =====================================================
  // RECEIVE NOTIFICATION
  // =====================================================

  const handleNotification = useCallback(
    (data) => {

      console.log(
        "APP RECEIVED NOTIFICATION:",
        data
      );


      // =================================================
      // CONNECTION CONFIRMATION
      // =================================================

      if (
        data.event === "connected"
      ) {

        console.log(
          "WebSocket connection confirmed"
        );

        return;
      }


      // =================================================
      // DATABASE / PAYMENT / ORDER NOTIFICATION
      // =================================================

      if (
        data.event === "notification"
      ) {

        const notificationId =
          data.notification_id;


        setNotifications(
          (previous) => {

            // -------------------------------------------
            // PREVENT DUPLICATES
            // -------------------------------------------

            if (
              notificationId &&
              previous.some(
                (notification) =>
                  notification.id ===
                  notificationId
              )
            ) {

              console.log(
                "Duplicate notification ignored:",
                notificationId
              );

              return previous;
            }


            return [
              ...previous,

              {
                id:
                  notificationId ||
                  `notification-${Date.now()}`,

                type:
                  data.type ||
                  "notification",

                message:
                  data.message ||
                  "You have a new notification.",

                notification_id:
                  notificationId,

                order_id:
                  data.order_id,

                timestamp:
                  data.timestamp ||
                  new Date().toISOString(),

                read_status:
                  data.read_status ?? false
              }
            ];

          }
        );

        return;
      }


      // =================================================
      // CART UPDATED
      // =================================================

      if (
        data.event === "cart_updated"
      ) {

        setNotifications(
          (previous) => [

            ...previous,

            {
              id:
                `cart-${data.cart_id}-${Date.now()}`,

              type:
                "cart",

              message:
                data.message ||
                "Your cart was updated.",

              cart_id:
                data.cart_id,

              action:
                data.action,

              timestamp:
                data.timestamp ||
                new Date().toISOString(),

              read_status:
                false
            }

          ]
        );

        return;
      }


      // =================================================
      // ORDER STATUS UPDATED
      // =================================================

      if (
        data.event ===
        "order_status_updated"
      ) {

        setNotifications(
          (previous) => [

            ...previous,

            {
              id:
                `order-${data.order_id}-${Date.now()}`,

              type:
                "order",

              message:
                data.message ||
                "Your order status was updated.",

              order_id:
                data.order_id,

              status:
                data.status,

              timestamp:
                data.timestamp ||
                new Date().toISOString(),

              read_status:
                false
            }

          ]
        );

        return;
      }


      // =================================================
      // UNKNOWN EVENT
      // =================================================

      console.log(
        "Unhandled notification event:",
        data
      );

    },
    []
  );


  // =====================================================
  // CLOSE ONE NOTIFICATION
  // =====================================================

  const closeNotification = useCallback(
    (id) => {

      setNotifications(
        (previous) =>
          previous.filter(
            (notification) =>
              notification.id !== id
          )
      );

    },
    []
  );


  // =====================================================
  // CLEAR ALL NOTIFICATIONS
  // =====================================================

  const clearNotifications = useCallback(
    () => {

      setNotifications([]);

    },
    []
  );


  // =====================================================
  // APP
  // =====================================================

  return (

    <BrowserRouter>

      {/* =================================================
          WEBSOCKET NOTIFICATION LISTENER
          ================================================= */}

      <NotificationListener
        userId={userId}
        onNotification={
          handleNotification
        }
      />


      {/* =================================================
          NOTIFICATION UI
          ================================================= */}

      <NotificationUI
        notifications={
          notifications
        }
        onClose={
          closeNotification
        }
        onClear={
          clearNotifications
        }
      />


      {/* =================================================
          ROUTES
          ================================================= */}

      <Routes>

        {/* =================================================
            LOGIN
            ================================================= */}

        <Route
          path="/"
          element={
            <Login />
          }
        />

        <Route
          path="/login"
          element={
            <Login />
          }
        />


        {/* =================================================
            REGISTER
            ================================================= */}

        <Route
          path="/register"
          element={
            <Register />
          }
        />


        {/* =================================================
            PRODUCTS
            ================================================= */}

        <Route
          path="/products"
          element={
            <Products />
          }
        />


        {/* =================================================
            CART
            ================================================= */}

        <Route
          path="/cart"
          element={
            <Cart />
          }
        />


        {/* =================================================
            ORDERS
            ================================================= */}

        <Route
          path="/orders"
          element={
            <Orders />
          }
        />

        <Route
          path="/orders/:orderId"
          element={
            <OrderDetails />
          }
        />


        {/* =================================================
            PAYMENT
            ================================================= */}

        <Route
          path="/payment/:orderId"
          element={
            <Payment />
          }
        />

        <Route
          path="/payment-success"
          element={
            <PaymentSuccess />
          }
        />

        <Route
          path="/payment-cancelled"
          element={
            <PaymentCancelled />
          }
        />


        {/* =================================================
            DASHBOARD
            ================================================= */}

        <Route
          path="/dashboard"
          element={
            <Dashboard />
          }
        />

      </Routes>

    </BrowserRouter>

  );
}


export default App;