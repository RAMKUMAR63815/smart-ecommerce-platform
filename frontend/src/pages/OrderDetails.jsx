import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/api";
import "./OrderDetails.css";

function OrderDetails() {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadOrder();
  }, [orderId]);

  const loadOrder = async () => {
    try {
      setLoading(true);
      setError("");

      const res = await api.get(`/orders/${orderId}`);

      console.log("Order details:", res.data);

      setOrder(res.data);
    } catch (err) {
      console.error("Order details error:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load order"
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={pageStyle}>
        <div style={cardStyle}>
          <h2>Loading Order...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={pageStyle}>
        <div style={cardStyle}>
          <h2>Order Error</h2>

          <p style={{ color: "red" }}>
            {error}
          </p>

          <button
            onClick={() => navigate("/orders")}
            style={secondaryButtonStyle}
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
            borderBottom: "1px solid #444",
            paddingBottom: "20px",
          }}
        >

          <h2 style={{ color: "white" }}>
            Order #{order.id}
          </h2>

          <p style={{ color: "white" }}>
            <strong>User ID:</strong>{" "}
            {order.user_id}
          </p>

          <p
            style={{
              fontSize: "22px",
              fontWeight: "bold",
              color: "white",
            }}
          >
            Total Amount: ₹{order.total_amount}
          </p>

          <p style={{ color: "white" }}>
            <strong>Status:</strong>{" "}
            <span
              style={{
                color:
                  order.status === "Paid"
                    ? "#22c55e"
                    : "#f59e0b",
                fontWeight: "bold",
              }}
            >
              {order.status}
            </span>
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
            onClick={() => navigate("/orders")}
            style={secondaryButtonStyle}
          >
            Back to Orders
          </button>

          {order.status !== "Paid" && (
            <button
              onClick={() => {
                console.log(
                  "Going to payment:",
                  order.id
                );

                navigate(`/payment/${order.id}`);
              }}
              style={primaryButtonStyle}
            >
              Proceed to Payment
            </button>
          )}

          {order.status === "Paid" && (
            <button
              onClick={() => navigate("/products")}
              style={primaryButtonStyle}
            >
              Continue Shopping
            </button>
          )}

        </div>
      </div>
    </div>
  );
}

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
  boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
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