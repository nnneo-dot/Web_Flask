# 簡易會員系統

1132 Web 程式設計 - 第 2 次小考

## 功能說明

- **首頁 `/`**：顯示系統簡介，提供登入與註冊連結。
- **註冊 `/register`**：填寫帳號、Email、密碼、電話、出生日期並完成後端驗證後加入會員。
- **登入 `/login`**：以 Email + 密碼登入，成功導向歡迎頁。
- **歡迎頁 `/welcome/<username>`**：顯示登入會員的個人資料。
- **會員清單 `/users`**：以表格列出所有會員（電話遮蔽、日期顯示民國年、密碼不顯示）。
- **錯誤頁 `/error`**：統一顯示錯誤訊息。

## 專案結構

```
project/
├── app.py
├── requirements.txt
├── users.json          # 首次執行自動建立
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── welcome.html
│   ├── users.html
│   └── error.html
└── static/
    └── css/
        └── style.css
```

## 安裝與執行

```bash
pip install -r requirements.txt
flask --debug run
```

瀏覽器開啟 [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 預設帳號

| Email | 密碼 |
|---|---|
| admin@example.com | admin123 |
