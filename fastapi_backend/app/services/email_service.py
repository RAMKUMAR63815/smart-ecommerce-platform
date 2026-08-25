
import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


SMTP_SERVER = os.getenv(
    "SMTP_SERVER",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")


# =========================================================
# SEND EMAIL
# =========================================================

def send_email(
    to_email: str,
    subject: str,
    body: str
):

    print("\n========================================")
    print("EMAIL SERVICE STARTED")
    print("========================================")

    # -----------------------------------------------------
    # CHECK EMAIL CONFIGURATION
    # -----------------------------------------------------

    if not EMAIL or not PASSWORD:

        print("❌ EMAIL CONFIGURATION MISSING")

        raise Exception(
            "Email configuration is missing in .env"
        )

    print("SMTP Server :", SMTP_SERVER)
    print("SMTP Port   :", SMTP_PORT)
    print("From        :", EMAIL)
    print("To          :", to_email)
    print("Subject     :", subject)

    # -----------------------------------------------------
    # CREATE EMAIL
    # -----------------------------------------------------

    msg = MIMEMultipart()

    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    msg.attach(
        MIMEText(
            body,
            "plain"
        )
    )

    server = None

    try:

        # -------------------------------------------------
        # CONNECT TO SMTP
        # -------------------------------------------------

        print("Connecting to SMTP server...")

        server = smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=15
        )
        server.set_debuglevel(1)

        print("✅ SMTP connection successful")

        # -------------------------------------------------
        # START TLS
        # -------------------------------------------------

        print("Starting TLS...")

        server.starttls()

        print("✅ TLS started successfully")

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        print("Logging into email account...")

        server.login(
            EMAIL,
            PASSWORD
        )

        print("✅ Email login successful")

        # -------------------------------------------------
        # SEND EMAIL
        # -------------------------------------------------

        print("Sending email...")

        server.sendmail(
            EMAIL,
            to_email,
            msg.as_string()
        )

        print("========================================")
        print("✅ EMAIL SENT SUCCESSFULLY")
        print("========================================")

        return True

    except Exception as e:

        print("========================================")
        print("❌ EMAIL SENDING FAILED")
        print("Error Type :", type(e).__name__)
        print("Error      :", str(e))
        print("========================================")

        raise

    finally:

        # -------------------------------------------------
        # CLOSE SMTP CONNECTION
        # -------------------------------------------------

        if server:

            try:

                server.quit()

                print("SMTP connection closed")

            except Exception:
                pass

