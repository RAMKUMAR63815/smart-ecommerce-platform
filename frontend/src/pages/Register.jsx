import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import "./Register.css";

function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const register = async () => {
    if (!name || !email || !password) {
      alert("Please fill all fields");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post("/auth/register", {
        name,
        email,
        password,
      });

      console.log("Register response:", response.data);

      alert("Registration Successful");

      navigate("/login");

    } catch (err) {
      console.error("Registration error:", err);

      alert(
        err.response?.data?.detail ||
        "Registration Failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">

      <div className="register-card">

        <div className="register-icon">
          👤
        </div>

        <h1>Create Account</h1>

        <p className="register-subtitle">
          Join Smart Ecommerce today
        </p>

        <div className="register-group">
          <label>Full Name</label>

          <input
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div className="register-group">
          <label>Email Address</label>

          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="register-group">
          <label>Password</label>

          <input
            type="password"
            placeholder="Create a password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button
          className="register-submit"
          onClick={register}
          disabled={loading}
        >
          {loading ? "Creating Account..." : "Create Account"}
        </button>

        <div className="login-link">
          <span>Already have an account?</span>

          <button onClick={() => navigate("/login")}>
            Login
          </button>
        </div>

      </div>

    </div>
  );
}

export default Register;