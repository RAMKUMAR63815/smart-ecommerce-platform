import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Orders() {

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const userId = 1;

  const navigate = useNavigate();

  // =========================
  // LOAD ORDERS
  // =========================

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {

    try {

      setLoading(true);
      setError("");

      const res = await axios.get(
        `http://127.0.0.1:8000/orders/?user_id=${userId}`
      );

      console.log("Orders response:", res.data);

      if (Array.isArray(res.data)) {

        setOrders(res.data);

      } else {

        setOrders([]);

      }

    } catch (err) {

      console.error("Orders error:", err);

      if (err.response) {

        setError(
          err.response.data.detail ||
          "Failed to load orders"
        );

      } else {

        setError("Cannot connect to server");

      }

      setOrders([]);

    } finally {

      setLoading(false);

    }

  };

  // =========================
  // LOADING
  // =========================

  if (loading) {

    return (
      <div style={{ padding: "20px" }}>

        <h1>My Orders</h1>

        <p>Loading orders...</p>

      </div>
    );

  }

  // =========================
  // ERROR
  // =========================

  if (error) {

    return (
      <div style={{ padding: "20px" }}>

        <h1>My Orders</h1>

        <p style={{ color: "red" }}>
          {error}
        </p>

        <button onClick={loadOrders}>
          Try Again
        </button>

      </div>
    );

  }

  // =========================
  // ORDERS PAGE
  // =========================

  return (

    <div
      style={{
        padding: "20px"
      }}
    >

      <h1>My Orders</h1>

      {orders.length === 0 ? (

        <div>

          <p>No Orders Found</p>

          <button
            onClick={() => navigate("/products")}
          >
            Continue Shopping
          </button>

        </div>

      ) : (

        <div>

          {orders.map((order) => (

            <div
              key={order.id}
              style={{
                border: "1px solid #ccc",
                padding: "20px",
                marginBottom: "15px",
                borderRadius: "8px"
              }}
            >

              <h2>
                Order ID : {order.id}
              </h2>

              <p>
                <strong>User ID :</strong>{" "}
                {order.user_id}
              </p>

              <p>
                <strong>Total :</strong>{" "}
                ₹{order.total_amount}
              </p>

              <p>
                <strong>Status :</strong>{" "}
                {order.status}
              </p>

              {/* VIEW DETAILS */}

              <button
                onClick={() =>
                  navigate(`/orders/${order.id}`)
                }
                style={{
                  padding: "10px 15px",
                  marginTop: "10px",
                  cursor: "pointer"
                }}
              >
                View Details
              </button>

            </div>

          ))}

        </div>

      )}

    </div>

  );
}

export default Orders;