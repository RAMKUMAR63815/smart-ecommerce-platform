
import { useEffect, useState } from "react";

function AdminReturns() {
  const [returns, setReturns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);

  const API_URL = "http://127.0.0.1:8000";

  // =====================================================
  // GET ALL RETURN REQUESTS
  // =====================================================

  const fetchReturns = async () => {
    try {
      setLoading(true);

      const response = await fetch(
        `${API_URL}/orders/returns`
      );

      const data = await response.json();

      console.log("RETURN REQUESTS:", data);

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to fetch returns"
        );
      }

      if (Array.isArray(data)) {
        setReturns(data);
      } else if (Array.isArray(data.returns)) {
        setReturns(data.returns);
      } else {
        setReturns([]);
      }

    } catch (error) {
      console.error(
        "Error fetching return requests:",
        error
      );

      alert("Unable to load return requests");

    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // LOAD DATA WHEN PAGE OPENS
  // =====================================================

  useEffect(() => {
    fetchReturns();
  }, []);

  // =====================================================
  // APPROVE RETURN
  // =====================================================

  const approveReturn = async (returnId) => {
    const confirmed = window.confirm(
      "Are you sure you want to approve this return?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingId(returnId);

      console.log(
        "Approving return:",
        returnId
      );

      const response = await fetch(
        `${API_URL}/orders/returns/${returnId}/approve`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      console.log(
        "Approve response:",
        data
      );

      if (!response.ok) {
        alert(
          data.detail ||
          "Failed to approve return"
        );

        return;
      }

      alert(
        "Return approved successfully"
      );

      await fetchReturns();

    } catch (error) {
      console.error(
        "Approve error:",
        error
      );

      alert(
        "Something went wrong while approving the return"
      );

    } finally {
      setProcessingId(null);
    }
  };

  // =====================================================
  // REJECT RETURN
  // =====================================================

  const rejectReturn = async (returnId) => {
    const confirmed = window.confirm(
      "Are you sure you want to reject this return?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingId(returnId);

      console.log(
        "Rejecting return:",
        returnId
      );

      const response = await fetch(
        `${API_URL}/orders/returns/${returnId}/reject`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      console.log(
        "Reject response:",
        data
      );

      if (!response.ok) {
        alert(
          data.detail ||
          "Failed to reject return"
        );

        return;
      }

      alert(
        "Return rejected successfully"
      );

      await fetchReturns();

    } catch (error) {
      console.error(
        "Reject error:",
        error
      );

      alert(
        "Something went wrong while rejecting the return"
      );

    } finally {
      setProcessingId(null);
    }
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div
        style={{
          padding: "30px",
        }}
      >
        <h2>
          Loading Return Requests...
        </h2>
      </div>
    );
  }

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div
      style={{
        padding: "30px",
        backgroundColor: "#f5f5f5",
        minHeight: "100vh",
      }}
    >

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >

        <h1 style={{ color: "grey" }}>
          🔔 Return Requests
        </h1>

        <button
          onClick={fetchReturns}
          style={{
            padding: "10px 20px",
            cursor: "pointer",
            border: "none",
            borderRadius: "5px",
            backgroundColor: "#007bff",
            color: "white",
          }}
        >
          🔄 Refresh
        </button>

      </div>


      {/* =================================================
          NO RETURN REQUESTS
      ================================================= */}

      {returns.length === 0 ? (

        <div
          style={{
            backgroundColor: "white",
            padding: "25px",
            marginTop: "20px",
            borderRadius: "10px",
            boxShadow:
              "0 2px 8px rgba(0,0,0,0.1)",
          }}
        >

          <h3>
            No Return Requests
          </h3>

          <button
            onClick={fetchReturns}
            style={{
              padding: "10px 20px",
              marginTop: "10px",
              cursor: "pointer",
            }}
          >
            Refresh
          </button>

        </div>

      ) : (

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            marginTop: "20px",
          }}
        >

          {returns.map((item) => {

            // =================================================
            // IMPORTANT FIX
            // Convert status to lowercase
            //
            // Pending  -> pending
            // PENDING  -> pending
            // pending  -> pending
            //
            // Approved -> approved
            // Rejected -> rejected
            // =================================================

            const normalizedStatus =
              item.status?.toLowerCase();

            return (

              <div
                key={item.id}
                style={{
                  backgroundColor: "white",
                  padding: "25px",
                  borderRadius: "10px",
                  boxShadow:
                    "0 2px 8px rgba(0,0,0,0.1)",
                }}
              >

                {/* =================================================
                    RETURN ID
                ================================================= */}

                <h2>
                  Return Request #{item.id}
                </h2>


                {/* =================================================
                    ORDER
                ================================================= */}

                <p>
                  <strong>
                    Order ID:
                  </strong>{" "}
                  #{item.order_id}
                </p>


                {/* =================================================
                    USER
                ================================================= */}

                <p>
                  <strong>
                    User ID:
                  </strong>{" "}
                  {item.user_id}
                </p>


                {/* =================================================
                    REASON
                ================================================= */}

                <p>
                  <strong>
                    Reason:
                  </strong>{" "}
                  {item.reason}
                </p>


                {/* =================================================
                    COMMENT
                ================================================= */}

                <p>
                  <strong>
                    Comment:
                  </strong>{" "}
                  {item.comment || "No comment"}
                </p>


                {/* =================================================
                    CREATED DATE
                ================================================= */}

                {item.created_at && (

                  <p>
                    <strong>
                      Requested At:
                    </strong>{" "}
                    {new Date(
                      item.created_at
                    ).toLocaleString()}
                  </p>

                )}


                {/* =================================================
                    STATUS
                ================================================= */}

                <p>
                  <strong>
                    Status:
                  </strong>{" "}

                  <span
                    style={{
                      fontWeight: "bold",
                      textTransform: "capitalize",
                    }}
                  >
                    {item.status}
                  </span>
                </p>


                {/* =================================================
                    PENDING
                    SHOW APPROVE + REJECT
                ================================================= */}

                {normalizedStatus === "pending" && (

                  <div
                    style={{
                      display: "flex",
                      gap: "10px",
                      marginTop: "20px",
                    }}
                  >

                    {/* APPROVE */}

                    <button
                      onClick={() =>
                        approveReturn(item.id)
                      }
                      disabled={
                        processingId === item.id
                      }
                      style={{
                        padding: "10px 20px",
                        backgroundColor: "#28a745",
                        color: "white",
                        border: "none",
                        borderRadius: "5px",
                        cursor:
                          processingId === item.id
                            ? "not-allowed"
                            : "pointer",
                        opacity:
                          processingId === item.id
                            ? 0.6
                            : 1,
                      }}
                    >

                      {processingId === item.id
                        ? "Processing..."
                        : "✓ Approve"}

                    </button>


                    {/* REJECT */}

                    <button
                      onClick={() =>
                        rejectReturn(item.id)
                      }
                      disabled={
                        processingId === item.id
                      }
                      style={{
                        padding: "10px 20px",
                        backgroundColor: "#dc3545",
                        color: "white",
                        border: "none",
                        borderRadius: "5px",
                        cursor:
                          processingId === item.id
                            ? "not-allowed"
                            : "pointer",
                        opacity:
                          processingId === item.id
                            ? 0.6
                            : 1,
                      }}
                    >

                      {processingId === item.id
                        ? "Processing..."
                        : "✕ Reject"}

                    </button>

                  </div>

                )}


                {/* =================================================
                    APPROVED
                ================================================= */}

                {normalizedStatus === "approved" && (

                  <div
                    style={{
                      marginTop: "20px",
                      padding: "12px",
                      backgroundColor: "#e8f5e9",
                      borderRadius: "5px",
                    }}
                  >

                    <p
                      style={{
                        color: "green",
                        fontWeight: "bold",
                        margin: 0,
                      }}
                    >
                      ✓ Return Approved
                    </p>

                  </div>

                )}


                {/* =================================================
                    REJECTED
                ================================================= */}

                {normalizedStatus === "rejected" && (

                  <div
                    style={{
                      marginTop: "20px",
                      padding: "12px",
                      backgroundColor: "#ffebee",
                      borderRadius: "5px",
                    }}
                  >

                    <p
                      style={{
                        color: "red",
                        fontWeight: "bold",
                        margin: 0,
                      }}
                    >
                      ✕ Return Rejected
                    </p>

                  </div>

                )}

              </div>

            );

          })}

        </div>

      )}

    </div>
  );
}

export default AdminReturns;

