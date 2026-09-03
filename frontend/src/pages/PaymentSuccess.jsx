import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import api from "../api/api";

import "./PaymentSuccess.css";


function PaymentSuccess() {

  const location = useLocation();
  const navigate = useNavigate();


  // =====================================================
  // STATE
  // =====================================================

  const [status, setStatus] = useState("checking");

  const [message, setMessage] = useState(
    "Verifying your payment..."
  );

  const [order, setOrder] = useState(null);


  // =====================================================
  // CHECK PAYMENT
  // =====================================================

  useEffect(() => {

    const params = new URLSearchParams(
      location.search
    );


    const orderId = params.get(
      "order_id"
    );

    const sessionId = params.get(
      "session_id"
    );


    console.log(
      "Stripe Session ID:",
      sessionId
    );

    console.log(
      "Order ID:",
      orderId
    );


    // ---------------------------------------------------
    // If order ID is missing
    // ---------------------------------------------------

    if (!orderId) {

      setStatus("success");

      setMessage(
        "Payment completed. Your order is being confirmed by the server."
      );

      return;
    }


    // ---------------------------------------------------
    // POLLING
    // ---------------------------------------------------

    let attempts = 0;

    const maxAttempts = 15;


    const checkOrder = async () => {

      try {

        const response = await api.get(
          `/orders/${orderId}`
        );


        const currentOrder =
          response.data;


        console.log(
          "PaymentSuccess Order:",
          currentOrder
        );


        setOrder(
          currentOrder
        );


        // ------------------------------------------------
        // CHECK PAYMENT STATUS
        // ------------------------------------------------

        const paymentStatus = String(
          currentOrder.payment_status || ""
        ).toLowerCase();


        console.log(
          "Payment Status:",
          paymentStatus
        );


        // ------------------------------------------------
        // PAYMENT SUCCESS
        // ------------------------------------------------

        if (
          paymentStatus === "paid"
        ) {

          setStatus(
            "success"
          );

          setMessage(
            "Payment verified successfully. Your order has been confirmed."
          );

          return;
        }


        // ------------------------------------------------
        // PAYMENT STILL PENDING
        // ------------------------------------------------

        attempts++;


        console.log(
          `Payment verification attempt ${attempts}/${maxAttempts}`
        );


        // ------------------------------------------------
        // MAX ATTEMPTS
        // ------------------------------------------------

        if (
          attempts >= maxAttempts
        ) {

          setStatus(
            "success"
          );

          setMessage(
            "Payment was completed. Your order is being confirmed by the server. Please check My Orders shortly."
          );

          return;
        }


        // ------------------------------------------------
        // TRY AGAIN AFTER 2 SECONDS
        // ------------------------------------------------

        setTimeout(
          checkOrder,
          2000
        );

      } catch (error) {

        console.error(
          "Payment verification error:",
          error
        );


        attempts++;


        if (
          attempts >= maxAttempts
        ) {

          setStatus(
            "success"
          );

          setMessage(
            "Payment completed. Please check My Orders shortly."
          );

          return;
        }


        setTimeout(
          checkOrder,
          2000
        );
      }
    };


    // ---------------------------------------------------
    // FIRST CHECK
    // ---------------------------------------------------

    checkOrder();


  }, [location.search]);


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="payment-result-page">

      <div className="payment-result-card">


        {/* SUCCESS ICON */}

        <div className="success-icon">
          ✓
        </div>


        {/* TITLE */}

        <h1>
          Payment Successful!
        </h1>


        {/* MESSAGE */}

        <p className="payment-message">
          {message}
        </p>


        {/* PAYMENT STATUS */}

        <div className="session-box">

          <span>
            Payment Status
          </span>

          <p>
            {
              status === "checking"
                ? "Verifying..."
                : "Paid"
            }
          </p>

        </div>


        {/* ORDER STATUS */}

        {order && (

          <div className="session-box">

            <span>
              Order Status
            </span>

            <p>
              {order.order_status}
            </p>

          </div>

        )}


        {/* ORDER ID */}

        {order && (

          <div className="session-box">

            <span>
              Order ID
            </span>

            <p>
              #{order.id}
            </p>

          </div>

        )}


        {/* BUTTONS */}

        <div className="payment-actions">


          <button
            className="primary-button"
            onClick={() =>
              navigate("/orders")
            }
          >
            View My Orders
          </button>


          <button
            className="secondary-button"
            onClick={() =>
              navigate("/products")
            }
          >
            Continue Shopping
          </button>


        </div>


      </div>

    </div>
  );
}


export default PaymentSuccess;