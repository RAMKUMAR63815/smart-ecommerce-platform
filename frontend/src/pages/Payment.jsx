import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/api";
import "./Payment.css";

function Payment() {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paying, setPaying] = useState(false);
  const [success, setSuccess] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState("UPI");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!orderId) {
      setError("Invalid order ID");
      setLoading(false);
      return;
    }

    loadOrder();
  }, [orderId]);

  const loadOrder = async () => {
    try {
      setLoading(true);
      setError("");

      console.log(
        "Loading payment for order:",
        orderId
      );

      const res = await api.get(
        `/orders/${orderId}`
      );

      console.log(
        "Payment Order:",
        res.data
      );

      setOrder(res.data);

    } catch (err) {
      console.error(
        "Payment order error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to load payment"
      );
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    if (!order) {
      return;
    }

    try {
      setPaying(true);
      setError("");

      console.log(
        "Processing payment for order:",
        order.id
      );

      console.log(
        "Payment method:",
        paymentMethod
      );

      const res = await api.put(
        `/orders/${order.id}/pay`
      );

      console.log(
        "Payment response:",
        res.data
      );

      /*
       * Backend may return:
       * { order: {...} }
       *
       * or directly:
       * {...}
       */

      const updatedOrder =
        res.data?.order || res.data;

      setOrder(updatedOrder);

      setSuccess(true);

    } catch (err) {
      console.error(
        "Payment error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Payment failed"
      );
    } finally {
      setPaying(false);
    }
  };

  if (loading) {
    return (
      <div className="payment-page">
        <div className="payment-loading">
          Loading payment...
        </div>
      </div>
    );
  }

  if (error && !order) {
    return (
      <div className="payment-page">
        <div className="payment-card">

          <h2>Payment Error</h2>

          <p
            style={{
              color: "red",
              marginBottom: "20px",
            }}
          >
            {error}
          </p>

          <button
            className="primary-btn"
            onClick={() =>
              navigate("/orders")
            }
          >
            Back to Orders
          </button>

        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="payment-page">
        <div className="payment-card">

          <h2>Order Not Found</h2>

          <button
            className="primary-btn"
            onClick={() =>
              navigate("/orders")
            }
          >
            Back to Orders
          </button>

        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="payment-page">

        <div className="success-card">

          <div className="success-circle">
            ✓
          </div>

          <h1>
            Payment Successful
          </h1>

          <p className="success-message">
            Your payment has been completed
            successfully.
          </p>

          <div className="success-details">

            <div className="detail-row">
              <span>Order ID</span>

              <strong>
                #{order.id}
              </strong>
            </div>

            <div className="detail-row">
              <span>Amount</span>

              <strong>
                ₹{order.total_amount}
              </strong>
            </div>

            <div className="detail-row">
              <span>Status</span>

              <strong className="paid-status">
                {order.status}
              </strong>
            </div>

          </div>

          <button
            className="primary-btn"
            onClick={() =>
              navigate("/orders")
            }
          >
            View My Orders
          </button>

          <button
            className="secondary-btn"
            onClick={() =>
              navigate(
                `/orders/${order.id}`
              )
            }
          >
            Order Details
          </button>

        </div>

      </div>
    );
  }

  return (
    <div className="payment-page">

      <div className="payment-card">

        <div className="payment-header">

          <div>
            <span className="small-title">
              SECURE CHECKOUT
            </span>

            <h1>Payment</h1>
          </div>

          <div className="lock-icon">
            🔒
          </div>

        </div>

        {error && (
          <div
            style={{
              background: "#fee2e2",
              color: "#b91c1c",
              padding: "12px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            {error}
          </div>
        )}

        <div className="order-summary">

          <div className="summary-row">
            <span>Order ID</span>

            <strong>
              #{order.id}
            </strong>
          </div>

          <div className="summary-row">
            <span>User ID</span>

            <strong>
              {order.user_id}
            </strong>
          </div>

          <div className="summary-row">
            <span>Total Amount</span>

            <strong className="amount">
              ₹{order.total_amount}
            </strong>
          </div>

          <div className="summary-row">
            <span>Order Status</span>

            <span className="pending-status">
              {order.status}
            </span>
          </div>

        </div>

        <h3 className="section-title">
          Select Payment Method
        </h3>

        <div className="payment-methods">

          <label
            className={
              paymentMethod === "UPI"
                ? "payment-option selected"
                : "payment-option"
            }
          >

            <input
              type="radio"
              name="payment"
              value="UPI"
              checked={
                paymentMethod === "UPI"
              }
              onChange={(e) =>
                setPaymentMethod(
                  e.target.value
                )
              }
            />

            <div className="method-icon">
              U
            </div>

            <div className="method-info">
              <strong>UPI</strong>

              <span>
                Google Pay, PhonePe, Paytm
              </span>
            </div>

          </label>

          <label
            className={
              paymentMethod === "CARD"
                ? "payment-option selected"
                : "payment-option"
            }
          >

            <input
              type="radio"
              name="payment"
              value="CARD"
              checked={
                paymentMethod === "CARD"
              }
              onChange={(e) =>
                setPaymentMethod(
                  e.target.value
                )
              }
            />

            <div className="method-icon">
              💳
            </div>

            <div className="method-info">
              <strong>
                Credit / Debit Card
              </strong>

              <span>
                Visa, Mastercard, RuPay
              </span>
            </div>

          </label>

          <label
            className={
              paymentMethod === "COD"
                ? "payment-option selected"
                : "payment-option"
            }
          >

            <input
              type="radio"
              name="payment"
              value="COD"
              checked={
                paymentMethod === "COD"
              }
              onChange={(e) =>
                setPaymentMethod(
                  e.target.value
                )
              }
            />

            <div className="method-icon">
              💵
            </div>

            <div className="method-info">
              <strong>
                Cash on Delivery
              </strong>

              <span>
                Pay when your order arrives
              </span>
            </div>

          </label>

        </div>

        <button
          className="pay-btn"
          onClick={handlePayment}
          disabled={paying}
        >
          {paying
            ? "Processing Payment..."
            : `Pay ₹${order.total_amount}`}
        </button>

        <button
          className="back-btn"
          onClick={() =>
            navigate(
              `/orders/${order.id}`
            )
          }
        >
          ← Back to Order
        </button>

        <div className="secure-text">
          🔒 Your payment information is secure
        </div>

      </div>

    </div>
  );
}

export default Payment;