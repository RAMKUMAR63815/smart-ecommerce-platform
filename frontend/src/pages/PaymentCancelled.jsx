import { Link } from "react-router-dom";

import "./PaymentCancelled.css";

function PaymentCancelled() {

  return (

    <div className="payment-result-page">

      <div className="payment-result-card">

        <div className="cancel-icon">
          ×
        </div>

        <h1>
          Payment Cancelled
        </h1>

        <p className="payment-message">

          Your payment was cancelled or the
          checkout session expired.

          Your pending order has not been
          marked as paid.

        </p>

        <div className="payment-actions">

          <Link
            to="/cart"
            className="primary-button"
          >
            Return to Cart
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

export default PaymentCancelled;