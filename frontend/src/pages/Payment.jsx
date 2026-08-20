import {
  useNavigate,
  useParams
} from "react-router-dom";

import "./Payment.css";

function Payment() {

  const { orderId } = useParams();

  const navigate = useNavigate();

  return (
    <div className="payment-page">

      <div className="payment-card">

        <div className="payment-header">

          <div>

            <span className="small-title">
              SECURE CHECKOUT
            </span>

            <h1>
              Payment
            </h1>

          </div>

          <div className="lock-icon">
            🔒
          </div>

        </div>

        <div className="order-summary">

          <div className="summary-row">

            <span>
              Order ID
            </span>

            <strong>
              #{orderId}
            </strong>

          </div>

        </div>

        <div className="secure-text">

          🔒 Payment is securely processed
          through Stripe Checkout.

        </div>

        <button
          className="back-btn"
          onClick={() =>
            navigate("/orders")
          }
        >
          ← Back to Orders
        </button>

      </div>

    </div>
  );
}

export default Payment;