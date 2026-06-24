def validate_auth_form(form):
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()

    if not username:
        raise ValueError("Username is required.")
    if not password:
        raise ValueError("Password is required.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")

    return {"username": username, "password": password}
