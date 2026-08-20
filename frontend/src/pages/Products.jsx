import {
  useEffect,
  useState
} from "react";

import {
  useNavigate
} from "react-router-dom";

import api from "../api/api";

import "./Products.css";

function Products() {

  const [products, setProducts] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [addingId, setAddingId] =
    useState(null);

  const [category, setCategory] =
    useState("");

  const [minPrice, setMinPrice] =
    useState("");

  const [maxPrice, setMaxPrice] =
    useState("");

  const [minPopularity, setMinPopularity] =
    useState("");

  const [inStock, setInStock] =
    useState("");

  const navigate =
    useNavigate();

  // =========================================================
  // LOAD PRODUCTS
  // =========================================================

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {

    try {

      setLoading(true);

      const params =
        new URLSearchParams();

      if (category.trim()) {
        params.append(
          "category",
          category.trim()
        );
      }

      if (minPrice !== "") {
        params.append(
          "min_price",
          minPrice
        );
      }

      if (maxPrice !== "") {
        params.append(
          "max_price",
          maxPrice
        );
      }

      if (minPopularity !== "") {
        params.append(
          "min_popularity",
          minPopularity
        );
      }

      if (inStock !== "") {
        params.append(
          "in_stock",
          inStock
        );
      }

      const queryString =
        params.toString();

      const url =
        queryString
          ? `/products/?${queryString}`
          : "/products/";

      const response =
        await api.get(url);

      setProducts(
        Array.isArray(
          response.data
        )
          ? response.data
          : []
      );

    } catch (error) {

      console.error(
        "Products error:",
        error
      );

      setProducts([]);

    } finally {

      setLoading(false);

    }
  };

  // =========================================================
  // FILTERS
  // =========================================================

  const applyFilters = () => {
    loadProducts();
  };

  const clearFilters = () => {

    setCategory("");
    setMinPrice("");
    setMaxPrice("");
    setMinPopularity("");
    setInStock("");

    setTimeout(() => {
      loadProducts();
    }, 0);
  };

  // =========================================================
  // ADD TO CART
  // =========================================================

  const addToCart = async (
    productId
  ) => {

    try {

      const userId =
        localStorage.getItem(
          "user_id"
        );

      if (!userId) {

        alert(
          "Please login first"
        );

        navigate("/login");

        return;
      }

      setAddingId(productId);

      await api.post(
        `/cart/add?user_id=${userId}&product_id=${productId}&quantity=1`
      );

      alert(
        "Product added to cart"
      );

      await loadProducts();

    } catch (error) {

      console.error(
        "Add cart error:",
        error
      );

      alert(
        error.response?.data?.detail ||
        "Failed to add product to cart"
      );

    } finally {

      setAddingId(null);

    }
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {

    return (

      <div className="products-page">

        <div className="products-loading">

          <div className="products-spinner"></div>

          <h2>
            Loading Products...
          </h2>

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

          <h1>
            Our Products
          </h1>

          <p>
            Discover products you'll love.
          </p>

        </div>

        <button
          className="cart-top-btn"
          onClick={() =>
            navigate("/cart")
          }
        >
          🛒 View Cart
        </button>

      </div>

      <div className="product-filters">

        <div className="filter-group">

          <label>
            Category
          </label>

          <input
            type="text"
            placeholder="Example: phone"
            value={category}
            onChange={(e) =>
              setCategory(
                e.target.value
              )
            }
          />

        </div>

        <div className="filter-group">

          <label>
            Min Price
          </label>

          <input
            type="number"
            min="0"
            placeholder="₹ Min"
            value={minPrice}
            onChange={(e) =>
              setMinPrice(
                e.target.value
              )
            }
          />

        </div>

        <div className="filter-group">

          <label>
            Max Price
          </label>

          <input
            type="number"
            min="0"
            placeholder="₹ Max"
            value={maxPrice}
            onChange={(e) =>
              setMaxPrice(
                e.target.value
              )
            }
          />

        </div>

        <div className="filter-group">

          <label>
            Min Popularity
          </label>

          <input
            type="number"
            min="0"
            placeholder="Popularity"
            value={minPopularity}
            onChange={(e) =>
              setMinPopularity(
                e.target.value
              )
            }
          />

        </div>

        <div className="filter-group">

          <label>
            Stock
          </label>

          <select
            value={inStock}
            onChange={(e) =>
              setInStock(
                e.target.value
              )
            }
          >

            <option value="">
              All
            </option>

            <option value="true">
              In Stock
            </option>

            <option value="false">
              Out of Stock
            </option>

          </select>

        </div>

        <button
          className="filter-btn"
          onClick={applyFilters}
        >
          Apply Filters
        </button>

        <button
          className="clear-filter-btn"
          onClick={clearFilters}
        >
          Clear
        </button>

      </div>

      <div className="product-result-info">

        Showing{" "}

        <strong>
          {products.length}
        </strong>{" "}

        product
        {products.length !== 1
          ? "s"
          : ""}

      </div>

      {products.length === 0 ? (

        <div className="empty-products">

          <div>
            📦
          </div>

          <h2>
            No Products Found
          </h2>

          <p>
            Try changing your filters.
          </p>

          <button
            onClick={clearFilters}
          >
            Clear Filters
          </button>

        </div>

      ) : (

        <div className="product-grid">

          {products.map(
            (product) => (

              <div
                className="product-card"
                key={product.id}
              >

                <div className="product-image">

                  {product.images ? (

                    <img
                      src={product.images}
                      alt={product.name}
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

                <div className="product-content">

                  <span className="product-id">
                    PRODUCT #{product.id}
                  </span>

                  <h2>
                    {product.name}
                  </h2>

                  <p className="product-description">
                    {product.description ||
                      "No description available."}
                  </p>

                  <div className="product-category">

                    Category:{" "}

                    <strong>
                      {product.category}
                    </strong>

                  </div>

                  <div className="product-price">

                    ₹
                    {Number(
                      product.price
                    ).toLocaleString(
                      "en-IN"
                    )}

                  </div>

                  <div className="product-popularity">

                    ⭐ Popularity:{" "}

                    {product.popularity ||
                      0}

                  </div>

                  <div className="stock-row">

                    {product.stock > 0 ? (

                      <span className="in-stock">

                        ● In Stock (
                        {product.stock}
                        )

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
                      addingId ===
                        product.id
                    }
                    onClick={() =>
                      addToCart(
                        product.id
                      )
                    }
                  >

                    {addingId ===
                    product.id
                      ? "Adding..."
                      : product.stock <=
                          0
                      ? "Out of Stock"
                      : "🛒 Add to Cart"}

                  </button>

                </div>

              </div>

            )
          )}

        </div>

      )}

    </div>
  );
}

export default Products;