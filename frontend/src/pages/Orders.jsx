
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import "./Orders.css";

function Orders() {

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // =====================================================
  // RETURN MODAL STATE
  // =====================================================

  const [showReturnModal, setShowReturnModal] =
    useState(false);

  const [selectedOrder, setSelectedOrder] =
    useState(null);

  const [returnReason, setReturnReason] =
    useState("");

  const [returnComment, setReturnComment] =
    useState("");

  const [returnLoading, setReturnLoading] =
    useState(false);

  const [returnMessage, setReturnMessage] =
    useState("");

  const [returnError, setReturnError] =
    useState("");

  const navigate = useNavigate();


  // =====================================================
  // LOGGED-IN USER
  // =====================================================

  const userId = localStorage.getItem("user_id");


  // =====================================================
  // GET ORDERS
  // =====================================================

  const loadOrders = async (showLoader = false) => {

    try {

      // Only show full-page loader on first load
      if (showLoader) {
        setLoading(true);
      }

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

      if (showLoader) {
        setLoading(false);
      }

    }

  };


  // =====================================================
  // LOAD ORDERS + AUTO REFRESH
  // =====================================================

  useEffect(() => {

    if (!userId) {

      setError(
        "Please login first."
      );

      setLoading(false);

      return;
    }


    // ---------------------------------------------------
    // FIRST LOAD
    // ---------------------------------------------------

    loadOrders(true);


    // ---------------------------------------------------
    // AUTO REFRESH
    //
    // This allows Stripe webhook changes to appear
    // automatically on the Orders page.
    // ---------------------------------------------------

    const interval = setInterval(() => {

      loadOrders(false);

    }, 3000);


    // ---------------------------------------------------
    // CLEANUP
    // ---------------------------------------------------

    return () => {

      clearInterval(interval);

    };

  }, [userId]);


  // =====================================================
  // OPEN RETURN MODAL
  // =====================================================

  const openReturnModal = (order) => {

    console.log(
      "Opening return modal for order:",
      order
    );

    setSelectedOrder(order);

    setReturnReason("");
    setReturnComment("");

    setReturnMessage("");
    setReturnError("");

    setShowReturnModal(true);

  };


  // =====================================================
  // CLOSE RETURN MODAL
  // =====================================================

  const closeReturnModal = () => {

    if (returnLoading) {
      return;
    }

    setShowReturnModal(false);

    setSelectedOrder(null);

    setReturnReason("");
    setReturnComment("");

    setReturnMessage("");
    setReturnError("");

  };


  // =====================================================
  // SUBMIT RETURN REQUEST
  // =====================================================

  const submitReturnRequest = async () => {

    // ---------------------------------------------------
    // CHECK ORDER
    // ---------------------------------------------------

    if (!selectedOrder) {

      setReturnError(
        "No order selected."
      );

      return;

    }


    // ---------------------------------------------------
    // CHECK REASON
    // ---------------------------------------------------

    if (!returnReason.trim()) {

      setReturnError(
        "Please enter a return reason."
      );

      return;

    }


    try {

      setReturnLoading(true);

      setReturnError("");
      setReturnMessage("");


      console.log(
        "Submitting return request:",
        {
          order_id: selectedOrder.id,
          reason: returnReason,
          comment: returnComment
        }
      );


      // -------------------------------------------------
      // CALL FASTAPI
      // -------------------------------------------------

      const response = await api.post(
        `/orders/${selectedOrder.id}/return`,
        {
          reason: returnReason,
          comment: returnComment
        }
      );


      console.log(
        "Return response:",
        response.data
      );


      // -------------------------------------------------
      // SUCCESS
      // -------------------------------------------------

      setReturnMessage(
        response.data?.message ||
        "Return request submitted successfully."
      );


      // -------------------------------------------------
      // CLOSE AFTER SHORT DELAY
      // -------------------------------------------------

      setTimeout(() => {

        setShowReturnModal(false);

        setSelectedOrder(null);

        setReturnReason("");
        setReturnComment("");

        setReturnMessage("");
        setReturnError("");

        // Reload orders so status becomes
        // "Return Requested"

        loadOrders(false);

      }, 1200);


    } catch (err) {

      console.error(
        "Return request error:",
        err
      );


      setReturnError(
        err.response?.data?.detail ||
        "Failed to submit return request."
      );

    } finally {

      setReturnLoading(false);

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
              onClick={() => loadOrders(true)}
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


        {/* =================================================
            PAGE HEADER
            ================================================= */}

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


        {/* =================================================
            EMPTY ORDERS
            ================================================= */}

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

          /* =================================================
             ORDERS LIST
             ================================================= */

          <div className="orders-list">

            {orders.map((order) => {

              // ------------------------------------------------
              // PAYMENT STATUS
              // ------------------------------------------------

              const isPaid =
                String(
                  order.payment_status || ""
                ).toLowerCase() === "paid";


              // ------------------------------------------------
              // ORDER STATUS
              // ------------------------------------------------

              const orderStatus =
                String(
                  order.order_status || ""
                ).trim();


              const isConfirmed =
                orderStatus.toLowerCase() ===
                "confirmed";


              // ------------------------------------------------
              // RETURN STATUS
              // ------------------------------------------------

              const isDelivered =
                orderStatus.toLowerCase() ===
                "delivered";


              const isReturnRequested =
                orderStatus.toLowerCase() ===
                "return requested";


              const isReturned =
                orderStatus.toLowerCase() ===
                "returned";


              // ------------------------------------------------
              // CAN REQUEST RETURN
              // ------------------------------------------------

              const canRequestReturn =
                isPaid &&
                isDelivered &&
                !isReturnRequested &&
                !isReturned;


              return (

                <div
                  className="order-card"
                  key={order.id}
                >


                  {/* =================================================
                      ORDER HEADER
                      ================================================= */}

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

                        : "N/A"

                      }

                    </div>

                  </div>


                  {/* =================================================
                      ORDER INFORMATION
                      ================================================= */}

                  <div className="order-info">


                    {/* USER ID */}

                    <div className="info-item">

                      <span>
                        User ID
                      </span>

                      <strong>
                        {order.user_id}
                      </strong>

                    </div>


                    {/* TOTAL */}

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


                    {/* PAYMENT */}

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


                    {/* ORDER STATUS */}

                    <div className="info-item">

                      <span>
                        Order Status
                      </span>

                      <strong
                        className={
                          isConfirmed
                            ? "status confirmed"
                            : isDelivered
                              ? "status delivered"
                              : isReturned
                                ? "status returned"
                                : isReturnRequested
                                  ? "status return-requested"
                                  : "status pending"
                        }
                      >

                        {order.order_status}

                      </strong>

                    </div>

                  </div>


                  {/* =================================================
                      ORDER FOOTER
                      ================================================= */}

                  <div className="order-card-footer">


                    {/* -------------------------------------------------
                        PAYMENT MESSAGE
                        ------------------------------------------------- */}

                    <span>

                      {isPaid

                        ? "Payment completed successfully"

                        : "Payment pending"

                      }

                    </span>


                    {/* -------------------------------------------------
                        ACTION BUTTONS
                        ------------------------------------------------- */}

                    <div className="order-actions">


                      {/* VIEW DETAILS */}

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


                      {/* =================================================
                          REQUEST RETURN
                          ================================================= */}

                      {canRequestReturn && (

                        <button
                          className="return-btn"
                          onClick={() =>
                            openReturnModal(order)
                          }
                        >
                          Request Return
                        </button>

                      )}


                      {/* =================================================
                          RETURN REQUESTED
                          ================================================= */}

                      {isReturnRequested && (

                        <span className="return-status">

                          Return Requested

                        </span>

                      )}


                      {/* =================================================
                          RETURNED
                          ================================================= */}

                      {isReturned && (

                        <span className="return-status returned">

                          Returned

                        </span>

                      )}

                    </div>

                  </div>

                </div>

              );

            })}

          </div>

        )}

      </div>


      {/* =========================================================
          RETURN MODAL
          ========================================================= */}

      {showReturnModal && selectedOrder && (

        <div
          className="return-modal-overlay"
          onClick={closeReturnModal}
        >

          <div
            className="return-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >


            {/* =================================================
                MODAL HEADER
                ================================================= */}

            <div className="return-modal-header">

              <div>

                <h2>
                  Request Return
                </h2>

                <p>
                  Order #{selectedOrder.id}
                </p>

              </div>


              <button
                className="modal-close-btn"
                onClick={closeReturnModal}
                disabled={returnLoading}
              >
                ×
              </button>

            </div>


            {/* =================================================
                SUCCESS MESSAGE
                ================================================= */}

            {returnMessage && (

              <div className="return-success">

                {returnMessage}

              </div>

            )}


            {/* =================================================
                ERROR MESSAGE
                ================================================= */}

            {returnError && (

              <div className="return-error">

                {returnError}

              </div>

            )}


            {/* =================================================
                RETURN FORM
                ================================================= */}

            {!returnMessage && (

              <div className="return-form">


                {/* -------------------------------------------------
                    REASON
                    ------------------------------------------------- */}

                <label>
                  Return Reason
                </label>

                <textarea
                  value={returnReason}
                  onChange={(event) =>
                    setReturnReason(
                      event.target.value
                    )
                  }
                  placeholder="Enter the reason for returning this order..."
                  rows="4"
                  disabled={returnLoading}
                />


                {/* -------------------------------------------------
                    COMMENT
                    ------------------------------------------------- */}

                <label>
                  Additional Comment
                  <span>
                    {" "}
                    (Optional)
                  </span>
                </label>

                <textarea
                  value={returnComment}
                  onChange={(event) =>
                    setReturnComment(
                      event.target.value
                    )
                  }
                  placeholder="Add any additional information..."
                  rows="3"
                  disabled={returnLoading}
                />


                {/* -------------------------------------------------
                    ACTIONS
                    ------------------------------------------------- */}

                <div className="return-modal-actions">

                  <button
                    type="button"
                    className="cancel-return-btn"
                    onClick={closeReturnModal}
                    disabled={returnLoading}
                  >
                    Cancel
                  </button>


                  <button
                    type="button"
                    className="submit-return-btn"
                    onClick={submitReturnRequest}
                    disabled={returnLoading}
                  >

                    {returnLoading

                      ? "Submitting..."

                      : "Submit Return Request"

                    }

                  </button>

                </div>

              </div>

            )}

          </div>

        </div>

      )}

    </div>

  );

}


export default Orders;

