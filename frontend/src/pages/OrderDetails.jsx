import { useEffect, useState } from "react";
import {
  useNavigate,
  useParams
} from "react-router-dom";

import api from "../api/api";
import "./OrderDetails.css";

function OrderDetails() {

  const { orderId } = useParams();

  const navigate = useNavigate();

  const [order, setOrder] = useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  // =========================================================
  // LOAD ORDER
  // =========================================================

  useEffect(() => {
    loadOrder();
  }, [orderId]);

  const loadOrder = async () => {

    try {

      setLoading(true);
      setError("");

      const res = await api.get(
        `/orders/${orderId}`
      );

      console.log(
        "Order details:",
        res.data
      );

      setOrder(res.data);

    } catch (err) {

      console.error(
        "Order details error:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to load order"
      );

    } finally {

      setLoading(false);

    }
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {

    return (
      <div style={pageStyle}>

        <div style={cardStyle}>

          <h2
            style={{
              color: "white"
            }}
          >
            Loading Order...
          </h2>

        </div>

      </div>
    );
  }

  // =========================================================
  // ERROR
  // =========================================================

  if (error) {

    return (
      <div style={pageStyle}>

        <div style={cardStyle}>

          <h2
            style={{
              color: "white"
            }}
          >
            Order Error
          </h2>

          <p
            style={{
              color: "red"
            }}
          >
            {error}
          </p>

          <button
            onClick={() =>
              navigate("/orders")
            }
            style={
              secondaryButtonStyle
            }
          >
            Back to Orders
          </button>

        </div>

      </div>
    );
  }

  if (!order) {
    return null;
  }

  const paymentStatus =
    String(
      order.payment_status || ""
    ).toLowerCase();

  const orderStatus =
    String(
      order.order_status || ""
    ).toLowerCase();

  const isPaid =
    paymentStatus === "paid";

  return (
    <div style={pageStyle}>

      <div style={cardStyle}>

        <h1
          style={{
            textAlign: "center",
            marginBottom: "30px",
            color: "white",
          }}
        >
          Order Details
        </h1>

        <div
          style={{
            borderBottom:
              "1px solid #444",
            paddingBottom: "20px",
          }}
        >

          <h2
            style={{
              color: "white"
            }}
          >
            Order #{order.id}
          </h2>

          <p
            style={{
              color: "white"
            }}
          >
            <strong>
              User ID:
            </strong>{" "}
            {order.user_id}
          </p>

          <p
            style={{
              fontSize: "22px",
              fontWeight: "bold",
              color: "white",
            }}
          >
            Total Amount: ₹
            {Number(
              order.total_amount
            ).toLocaleString("en-IN")}
          </p>

          <p
            style={{
              color: "white"
            }}
          >
            <strong>
              Payment Status:
            </strong>{" "}

            <span
              style={{
                color: isPaid
                  ? "#22c55e"
                  : "#f59e0b",
                fontWeight: "bold",
              }}
            >
              {order.payment_status}
            </span>
          </p>

          <p
            style={{
              color: "white"
            }}
          >
            <strong>
              Order Status:
            </strong>{" "}

            <span
              style={{
                color:
                  orderStatus ===
                  "confirmed"
                    ? "#22c55e"
                    : "#f59e0b",
                fontWeight: "bold",
              }}
            >
              {order.order_status}
            </span>
          </p>

          <p
            style={{
              color: "#d1d5db"
            }}
          >
            <strong>
              Created:
            </strong>{" "}

            {order.created_at
              ? new Date(
                  order.created_at
                ).toLocaleString("en-IN")
              : "N/A"}
          </p>

        </div>

        <div
          style={{
            display: "flex",
            gap: "12px",
            marginTop: "25px",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >

          <button
            onClick={() =>
              navigate("/orders")
            }
            style={
              secondaryButtonStyle
            }
          >
            Back to Orders
          </button>

          {isPaid ? (

            <button
              onClick={() =>
                navigate("/products")
              }
              style={
                primaryButtonStyle
              }
            >
              Continue Shopping
            </button>

          ) : (

            <button
              onClick={() =>
                navigate("/cart")
              }
              style={
                primaryButtonStyle
              }
            >
              Return to Cart
            </button>

          )}

        </div>

      </div>

    </div>
  );
}

// =========================================================
// STYLES
// =========================================================

const pageStyle = {
  minHeight: "100vh",
  width: "100%",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  padding: "30px",
  boxSizing: "border-box",
  backgroundColor: "#f5f7fb",
};

const cardStyle = {
  width: "100%",
  maxWidth: "600px",
  backgroundColor: "#111827",
  padding: "35px",
  borderRadius: "12px",
  boxShadow:
    "0 4px 20px rgba(0, 0, 0, 0.08)",
  boxSizing: "border-box",
};

const primaryButtonStyle = {
  padding: "12px 20px",
  border: "none",
  borderRadius: "6px",
  backgroundColor: "#2563eb",
  color: "white",
  fontSize: "15px",
  fontWeight: "bold",
  cursor: "pointer",
};

const secondaryButtonStyle = {
  padding: "12px 20px",
  border: "none",
  borderRadius: "6px",
  backgroundColor: "#4b5563",
  color: "white",
  fontSize: "15px",
  fontWeight: "bold",
  cursor: "pointer",
};

export default OrderDetails;