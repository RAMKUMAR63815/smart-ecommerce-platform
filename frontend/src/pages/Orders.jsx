import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import "./Orders.css";

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const userId =
    localStorage.getItem("user_id");

  // =====================================================
  // LOAD ORDERS
  // =====================================================

  useEffect(() => {
    if (userId) {
      loadOrders();
    } else {
      setError("Please login first.");
      setLoading(false);
    }
  }, [userId]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/orders/?user_id=${userId}`
      );

      console.log(
        "Orders response:",
        response.data
      );

      setOrders(
        Array.isArray(response.data)
          ? response.data
          : []
      );

    } catch (err) {
      console.error(
        "Orders error:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to load orders"
      );

      setOrders([]);

    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (
      <div className="orders-page">

        <div className="orders-container">

          <h1>
            My Orders
          </h1>

          <div className="orders-loading">

            <div className="spinner"></div>

            <p>
              Loading orders...
            </p>

          </div>

        </div>

      </div>
    );
  }

  // =====================================================
  // ERROR
  // =====================================================

  if (error) {

    return (
      <div className="orders-page">

        <div className="orders-container">

          <h1>
            My Orders
          </h1>

          <div className="orders-error">

            <div className="error-icon">
              !
            </div>

            <h2>
              Unable to load orders
            </h2>

            <p>
              {error}
            </p>

            <button
              className="retry-btn"
              onClick={loadOrders}
            >
              Try Again
            </button>

          </div>

        </div>

      </div>
    );
  }

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="orders-page">

      <div className="orders-container">

        <div className="orders-header">

          <div>

            <h1>
              My Orders
            </h1>

            <p>
              View and track your recent orders
            </p>

          </div>

          <button
            className="shop-btn"
            onClick={() =>
              navigate("/products")
            }
          >
            Continue Shopping
          </button>

        </div>

        {orders.length === 0 ? (

          <div className="empty-orders">

            <div className="empty-icon">
              🛒
            </div>

            <h2>
              No Orders Found
            </h2>

            <p>
              You haven't placed any orders yet.
            </p>

            <button
              className="shop-btn"
              onClick={() =>
                navigate("/products")
              }
            >
              Start Shopping
            </button>

          </div>

        ) : (

          <div className="orders-list">

            {orders.map((order) => {

              const isPaid =
                String(
                  order.payment_status
                ).toLowerCase() === "paid";

              const isConfirmed =
                String(
                  order.order_status
                ).toLowerCase() ===
                "confirmed";

              return (
                <div
                  className="order-card"
                  key={order.id}
                >

                  <div className="order-card-header">

                    <div>

                      <span className="order-label">
                        ORDER ID
                      </span>

                      <h2>
                        #{order.id}
                      </h2>

                    </div>

                    <div className="order-date">

                      {order.created_at
                        ? new Date(
                            order.created_at
                          ).toLocaleDateString(
                            "en-IN",
                            {
                              day: "2-digit",
                              month: "short",
                              year: "numeric",
                            }
                          )
                        : "N/A"}

                    </div>

                  </div>

                  <div className="order-info">

                    <div className="info-item">

                      <span>
                        User ID
                      </span>

                      <strong>
                        {order.user_id}
                      </strong>

                    </div>

                    <div className="info-item">

                      <span>
                        Total Amount
                      </span>

                      <strong className="amount">

                        ₹
                        {Number(
                          order.total_amount
                        ).toLocaleString(
                          "en-IN"
                        )}

                      </strong>

                    </div>

                    <div className="info-item">

                      <span>
                        Payment
                      </span>

                      <strong
                        className={
                          isPaid
                            ? "status paid"
                            : "status pending"
                        }
                      >
                        {order.payment_status}
                      </strong>

                    </div>

                    <div className="info-item">

                      <span>
                        Order Status
                      </span>

                      <strong
                        className={
                          isConfirmed
                            ? "status confirmed"
                            : "status pending"
                        }
                      >
                        {order.order_status}
                      </strong>

                    </div>

                  </div>

                  <div className="order-card-footer">

                    <span>
                      {isPaid
                        ? "Payment completed successfully"
                        : "Payment pending"}
                    </span>

                    <button
                      className="details-btn"
                      onClick={() =>
                        navigate(
                          `/orders/${order.id}`
                        )
                      }
                    >
                      View Details →
                    </button>

                  </div>

                </div>
              );
            })}

          </div>
        )}

      </div>

    </div>
  );
}

export default Orders;