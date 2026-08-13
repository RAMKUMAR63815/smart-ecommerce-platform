import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import "./Cart.css";

function Cart() {
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  const userId = localStorage.getItem("user_id");

  useEffect(() => {
    if (userId) {
      loadCart();
    } else {
      setLoading(false);
    }
  }, []);

  const loadCart = async () => {
    try {
      setLoading(true);

      const response = await api.get(
        `/cart/?user_id=${userId}`
      );

      console.log("Cart response:", response.data);

      if (
        response.data &&
        Array.isArray(response.data.cart)
      ) {
        setCart(response.data.cart);
      } else {
        setCart([]);
      }
    } catch (error) {
      console.error("Cart error:", error);
      setCart([]);
    } finally {
      setLoading(false);
    }
  };

  const increaseQuantity = async (item) => {
    try {
      await api.put(
        `/cart/update/${item.id}?quantity=${item.quantity + 1}`
      );

      await loadCart();
    } catch (error) {
      alert(
        error.response?.data?.detail ||
        "Unable to increase quantity"
      );
    }
  };

  const decreaseQuantity = async (item) => {
    if (item.quantity <= 1) return;

    try {
      await api.put(
        `/cart/update/${item.id}?quantity=${item.quantity - 1}`
      );

      await loadCart();
    } catch (error) {
      alert(
        error.response?.data?.detail ||
        "Unable to decrease quantity"
      );
    }
  };

  const removeItem = async (cartId) => {
    try {
      await api.delete(`/cart/remove/${cartId}`);

      await loadCart();
    } catch (error) {
      alert(
        error.response?.data?.detail ||
        "Unable to remove item"
      );
    }
  };

  const placeOrder = async () => {
    if (!userId) {
      navigate("/login");
      return;
    }

    if (cart.length === 0) {
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

  const cartTotal = cart.reduce(
    (sum, item) =>
      sum + Number(item.total || 0),
    0
  );

  if (!userId) {
    return (
      <div className="cart-page">
        <div className="cart-empty">
          <div className="cart-empty-icon">🔐</div>
          <h2>Please Login</h2>
          <p>Login to view your shopping cart.</p>

          <button
            onClick={() => navigate("/login")}
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="cart-page">
        <div className="cart-loading">
          <div className="cart-spinner"></div>
          <h2>Loading Cart...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">

      <div className="cart-header">
        <div>
          <span>SHOPPING CART</span>
          <h1>Your Cart</h1>
          <p>
            {cart.length} item{cart.length !== 1 ? "s" : ""}
          </p>
        </div>

        <button
          className="continue-shopping"
          onClick={() => navigate("/products")}
        >
          ← Continue Shopping
        </button>
      </div>

      {cart.length === 0 ? (
        <div className="cart-empty">
          <div className="cart-empty-icon">
            🛒
          </div>

          <h2>Your Cart is Empty</h2>

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

          <div className="cart-items">

            {cart.map((item) => (
              <div
                className="cart-item"
                key={item.id}
              >

                <div className="cart-product-image">
                  {item.image ? (
                    <img
                      src={item.image}
                      alt={item.product_name}
                    />
                  ) : (
                    <span>🛍️</span>
                  )}
                </div>

                <div className="cart-product-info">

                  <span className="cart-product-id">
                    PRODUCT #{item.product_id}
                  </span>

                  <h2>{item.product_name}</h2>

                  <p>
                    {item.description}
                  </p>

                  <strong>
                    ₹{Number(item.price).toLocaleString("en-IN")}
                  </strong>

                  <div className="quantity-section">

                    <button
                      onClick={() =>
                        decreaseQuantity(item)
                      }
                      disabled={item.quantity <= 1}
                    >
                      −
                    </button>

                    <span>{item.quantity}</span>

                    <button
                      onClick={() =>
                        increaseQuantity(item)
                      }
                      disabled={
                        item.quantity >= item.stock
                      }
                    >
                      +
                    </button>

                  </div>

                  <button
                    className="remove-btn"
                    onClick={() =>
                      removeItem(item.id)
                    }
                  >
                    🗑 Remove
                  </button>

                </div>

                <div className="cart-item-total">
                  <span>Total</span>

                  <strong>
                    ₹{Number(item.total).toLocaleString("en-IN")}
                  </strong>
                </div>

              </div>
            ))}

          </div>

          <div className="cart-summary">

            <h2>Order Summary</h2>

            <div className="summary-line">
              <span>Items</span>
              <span>{cart.length}</span>
            </div>

            <div className="summary-line">
              <span>Subtotal</span>
              <strong>
                ₹{cartTotal.toLocaleString("en-IN")}
              </strong>
            </div>

            <div className="summary-line">
              <span>Delivery</span>
              <strong className="free">
                FREE
              </strong>
            </div>

            <hr />

            <div className="summary-total">
              <span>Total</span>
              <strong>
                ₹{cartTotal.toLocaleString("en-IN")}
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