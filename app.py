"""
簡易會員系統 - Flask Web Application
1132 Web 程式設計 - 第 2 次小考
"""

import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

USERS_FILE = "users.json"

DEFAULT_DATA = {
    "users": [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "phone": "0912345678",
            "birthdate": "1990-01-01"
        }
    ]
}


# ─────────────────────── 輔助函式 ───────────────────────

def init_json_file(file_path: str) -> None:
    """若 JSON 檔不存在，則建立並寫入預設資料。"""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=2)


def read_users(file_path: str) -> dict:
    """讀取 JSON 檔案並回傳使用者資料字典；讀取失敗則回傳預設空結構。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": []}
    except json.JSONDecodeError:
        return {"users": []}


def save_users(file_path: str, data: dict) -> bool:
    """將使用者資料寫入 JSON 檔案；成功回傳 True，失敗回傳 False。"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def validate_register(form_data: dict, users: list) -> dict:
    """
    驗證註冊表單資料。

    Args:
        form_data: 包含 username, email, password, phone, birthdate 的字典。
        users: 現有使用者清單。

    Returns:
        成功: {"success": True, "data": {...}}
        失敗: {"success": False, "error": "錯誤訊息"}
    """
    username = form_data.get("username", "").strip()
    email = form_data.get("email", "").strip()
    password = form_data.get("password", "").strip()
    phone = form_data.get("phone", "").strip()
    birthdate = form_data.get("birthdate", "").strip()

    # 必填欄位
    if not username:
        return {"success": False, "error": "帳號為必填欄位。"}
    if not email:
        return {"success": False, "error": "Email 為必填欄位。"}
    if not password:
        return {"success": False, "error": "密碼為必填欄位。"}
    if not birthdate:
        return {"success": False, "error": "出生日期為必填欄位。"}

    # Email 格式
    if "@" not in email or "." not in email:
        return {"success": False, "error": "Email 格式不正確，必須包含 @ 與 .。"}

    # 密碼長度
    if not (6 <= len(password) <= 16):
        return {"success": False, "error": "密碼長度需介於 6～16 字元。"}

    # 電話（選填）
    if phone:
        if len(phone) != 10 or not phone.isdigit() or not phone.startswith("09"):
            return {"success": False, "error": "電話格式不正確，需為 10 碼數字且開頭為 09。"}

    # 重複帳號或 Email
    for user in users:
        if user["username"] == username:
            return {"success": False, "error": f"帳號「{username}」已被使用。"}
        if user["email"] == email:
            return {"success": False, "error": f"Email「{email}」已被使用。"}

    return {
        "success": True,
        "data": {
            "username": username,
            "email": email,
            "password": password,
            "phone": phone,
            "birthdate": birthdate
        }
    }


def verify_login(email: str, password: str, users: list) -> dict:
    """
    驗證登入的 Email 與密碼。

    Args:
        email: 使用者輸入的 Email。
        password: 使用者輸入的密碼。
        users: 現有使用者清單。

    Returns:
        成功: {"success": True, "data": {...}}
        失敗: {"success": False, "error": "錯誤訊息"}
    """
    email = email.strip()
    password = password.strip()

    if not email or not password:
        return {"success": False, "error": "Email 與密碼不得為空。"}

    for user in users:
        if user["email"] == email and user["password"] == password:
            return {"success": True, "data": user}

    return {"success": False, "error": "Email 或密碼錯誤，請重新輸入。"}


# ─────────────────────── 自訂過濾器 ───────────────────────

@app.template_filter("mask_phone")
def mask_phone(phone: str) -> str:
    """遮蔽電話號碼中間四碼，例如 0912345678 → 0912****78。"""
    if not phone or len(phone) < 6:
        return phone
    return phone[:4] + "*" * (len(phone) - 6) + phone[-2:]


@app.template_filter("format_tw_date")
def format_tw_date(date_str: str) -> str:
    """將西元日期字串（YYYY-MM-DD）轉換為民國年格式（民國 YYY 年 MM 月 DD 日）。"""
    try:
        parts = date_str.split("-")
        year = int(parts[0]) - 1911
        month = int(parts[1])
        day = int(parts[2])
        return f"民國 {year} 年 {month:02d} 月 {day:02d} 日"
    except (ValueError, IndexError, AttributeError):
        return date_str


# ─────────────────────── 初始化（模組層級）───────────────────────

init_json_file(USERS_FILE)


# ─────────────────────── 路由 ───────────────────────

@app.route("/")
def index():
    """首頁：顯示系統標題與簡介，提供登入、註冊連結。"""
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register_route():
    """
    GET：顯示註冊表單。
    POST：驗證並儲存新會員，成功導向登入頁，失敗導向錯誤頁。
    """
    if request.method == "POST":
        form_data = {
            "username": request.form.get("username", "").strip(),
            "email": request.form.get("email", "").strip(),
            "password": request.form.get("password", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "birthdate": request.form.get("birthdate", "").strip(),
        }
        data = read_users(USERS_FILE)
        result = validate_register(form_data, data["users"])

        if not result["success"]:
            return redirect(url_for("error_route", message=result["error"]))

        data["users"].append(result["data"])
        if not save_users(USERS_FILE, data):
            return redirect(url_for("error_route", message="儲存資料時發生錯誤，請稍後再試。"))

        return redirect(url_for("login_route"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_route():
    """
    GET：顯示登入表單。
    POST：驗證 Email 與密碼，成功導向歡迎頁，失敗導向錯誤頁。
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        data = read_users(USERS_FILE)
        result = verify_login(email, password, data["users"])

        if not result["success"]:
            return redirect(url_for("error_route", message=result["error"]))

        username = result["data"]["username"]
        return redirect(url_for("welcome_route", username=username))

    return render_template("login.html")


@app.route("/welcome/<username>")
def welcome_route(username: str):
    """歡迎頁：依 URL 中的 username 從 JSON 查詢並顯示該會員資料。"""
    data = read_users(USERS_FILE)
    user = next((u for u in data["users"] if u["username"] == username), None)

    if user is None:
        return redirect(url_for("error_route", message=f"找不到使用者「{username}」。"))

    return render_template("welcome.html", user=user)


@app.route("/users")
def users_list_route():
    """會員清單：讀取 JSON 並以表格列出所有會員（密碼欄位不顯示）。"""
    data = read_users(USERS_FILE)
    return render_template("users.html", users=data["users"])


@app.route("/error")
def error_route():
    """錯誤頁：接收 message 參數並顯示，提供返回前一頁與首頁連結。"""
    message = request.args.get("message", "發生未知錯誤。")
    return render_template("error.html", message=message)


# ─────────────────────── 啟動 ───────────────────────

if __name__ == "__main__":
    app.run(debug=True)
