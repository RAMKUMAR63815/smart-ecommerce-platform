import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import "./Cart.css";

function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [cartTotal, setCartTotal] = useState(0);
  const [tax, setTax] = useState(0);
  const [grandTotal, setGrandTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  const navigate = useNavigate();

  const userId = localStorage.getItem("user_id");

  // =========================================================
  // LOAD CART
  // =========================================================

  useEffect(() => {
    if (userId) {
      loadCart();
    } else {
      setLoading(false);
    }
  }, [userId]);

  const loadCart = async () => {
    try {
      setLoading(true);

      const response = await api.get(
        `/cart/?user_id=${userId}`
      );

      console.log("Cart response:", response.data);

      // Backend returns:
      // {
      //   items: [],
      //   cart_total: 0,
      //   tax: 0,
      //   grand_total: 0
      // }

      setCartItems(
        Array.isArray(response.data.items)
          ? response.data.items
          : []
      );

      setCartTotal(
        Number(response.data.cart_total || 0)
      );

      setTax(
        Number(response.data.tax || 0)
      );

      setGrandTotal(
        Number(response.data.grand_total || 0)
      );

    } catch (error) {
      console.error("Cart error:", error);

      setCartItems([]);
      setCartTotal(0);
      setTax(0);
      setGrandTotal(0);

    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // INCREASE QUANTITY
  // =========================================================

  const increaseQuantity = async (item) => {
    try {
      setUpdatingId(item.cart_id);

      await api.put(
        `/cart/update/${item.cart_id}?quantity=${item.quantity + 1}`
      );

      await loadCart();

    } catch (error) {
      console.error("Increase quantity error:", error);

      alert(
        error.response?.data?.detail ||
        "Unable to increase quantity"
      );

    } finally {
      setUpdatingId(null);
    }
  };

  // =========================================================
  // DECREASE QUANTITY
  // =========================================================

  const decreaseQuantity = async (item) => {
    if (item.quantity <= 1) {
      return;
    }

    try {
      setUpdatingId(item.cart_id);

      await api.put(
        `/cart/update/${item.cart_id}?quantity=${item.quantity - 1}`
      );

      await loadCart();

    } catch (error) {
      console.error("Decrease quantity error:", error);

      alert(
        error.response?.data?.detail ||
        "Unable to decrease quantity"
      );

    } finally {
      setUpdatingId(null);
    }
  };

  // =========================================================
  // REMOVE ITEM
  // =========================================================

  const removeItem = async (cartId) => {
    try {
      setUpdatingId(cartId);

      await api.delete(
        `/cart/remove/${cartId}`
      );

      await loadCart();

    } catch (error) {
      console.error("Remove item error:", error);

      alert(
        error.response?.data?.detail ||
        "Unable to remove item"
      );

    } finally {
      setUpdatingId(null);
    }
  };

  // =========================================================
  // PLACE ORDER
  // =========================================================

  const placeOrder = async () => {
    if (!userId) {
      navigate("/login");
      return;
    }

    if (cartItems.length === 0) {
      alert("Cart is empty");
      return;
    }

    try {
      const response = await api.post(
        `/orders/create?user_id=${userId}`
      );

      const order = response.data?.order;

      if (order) {
        alert(
          `Order placed successfully!\nOrder ID: ${order.id}`
        );

        navigate(`/orders/${order.id}`);

      } else {
        alert("Order placed successfully!");

        navigate("/orders");
      }

    } catch (error) {
      console.error("Place order error:", error);

      alert(
        error.response?.data?.detail ||
        "Failed to place order"
      );
    }
  };

  // =========================================================
  // LOGIN CHECK
  // =========================================================

  if (!userId) {
    return (
      <div className="cart-page">

        <div className="cart-empty">

          <div className="cart-empty-icon">
            🔐
          </div>

          <h2>Please Login</h2>

          <p>
            Login to view your shopping cart.
          </p>

          <button
            onClick={() => navigate("/login")}
          >
            Login
          </button>

        </div>

      </div>
    );
  }

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="cart-page">

        <div className="cart-loading">

          <div className="cart-spinner"></div>

          <h2>
            Loading Cart...
          </h2>

        </div>

      </div>
    );
  }

  // =========================================================
  // CART PAGE
  // =========================================================

  return (
    <div className="cart-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="cart-header">

        <div>

          <span>
            SHOPPING CART
          </span>

          <h1>
            Your Cart
          </h1>

          <p>
            {cartItems.length} item
            {cartItems.length !== 1 ? "s" : ""}
          </p>

        </div>

        <button
          className="continue-shopping"
          onClick={() => navigate("/products")}
        >
          ← Continue Shopping
        </button>

      </div>

      {/* =====================================================
          EMPTY CART
      ===================================================== */}

      {cartItems.length === 0 ? (

        <div className="cart-empty">

          <div className="cart-empty-icon">
            🛒
          </div>

          <h2>
            Your Cart is Empty
          </h2>

          <p>
            Looks like you haven't added anything yet.
          </p>

          <button
            onClick={() => navigate("/products")}
          >
            Start Shopping
          </button>

        </div>

      ) : (

        <div className="cart-layout">

          {/* =================================================
              CART ITEMS
          ================================================= */}

          <div className="cart-items">

            {cartItems.map((item) => (

              <div
                className="cart-item"
                key={item.cart_id}
              >

                {/* PRODUCT IMAGE */}

                <div className="cart-product-image">

                  {item.images ? (

                    <img
                      src={item.images}
                      alt={item.product_name}
                      onError={(e) => {
                        e.currentTarget.style.display =
                          "none";
                      }}
                    />

                  ) : (

                    <span>
                      🛍️
                    </span>

                  )}

                </div>

                {/* PRODUCT DETAILS */}

                <div className="cart-product-info">

                  <span className="cart-product-id">
                    PRODUCT #{item.product_id}
                  </span>

                  <h2>
                    {item.product_name}
                  </h2>

                  <p>
                    Category: {item.category}
                  </p>

                  <strong>
                    ₹
                    {Number(
                      item.price
                    ).toLocaleString("en-IN")}
                  </strong>

                  {/* QUANTITY */}

                  <div className="quantity-section">

                    <button
                      onClick={() =>
                        decreaseQuantity(item)
                      }
                      disabled={
                        item.quantity <= 1 ||
                        updatingId === item.cart_id
                      }
                    >
                      −
                    </button>

                    <span>
                      {item.quantity}
                    </span>

                    <button
                      onClick={() =>
                        increaseQuantity(item)
                      }
                      disabled={
                        updatingId === item.cart_id
                      }
                    >
                      +
                    </button>

                  </div>

                  {/* REMOVE */}

                  <button
                    className="remove-btn"
                    onClick={() =>
                      removeItem(item.cart_id)
                    }
                    disabled={
                      updatingId === item.cart_id
                    }
                  >
                    🗑 Remove
                  </button>

                </div>

                {/* ITEM TOTAL */}

                <div className="cart-item-total">

                  <span>
                    Item Total
                  </span>

                  <strong>
                    ₹
                    {Number(
                      item.item_total
                    ).toLocaleString("en-IN")}
                  </strong>

                </div>

              </div>

            ))}

          </div>

          {/* =================================================
              ORDER SUMMARY
          ================================================= */}

          <div className="cart-summary">

            <h2>
              Order Summary
            </h2>

            <div className="summary-line">

              <span>
                Items
              </span>

              <span>
                {cartItems.length}
              </span>

            </div>

            <div className="summary-line">

              <span>
                Subtotal
              </span>

              <strong>
                ₹
                {cartTotal.toLocaleString("en-IN")}
              </strong>

            </div>

            <div className="summary-line">

              <span>
                Tax (18%)
              </span>

              <strong>
                ₹
                {tax.toLocaleString("en-IN")}
              </strong>

            </div>

            <div className="summary-line">

              <span>
                Delivery
              </span>

              <strong className="free">
                FREE
              </strong>

            </div>

            <hr />

            <div className="summary-total">

              <span>
                Grand Total
              </span>

              <strong>
                ₹
                {grandTotal.toLocaleString("en-IN")}
              </strong>

            </div>

            <button
              className="checkout-btn"
              onClick={placeOrder}
            >
              Place Order →
            </button>

            <div className="secure-cart">
              🔒 Secure Checkout
            </div>

          </div>

        </div>

      )}

    </div>
  );
}

export default Cart;