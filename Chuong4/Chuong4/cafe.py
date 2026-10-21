from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# --- DỮ LIỆU BÀI 1 & BÀI 2 ---
SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê Lợi, Huế",
    "open": 7,
    "close": 22,
}

PROMOTIONS = ["Giảm 10% cho sinh viên", "Mua 2 tặng 1 vào thứ Hai"]

MENU = [
    {"name": "cà phê đen", "price": 20000, "available": True},
    {"name": "bạc xỉu", "price": 30000, "available": False},
    {"name": "cà phê sữa", "price": 25000, "available": True},
    {"name": "trà đào", "price": 35000, "available": True},
    {"name": "matcha latte", "price": 40000, "available": True},
]


# --- FILTER TỰ VIẾT ĐỊNH DẠNG TIỀN (BÀI 2) ---
@app.template_filter("vnd")
def vnd_filter(value):
    if value is None:
        return "0 đ"
    return f"{int(value):,}".replace(",", ".") + " đ"


# --- ROUTE XỬ LÝ CHUNG (BÀI 1 & BÀI 2) ---
@app.route("/")
@app.route("/menu")
def index():
    # 1. Xử lý giờ mở/đóng cửa (Bài 1)
    gio_param = request.args.get("gio")
    if gio_param is not None and gio_param.isdigit():
        current_hour = int(gio_param)
    else:
        current_hour = datetime.now().hour

    is_open = SHOP["open"] <= current_hour < SHOP["close"]

    # 2. Xử lý thống kê thực đơn (Bài 2)
    total_items = len(MENU)
    if total_items > 0:
        available_count = sum(1 for item in MENU if item["available"])
        avg_price = sum(item["price"] for item in MENU) / total_items
    else:
        available_count = 0
        avg_price = 0

    return render_template(
        "index.html",
        shop=SHOP,
        promotions=PROMOTIONS,
        current_hour=current_hour,
        is_open=is_open,
        menu=MENU,
        total_items=total_items,
        available_count=available_count,
        avg_price=avg_price,
    )


if __name__ == "__main__":
    app.run(debug=True)