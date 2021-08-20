import os

APP_SECRET_KEY = os.getenv(
    "APP_SECRET_KEY", "9438e1d80dc365bc4609df5e3269a4b01845d587f51cd6d7a222fc0d0e0b809d"
)

APP_ADMIN_KEY = os.getenv("APP_ADMIN_KEY", None)
