import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import "./Products.css";

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addingId, setAddingId] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await api.get("/products/");

      setProducts(
        Array.isArray(response.data)
          ? response.data
          : []
      );
    } catch (error) {
      console.error("Products error:", error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId) => {
    try {
      const userId = localStorage.getItem("user_id");

      if (!userId) {
        alert("Please login first");
        navigate("/login");
        return;
      }

      setAddingId(productId);

      await api.post(
        `/cart/add?user_id=${userId}&product_id=${productId}&quantity=1`
      );

      alert("Product added to cart");

      await loadProducts();

    } catch (error) {
      console.error("Add cart error:", error);

      alert(
        error.response?.data?.detail ||
        "Failed to add product to cart"
      );
    } finally {
      setAddingId(null);
    }
  };

  if (loading) {
    return (
      <div className="products-page">
        <div className="products-loading">
          <div className="products-spinner"></div>
          <h2>Loading Products...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="products-page">

      <div className="products-header">

        <div>
          <span className="page-label">
            SMART ECOMMERCE
          </span>

          <h1>Our Products</h1>

          <p>
            Discover products you'll love.
          </p>
        </div>

        <button
          className="cart-top-btn"
          onClick={() => navigate("/cart")}
        >
          🛒 View Cart
        </button>

      </div>

      {products.length === 0 ? (
        <div className="empty-products">
          <div>📦</div>
          <h2>No Products Available</h2>
          <p>Please check again later.</p>
        </div>
      ) : (
        <div className="product-grid">

          {products.map((product) => (

            <div
              className="product-card"
              key={product.id}
            >

              <div className="product-image">
                {product.image ? (
                  <img
                    src={product.image}
                    alt={product.name}
                    onError={(e) => {
                      e.currentTarget.style.display =
                        "none";
                    }}
                  />
                ) : (
                  <span>🛍️</span>
                )}
              </div>

              <div className="product-content">

                <span className="product-id">
                  PRODUCT #{product.id}
                </span>

                <h2>{product.name}</h2>

                <p className="product-description">
                  {product.description ||
                    "No description available."}
                </p>

                <div className="product-price">
                  ₹{Number(product.price).toLocaleString("en-IN")}
                </div>

                <div className="stock-row">

                  {product.stock > 0 ? (
                    <span className="in-stock">
                      ● In Stock ({product.stock})
                    </span>
                  ) : (
                    <span className="out-stock">
                      ● Out of Stock
                    </span>
                  )}

                </div>

                <button
                  className="add-cart-btn"
                  disabled={
                    product.stock <= 0 ||
                    addingId === product.id
                  }
                  onClick={() =>
                    addToCart(product.id)
                  }
                >
                  {addingId === product.id
                    ? "Adding..."
                    : product.stock <= 0
                    ? "Out of Stock"
                    : "🛒 Add to Cart"}
                </button>

              </div>

            </div>

          ))}

        </div>
      )}

    </div>
  );
}

export default Products;