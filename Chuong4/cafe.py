from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# Dữ liệu quán cà phê theo yêu cầu đề bài
SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê Lợi, Huế",
    "open": 7,
    "close": 22,
}

PROMOTIONS = ["Giảm 10% cho sinh viên", "Mua 2 tặng 1 vào thứ Hai"]


@app.route("/")
def index():
    # Lấy tham số 'gio' trên URL (ví dụ: /?gio=9)
    gio_param = request.args.get("gio")

    # Nếu có truyền tham số ?gio= và là số nguyên thì dùng, ngược lại lấy giờ thực tế từ máy
    if gio_param is not None and gio_param.isdigit():
        current_hour = int(gio_param)
    else:
        current_hour = datetime.now().hour

    # Quán mở từ giờ 'open' đến trước giờ 'close' (open <= giờ < close)
    # Ví dụ: 7h là mở, 22h tính là đóng
    is_open = SHOP["open"] <= current_hour < SHOP["close"]

    return render_template(
        "index.html",
        shop=SHOP,
        promotions=PROMOTIONS,
        current_hour=current_hour,
        is_open=is_open,
    )


if __name__ == "__main__":
    app.run(debug=True)