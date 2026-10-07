from flask import Flask, abort, redirect, url_for, request, make_response
from html import escape
import csv
import io

app = Flask(__name__)


# =========================
# DỮ LIỆU MẪU
# =========================

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {
            "PMMNM": 8.5,
            "CSDL": 7.0,
            "MMT": 9.0
        }
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {
            "PMMNM": 6.0,
            "CSDL": 5.5,
            "MMT": 7.0
        }
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {
            "PMMNM": 9.5,
            "CSDL": 9.0
        }
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {
            "PMMNM": 4.0,
            "CSDL": 3.5,
            "MMT": 5.0
        }
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {
            "PMMNM": 7.5,
            "MMT": 8.0
        }
    }
}


# =========================
# TÍNH ĐIỂM TRUNG BÌNH
# =========================

def average(scores):
    if not scores:
        return None

    return round(sum(scores.values()) / len(scores), 2)


# =========================
# XẾP LOẠI
# =========================

def rank(avg):
    if avg is None:
        return "Chưa có điểm"

    if avg >= 8.5:
        return "Giỏi"
    elif avg >= 7.0:
        return "Khá"
    elif avg >= 5.0:
        return "Trung bình"
    else:
        return "Yếu"


# =========================
# THÔNG TIN SINH VIÊN
# =========================

def student_summary(mssv):
    student = STUDENTS[mssv]
    avg = average(student["scores"])

    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg)
    }


# =========================
# LAYOUT HTML
# =========================

def layout(title, body):
    safe_title = escape(title)

    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title}</title>
</head>
<body>

    <nav>
        <a href="{url_for('home')}">Trang chủ</a> |
        <a href="{url_for('student_list')}">Sinh viên</a> |
        <a href="{url_for('search')}">Tìm kiếm</a>
    </nav>

    <hr>

    {body}

</body>
</html>
"""


# =========================
# TRANG CHỦ
# =========================
@app.route("/")
def home():
    total_students = len(STUDENTS)
    classes = sorted(set(student["lop"] for student in STUDENTS.values()))

    body = f"""
    <h1>Sổ điểm lớp học</h1>

    <p>Tổng số sinh viên: <strong>{total_students}</strong></p>
    <p>Số lớp: <strong>{len(classes)}</strong></p>

    <ul>
        <li>
            <a href="{url_for('student_list')}">
                Xem danh sách sinh viên
            </a>
        </li>

        <li>
            <a href="{url_for('api_students')}">
                Xem API sinh viên
            </a>
        </li>
    </ul>
    """

    return layout("Trang chủ", body)
# =========================
# DANH SÁCH SINH VIÊN
# =========================

@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip()

    students = []

    for mssv, student in STUDENTS.items():
        if lop_filter:
            if student["lop"].lower() != lop_filter.lower():
                continue

        students.append(student_summary(mssv))

    classes = sorted(set(student["lop"] for student in STUDENTS.values()))

    options = '<option value="">Tất cả</option>'

    for lop in classes:
        selected = ""

        if lop_filter.lower() == lop.lower():
            selected = " selected"

        options += f'<option value="{escape(lop)}"{selected}>{escape(lop)}</option>'

    rows = ""

    for student in students:
        avg = student["average"]

        if avg is None:
            avg_display = "—"
        else:
            avg_display = str(avg)

        rows += f"""
        <tr>
            <td>
                <a href="{url_for('student_detail', mssv=student['mssv'])}">
                    {escape(student['mssv'])}
                </a>
            </td>
            <td>{escape(student['name'])}</td>
            <td>{escape(student['lop'])}</td>
            <td>{avg_display}</td>
            <td>{escape(student['rank'])}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="5">Không có sinh viên phù hợp.</td>
        </tr>
        """

    body = f"""
    <h1>Danh sách sinh viên</h1>

    <form method="get" action="{url_for('student_list')}">
        <label for="lop">Lọc theo lớp:</label>

        <select name="lop" id="lop">
            {options}
        </select>

        <button type="submit">Lọc</button>
    </form>

    <br>

    <table border="1" cellpadding="8">
        <thead>
            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
        </thead>

        <tbody>
            {rows}
        </tbody>
    </table>
    """

    return layout("Danh sách sinh viên", body)


# =========================
# CHI TIẾT SINH VIÊN
# =========================

@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    student = STUDENTS[mssv]
    avg = average(student["scores"])
    student_rank = rank(avg)

    if avg is None:
        avg_display = "—"
    else:
        avg_display = str(avg)

    scores_html = ""

    for course, score in student["scores"].items():
        scores_html += f"""
        <tr>
            <td>{escape(course)}</td>
            <td>{score}</td>
        </tr>
        """

    if not scores_html:
        scores_html = """
        <tr>
            <td colspan="2">Chưa có điểm.</td>
        </tr>
        """

    body = f"""
    <h1>Thông tin sinh viên</h1>

    <p>
        <strong>Họ tên:</strong>
        {escape(student["name"])}
    </p>

    <p>
        <strong>MSSV:</strong>
        {escape(mssv)}
    </p>

    <p>
        <strong>Lớp:</strong>
        <a href="{url_for('student_list', lop=student['lop'])}">
            {escape(student["lop"])}
        </a>
    </p>

    <p>
        <strong>Điểm trung bình:</strong>
        {avg_display}
    </p>

    <p>
        <strong>Xếp loại:</strong>
        {escape(student_rank)}
    </p>

    <h2>Điểm các học phần</h2>

    <table border="1" cellpadding="8">
        <thead>
            <tr>
                <th>Học phần</th>
                <th>Điểm</th>
            </tr>
        </thead>

        <tbody>
            {scores_html}
        </tbody>
    </table>

    <br>

    <a href="{url_for('student_export', mssv=mssv)}">
        Xuất CSV
    </a>
    """

    return layout("Thông tin sinh viên", body)


# =========================
# REDIRECT 301
# =========================

@app.route("/sv/<mssv>")
def old_student_url(mssv):
    return redirect(
        url_for("student_detail", mssv=mssv),
        code=301
    )


# =========================
# EXPORT CSV
# =========================

@app.route("/students/<mssv>/export")
def student_export(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(["hoc_phan", "diem"])

    for course, score in STUDENTS[mssv]["scores"].items():
        writer.writerow([course, score])

    response = make_response("\ufeff" + output.getvalue())

    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=diem_{mssv}.csv"
    )

    return response


# =========================
# TÌM KIẾM
# =========================

@app.route("/search")
def search():
    keyword = request.args.get("q", "")

    keyword_lower = keyword.lower()

    results = []

    for mssv, student in STUDENTS.items():
        if (
            keyword_lower in student["name"].lower()
            or keyword_lower in mssv.lower()
        ):
            results.append(student_summary(mssv))

    rows = ""

    for student in results:
        rows += f"""
        <li>
            <a href="{url_for('student_detail', mssv=student['mssv'])}">
                {escape(student['mssv'])}
            </a>
            -
            {escape(student['name'])}
            -
            {escape(student['lop'])}
        </li>
        """

    if not rows:
        rows = "<li>Không tìm thấy sinh viên phù hợp.</li>"

    body = f"""
    <h1>Tìm kiếm sinh viên</h1>

    <form method="get" action="{url_for('search')}">
        <input
            type="text"
            name="q"
            value="{escape(keyword)}"
            placeholder="Nhập MSSV hoặc họ tên"
        >

        <button type="submit">Tìm kiếm</button>
    </form>

    <p>
        Tìm thấy <strong>{len(results)}</strong> sinh viên.
    </p>

    <ul>
        {rows}
    </ul>
    """

    return layout("Tìm kiếm", body)



# =========================
# PART 2 - JSON API
# =========================

from flask import jsonify


# =========================
# GET /api/students
# =========================

@app.route("/api/students", methods=["GET"])
def api_students():
    lop_filter = request.args.get("lop")

    # Phân biệt:
    # - không truyền min_avg
    # - truyền min_avg nhưng giá trị không hợp lệ
    min_avg_raw = request.args.get("min_avg")

    if min_avg_raw is not None:
        try:
            min_avg = float(min_avg_raw)
        except ValueError:
            return jsonify({
                "error": "Dữ liệu không hợp lệ",
                "detail": "min_avg phải là một số."
            }), 400
    else:
        min_avg = None

    results = []

    for mssv in STUDENTS:
        student = student_summary(mssv)

        # Lọc theo lớp
        if lop_filter:
            if student["lop"].lower() != lop_filter.lower():
                continue

        # Lọc theo điểm trung bình
        if min_avg is not None:
            if student["average"] is None:
                continue

            if student["average"] < min_avg:
                continue

        results.append(student)

    return jsonify(results)


# =========================
# GET /api/students/<mssv>
# =========================

@app.route("/api/students/<mssv>", methods=["GET"])
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    return jsonify(student_summary(mssv))


# =========================
# API ĐIỂM THEO HỌC PHẦN
# =========================

@app.route(
    "/api/students/<mssv>/scores/<course>",
    methods=["GET", "PUT", "DELETE"]
)
def api_student_score(mssv, course):

    # Kiểm tra sinh viên
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    # Chuẩn hóa tên học phần
    course = course.upper()

    scores = STUDENTS[mssv]["scores"]

    # =========================
    # GET
    # =========================

    if request.method == "GET":

        if course not in scores:
            abort(
                404,
                description=(
                    f"Không có điểm học phần {course} "
                    f"của sinh viên {mssv}."
                )
            )

        return jsonify({
            "mssv": mssv,
            "course": course,
            "score": scores[course]
        })


    # =========================
    # PUT
    # =========================

    if request.method == "PUT":

        score_raw = request.args.get("score")

        # Không có score
        if score_raw is None:
            return jsonify({
                "error": "Dữ liệu không hợp lệ",
                "detail": "Thiếu tham số score."
            }), 400

        # Kiểm tra score có phải số không
        try:
            score = float(score_raw)
        except ValueError:
            return jsonify({
                "error": "Dữ liệu không hợp lệ",
                "detail": "score phải là một số."
            }), 400

        # Kiểm tra khoảng điểm
        if score < 0 or score > 10:
            return jsonify({
                "error": "Dữ liệu không hợp lệ",
                "detail": "score phải nằm trong khoảng từ 0 đến 10."
            }), 400

        # Kiểm tra điểm đã tồn tại chưa
        is_new = course not in scores

        # Lưu điểm
        scores[course] = score

        result = {
            "mssv": mssv,
            "course": course,
            "score": score
        }

        # Điểm mới -> 201 + Location
        if is_new:
            response = jsonify(result)

            response.status_code = 201

            response.headers["Location"] = url_for(
                "api_student_score",
                mssv=mssv,
                course=course
            )

            return response

        # Điểm cũ -> 200 + average
        result["average"] = average(scores)

        return jsonify(result), 200


    # =========================
    # DELETE
    # =========================

    if request.method == "DELETE":

        if course not in scores:
            abort(
                404,
                description=(
                    f"Không có điểm học phần {course} "
                    f"của sinh viên {mssv}."
                )
            )

        del scores[course]

        return "", 204
from werkzeug.exceptions import HTTPException


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_http_error(error):
    if error.code == 400:
        title = "Dữ liệu không hợp lệ"
    elif error.code == 404:
        title = "Không tìm thấy"
    else:
        title = "Phương thức không được hỗ trợ"

    detail = error.description

    if request.path.startswith("/api/"):
        return jsonify({
            "error": title,
            "detail": detail
        }), error.code

    body = f"""
    <h1>{error.code} - {escape(title)}</h1>
    <p>{escape(detail)}</p>
    """

    return layout(title, body), error.code




@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_http_error(error):
    if error.code == 400:
        title = "Dữ liệu không hợp lệ"
    elif error.code == 404:
        title = "Không tìm thấy"
    else:
        title = "Phương thức không được hỗ trợ"

    detail = error.description

    if request.path.startswith("/api/"):
        return jsonify({
            "error": title,
            "detail": detail
        }), error.code

    body = f"""
    <h1>{error.code} - {escape(title)}</h1>
    <p>{escape(detail)}</p>
    """

    return layout(title, body), error.code
# =========================
# CHẠY FLASK
# =========================

if __name__ == "__main__":
    app.run(debug=True, port=8000)