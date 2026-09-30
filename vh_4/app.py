# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from markupsafe import escape

app = Flask(__name__)

# 1. Khai báo danh sách BOOKS >= 4 cuốn đầy đủ thuộc tính
BOOKS = [
    {"id": 1, "title": "Lập Trình Python Căn Bản", "author": "Nguyễn Văn A", "year": 2021, "category": "Lập trình", "available": True},
    {"id": 2, "title": "Flask Web Development", "author": "Miguel Grinberg", "year": 2018, "category": "Lập trình", "available": False},
    {"id": 3, "title": "Cấu Trúc Dữ Liệu & Giải Thuật", "author": "Trần Thị B", "year": 2020, "category": "Khoa học máy tính", "available": True},
    {"id": 4, "title": "Hệ Quản Trị Cơ Sở Dữ Liệu", "author": "Lê Văn C", "year": 2019, "category": "Cơ sở dữ liệu", "available": True},
    {"id": 5, "title": "Thiết Kế Web Với HTML/CSS", "author": "Phạm Văn D", "year": 2022, "category": "Lập trình", "available": True},
]

# 2. Route Trang chủ /
@app.route("/")
def index():
    total_books = len(BOOKS)
    available_books = sum(1 for b in BOOKS if b["available"])
    return render_template("index.html", total=total_books, available=available_books)

# 3. Route /books : Bảng sách, thanh lọc theo thể loại
@app.route("/books")
def books_list():
    category = request.args.get("category")
    # Lấy danh sách thể loại không trùng lặp để làm thanh lọc
    categories = sorted(list(set(b["category"] for b in BOOKS)))
    
    filtered_books = BOOKS
    if category:
        filtered_books = [b for b in BOOKS if b["category"].lower() == category.lower()]
        
    return render_template("books.html", books=filtered_books, categories=categories, selected_category=category)

# 4. Route /books/<int:book_id> : Trang chi tiết sách
@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        msg = f"Không có sách với ID = {escape(str(book_id))}"
        return render_template("404.html", message=msg), 404
    return render_template("detail.html", book=book)

# 5. Route API: /api/books và /api/books/<int:book_id>
@app.route("/api/books")
def api_books():
    return jsonify(BOOKS)

@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book)

# 6. Trang 404 tuỳ biến có menu chung
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", message="Trang bạn truy cập không tồn tại."), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)