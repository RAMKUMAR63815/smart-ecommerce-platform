import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const userId = localStorage.getItem("user_id");
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      /*
       * If your backend dashboard endpoint is:
       * GET /dashboard
       */
      const response = await api.get("/dashboard");

      console.log("Dashboard response:", response.data);

      setDashboard(response.data);
    } catch (error) {
      console.error("Dashboard error:", error);

      setError(
        error.response?.data?.detail ||
          "Unable to load dashboard"
      );

      /*
       * Create fallback dashboard data.
       * This allows the page to remain attractive
       * even if the backend dashboard API is not ready.
       */
      setDashboard({
        total_products: 0,
        total_orders: 0,
        total_users: 0,
        total_revenue: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // LOGOUT
  // =========================

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user");
    localStorage.removeItem("user_role");

    navigate("/login", { replace: true });
  };

  // =========================
  // LOADING
  // =========================

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <h2>Loading Dashboard...</h2>
          <p>Please wait...</p>
        </div>
      </div>
    );
  }

  // =========================
  // DASHBOARD
  // =========================

  return (
    <div className="dashboard-page">

      {/* =========================
          SIDEBAR
      ========================= */}

      <aside className="dashboard-sidebar">

        <div className="sidebar-logo">
          <div className="logo-icon">
            S
          </div>

          <div>
            <h2>Smart</h2>
            <span>E-Commerce</span>
          </div>
        </div>

        <nav className="sidebar-menu">

          <button
            className="menu-item active"
            onClick={() => navigate("/dashboard")}
          >
            <span className="menu-icon">▦</span>
            Dashboard
          </button>

          <button
            className="menu-item"
            onClick={() => navigate("/products")}
          >
            <span className="menu-icon">🛍</span>
            Products
          </button>

          <button
            className="menu-item"
            onClick={() => navigate("/cart")}
          >
            <span className="menu-icon">🛒</span>
            Cart
          </button>

          <button
            className="menu-item"
            onClick={() => navigate("/orders")}
          >
            <span className="menu-icon">📦</span>
            My Orders
          </button>

        </nav>

        <div className="sidebar-bottom">

          <button
            className="menu-item"
            onClick={() => navigate("/products")}
          >
            <span className="menu-icon">←</span>
            Continue Shopping
          </button>

          <button
            className="logout-menu"
            onClick={logout}
          >
            <span className="menu-icon">↪</span>
            Logout
          </button>

        </div>

      </aside>


      {/* =========================
          MAIN CONTENT
      ========================= */}

      <main className="dashboard-main">

        {/* TOP BAR */}

        <header className="dashboard-header">

          <div>
            <h1>Dashboard</h1>

            <p>
              Welcome back
              {user?.name
                ? `, ${user.name}`
                : ""}
              !
            </p>
          </div>

          <div className="header-user">

            <div className="user-avatar">
              {user?.name
                ? user.name.charAt(0).toUpperCase()
                : "U"}
            </div>

            <div className="header-user-info">
              <strong>
                {user?.name || "User"}
              </strong>

              <span>
                {user?.email || "Customer"}
              </span>
            </div>

          </div>

        </header>


        {/* ERROR */}

        {error && (
          <div className="dashboard-warning">
            <span>⚠</span>
            {error}
          </div>
        )}


        {/* =========================
            STATISTICS
        ========================= */}

        <section className="stats-grid">

          {/* PRODUCTS */}

          <div className="stat-card">

            <div className="stat-icon products-icon">
              🛍
            </div>

            <div className="stat-content">
              <span>Total Products</span>

              <h2>
                {dashboard?.total_products ?? 0}
              </h2>

              <small>
                Available products
              </small>
            </div>

          </div>


          {/* ORDERS */}

          <div className="stat-card">

            <div className="stat-icon orders-icon">
              📦
            </div>

            <div className="stat-content">
              <span>Total Orders</span>

              <h2>
                {dashboard?.total_orders ?? 0}
              </h2>

              <small>
                Orders placed
              </small>
            </div>

          </div>


          {/* USERS */}

          <div className="stat-card">

            <div className="stat-icon users-icon">
              👥
            </div>

            <div className="stat-content">
              <span>Total Users</span>

              <h2>
                {dashboard?.total_users ?? 0}
              </h2>

              <small>
                Registered users
              </small>
            </div>

          </div>


          {/* REVENUE */}

          <div className="stat-card">

            <div className="stat-icon revenue-icon">
              ₹
            </div>

            <div className="stat-content">
              <span>Total Revenue</span>

              <h2>
                ₹
                {Number(
                  dashboard?.total_revenue || 0
                ).toLocaleString("en-IN")}
              </h2>

              <small>
                Overall revenue
              </small>
            </div>

          </div>

        </section>


        {/* =========================
            QUICK ACTIONS
        ========================= */}

        <section className="dashboard-section">

          <div className="section-heading">

            <div>
              <h2>Quick Actions</h2>

              <p>
                Manage your shopping activity
              </p>
            </div>

          </div>


          <div className="quick-actions">

            <button
              className="action-card"
              onClick={() => navigate("/products")}
            >

              <div className="action-icon blue">
                🛍
              </div>

              <div>
                <h3>Browse Products</h3>

                <p>
                  Explore available products
                </p>
              </div>

              <span className="action-arrow">
                →
              </span>

            </button>


            <button
              className="action-card"
              onClick={() => navigate("/cart")}
            >

              <div className="action-icon green">
                🛒
              </div>

              <div>
                <h3>Shopping Cart</h3>

                <p>
                  View and manage your cart
                </p>
              </div>

              <span className="action-arrow">
                →
              </span>

            </button>


            <button
              className="action-card"
              onClick={() => navigate("/orders")}
            >

              <div className="action-icon orange">
                📦
              </div>

              <div>
                <h3>My Orders</h3>

                <p>
                  Track your orders and payments
                </p>
              </div>

              <span className="action-arrow">
                →
              </span>

            </button>

          </div>

        </section>


        {/* =========================
            ACCOUNT CARD
        ========================= */}

        <section className="account-card">

          <div className="account-left">

            <div className="large-avatar">
              {user?.name
                ? user.name.charAt(0).toUpperCase()
                : "U"}
            </div>

            <div>

              <span className="account-label">
                Logged in as
              </span>

              <h2>
                {user?.name || "Customer"}
              </h2>

              <p>
                {user?.email || "No email available"}
              </p>

              <span className="role-badge">
                {localStorage.getItem(
                  "user_role"
                ) || "Customer"}
              </span>

            </div>

          </div>


          <div className="account-right">

            <p>
              User ID
            </p>

            <strong>
              #{userId || "N/A"}
            </strong>

          </div>

        </section>


        {/* =========================
            FOOTER
        ========================= */}

        <footer className="dashboard-footer">
          <p>
            © 2026 Smart E-Commerce Platform
          </p>

          <span>
            Secure • Fast • Reliable
          </span>
        </footer>

      </main>

    </div>
  );
}

export default Dashboard;