import math
from flask import Flask, abort, render_template, request

app = Flask(__name__)

SHOP = {
    "name": "Sông Hương",
    "address": "12 Lê Lợi, Huế",
    "phone": "0234 3888 999",
}

# Danh sách thực đơn 7 món
MENU = [
    {"id": 1, "name": "Cà phê đen", "price": 20000, "image": "ca-phe-den.jpg"},
    {"id": 2, "name": "Cà phê sữa", "price": 25000, "image": "ca-phe-sua.jpg"},
    {"id": 3, "name": "Bạc xỉu", "price": 30000, "image": "bac-xiu.jpg"},
    {"id": 4, "name": "Trà đào", "price": 35000, "image": "tra-dao.jpg"},
    {"id": 5, "name": "Trà sữa", "price": 35000, "image": "tra-sua.jpg"},
    {"id": 6, "name": "Nước cam", "price": 30000, "image": "nuoc-cam.jpg"},
    {"id": 7, "name": "Sinh tố bơ", "price": 40000, "image": "sinh-to-bo.jpg"},
]

PER_PAGE = 3  # Số món hiển thị trên mỗi trang


@app.template_filter("vnd")
def vnd_filter(value):
    if value is None:
        return "0 đ"
    return f"{int(value):,}".replace(",", ".") + " đ"


@app.route("/")
def index():
    return render_template("index.html", shop=SHOP)


@app.route("/menu")
def show_menu():
    page_param = request.args.get("page", "1")

    # Xử lý /menu?page=abc -> Chuyển về trang 1
    if not page_param.isdigit():
        page = 1
    else:
        page = int(page_param)

    total_items = len(MENU)
    total_pages = math.ceil(total_items / PER_PAGE)

    # Xử lý /menu?page=0 hoặc /menu?page=4 -> Báo lỗi 404
    if page < 1 or (total_pages > 0 and page > total_pages):
        abort(404)

    # Cắt danh sách món theo trang
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    items_on_page = MENU[start:end]

    return render_template(
        "menu.html",
        shop=SHOP,
        items=items_on_page,
        page=page,
        pages=total_pages,
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", shop=SHOP)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", shop=SHOP), 404


if __name__ == "__main__":
    app.run(debug=True)