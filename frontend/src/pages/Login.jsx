import {
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  useAuth0,
} from "@auth0/auth0-react";

import axios from "axios";

import "./Login.css";


function Login() {

  const navigate =
    useNavigate();


  const [
    email,
    setEmail,
  ] = useState("");


  const [
    password,
    setPassword,
  ] = useState("");


  const [
    error,
    setError,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(false);


  const {
    loginWithRedirect,
    logout,
    isAuthenticated,
    isLoading,
    user,
  } = useAuth0();


  // =====================================================
  // AUTH0 LOADING
  // =====================================================

  if (isLoading) {

    return (

      <div className="login-page">

        <div className="login-loading">

          <div className="spinner"></div>

          <p>
            Loading...
          </p>

        </div>

      </div>

    );

  }


  // =====================================================
  // AUTH0 LOGGED IN
  // =====================================================

  if (isAuthenticated) {

    return (

      <div className="login-page">

        <div className="login-card welcome-card">

          <div className="success-icon">
            ✓
          </div>


          <h1>
            Welcome!
          </h1>


          {user?.picture && (

            <img
              src={user.picture}
              alt="Profile"
              className="profile-image"
            />

          )}


          <h3>
            {user?.name}
          </h3>


          <p className="user-email">
            {user?.email}
          </p>


          <button
            className="login-btn"

            onClick={() =>
              navigate(
                "/products"
              )
            }
          >
            Continue Shopping
          </button>


          <button
            className="logout-btn"

            onClick={() => {

              localStorage.clear();

              logout({
                logoutParams: {
                  returnTo:
                    window.location.origin,
                },
              });

            }}
          >
            Logout
          </button>

        </div>

      </div>

    );

  }


  // =====================================================
  // NORMAL LOGIN
  // =====================================================

  const login =
    async () => {

      if (
        !email ||
        !password
      ) {

        setError(
          "Please enter email and password"
        );

        return;

      }


      try {

        setLoading(true);

        setError("");


        const form =
          new URLSearchParams();


        form.append(
          "username",
          email
        );


        form.append(
          "password",
          password
        );


        const res =
          await axios.post(

            "http://127.0.0.1:8000/auth/login",

            form,

            {
              headers: {

                "Content-Type":
                  "application/x-www-form-urlencoded",

              },
            }

          );


        console.log(
          "Login response:",
          res.data
        );


        const accessToken =
          res.data?.access_token;


        if (!accessToken) {

          setError(
            "Login failed. Access token was not received."
          );

          return;

        }


        // =================================================
        // SAVE TOKENS
        // =================================================

        localStorage.setItem(
          "access_token",
          accessToken
        );


        localStorage.setItem(
          "token",
          accessToken
        );


        if (
          res.data?.refresh_token
        ) {

          localStorage.setItem(
            "refresh_token",
            res.data.refresh_token
          );

        }


        // =================================================
        // GET USER
        // =================================================

        let loggedInUser =
          res.data?.user;


        let userId =
          loggedInUser?.id;


        if (!userId) {

          try {

            const meResponse =
              await axios.get(

                "http://127.0.0.1:8000/auth/me",

                {
                  headers: {

                    Authorization:
                      `Bearer ${accessToken}`,

                  },
                }

              );


            loggedInUser =
              meResponse.data;


            userId =
              loggedInUser?.id;


          }
          catch (meError) {

            console.error(
              "Auth Me error:",
              meError
            );

          }

        }


        // =================================================
        // USER ID REQUIRED FOR NOTIFICATIONS
        // =================================================

        if (!userId) {

          setError(
            "Login successful, but User ID was not received."
          );

          return;

        }


        // =================================================
        // SAVE USER ID
        // =================================================

        localStorage.setItem(
          "user_id",
          String(userId)
        );


        console.log(
          "Logged in user ID:",
          userId
        );


        // =================================================
        // SAVE USER
        // =================================================

        if (loggedInUser) {

          localStorage.setItem(
            "user",
            JSON.stringify(
              loggedInUser
            )
          );


          if (
            loggedInUser.role
          ) {

            localStorage.setItem(
              "user_role",
              loggedInUser.role
            );

          }

        }


        // =================================================
        // LOGIN SUCCESS
        // =================================================

        alert(
          "Login Successful"
        );


        navigate(
          "/products",
          {
            replace: true,
          }
        );


      }
      catch (err) {

        console.error(
          "Login error:",
          err
        );


        if (
          err.response
        ) {

          setError(

            err.response.data?.detail ||

            "Invalid email or password"

          );

        }
        else {

          setError(
            "Cannot connect to server"
          );

        }

      }
      finally {

        setLoading(false);

      }

    };


  // =====================================================
  // PAGE
  // =====================================================

  return (

    <div className="login-page">

      <div className="login-card">

        <div className="brand-icon">
          🛒
        </div>


        <h1>
          Smart Ecommerce
        </h1>


        <p className="login-subtitle">
          Welcome back! Login to continue shopping.
        </p>


        {error && (

          <div className="login-error">
            ⚠ {error}
          </div>

        )}


        {/* EMAIL */}

        <div className="input-group">

          <label>
            Email Address
          </label>


          <input
            type="email"

            placeholder="Enter your email"

            value={email}

            onChange={(e) =>
              setEmail(
                e.target.value
              )
            }

          />

        </div>


        {/* PASSWORD */}

        <div className="input-group">

          <label>
            Password
          </label>


          <input
            type="password"

            placeholder="Enter your password"

            value={password}

            onChange={(e) =>
              setPassword(
                e.target.value
              )
            }

            onKeyDown={(e) => {

              if (
                e.key ===
                "Enter"
              ) {

                login();

              }

            }}

          />

        </div>


        {/* LOGIN */}

        <button
          className="login-btn"

          onClick={login}

          disabled={loading}
        >

          {loading ? (

            <>

              <span className="button-spinner"></span>

              Logging in...

            </>

          ) : (

            "Login"

          )}

        </button>


        {/* DIVIDER */}

        <div className="divider">

          <span>
            OR
          </span>

        </div>


        {/* GOOGLE */}

        <button
          className="google-btn"

          onClick={() =>
            loginWithRedirect()
          }
        >

          <span className="google-logo">
            G
          </span>

          Continue with Google

        </button>


        {/* REGISTER */}

        <div className="register-section">

          <span>
            Don't have an account?
          </span>


          <button
            onClick={() =>
              navigate(
                "/register"
              )
            }
          >
            Create Account
          </button>

        </div>

      </div>

    </div>

  );

}


export default Login;