import { useAuth0 } from "@auth0/auth0-react";

function Login() {

  const {
    loginWithRedirect,
    logout,
    isAuthenticated,
    isLoading,
    user
  } = useAuth0();


  // =========================
  // LOADING
  // =========================

  if (isLoading) {

    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          background: "#f5f7fb"
        }}
      >

        <h2>
          Loading...
        </h2>

      </div>
    );

  }


  // =========================
  // LOGGED IN
  // =========================

  if (isAuthenticated) {

    return (

      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          background: "#f5f7fb"
        }}
      >

        <div
          style={{
            width: "400px",
            padding: "40px",
            background: "white",
            borderRadius: "12px",
            boxShadow: "0 5px 25px rgba(0,0,0,0.1)",
            textAlign: "center"
          }}
        >

          <h1>
            Welcome
          </h1>

          {user?.picture && (

            <img
              src={user.picture}
              alt="Profile"
              style={{
                width: "80px",
                height: "80px",
                borderRadius: "50%",
                marginBottom: "15px"
              }}
            />

          )}

          <h3>
            {user?.name}
          </h3>

          <p>
            {user?.email}
          </p>

          <button
            onClick={() =>
              logout({
                logoutParams: {
                  returnTo: window.location.origin
                }
              })
            }
            style={{
              marginTop: "20px",
              padding: "12px 25px",
              border: "none",
              borderRadius: "6px",
              background: "#dc3545",
              color: "white",
              cursor: "pointer",
              fontSize: "16px"
            }}
          >
            Logout
          </button>

        </div>

      </div>

    );

  }


  // =========================
  // LOGIN PAGE
  // =========================

  return (

    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f5f7fb"
      }}
    >

      <div
        style={{
          width: "400px",
          padding: "40px",
          background: "white",
          borderRadius: "12px",
          boxShadow: "0 5px 25px rgba(0,0,0,0.1)",
          textAlign: "center"
        }}
      >

        <h1>
          Smart Ecommerce
        </h1>

        <p>
          Login to continue
        </p>


        <button
          onClick={() => loginWithRedirect()}
          style={{
            width: "100%",
            padding: "14px",
            marginTop: "20px",
            border: "1px solid #ddd",
            borderRadius: "6px",
            background: "white",
            cursor: "pointer",
            fontSize: "16px"
          }}
        >

          🔐 Continue with Google

        </button>

      </div>

    </div>

  );
}

export default Login;