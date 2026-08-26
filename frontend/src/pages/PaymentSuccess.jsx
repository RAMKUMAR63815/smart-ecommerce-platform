  import { useEffect } from "react";
  import {
    Link,
    useSearchParams
  } from "react-router-dom";

  import "./PaymentSuccess.css";

  function PaymentSuccess() {

    const [searchParams] =
      useSearchParams();

    const sessionId =
      searchParams.get(
        "session_id"
      );

    useEffect(() => {

      console.log(
        "Stripe Session ID:",
        sessionId
      );

    }, [sessionId]);

    return (

      <div className="payment-result-page">

        <div className="payment-result-card">

          <div className="success-icon">
            ✓
          </div>

          <h1>
            Payment Successful!
          </h1>

          <p className="payment-message">
            Your Stripe payment was completed
            successfully. Your order is being
            confirmed by the server.
          </p>

          {sessionId && (

            <div className="session-box">

              <span>
                Transaction ID
              </span>

              <p>
                {sessionId}
              </p>

            </div>

          )}

          <div className="payment-actions">

            <Link
              to="/orders"
              className="primary-button"
            >
              View My Orders
            </Link>

            <Link
              to="/products"
              className="secondary-button"
            >
              Continue Shopping
            </Link>

          </div>

        </div>

      </div>

    );
  }

  export default PaymentSuccess;