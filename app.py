from flask import Flask, render_template, request, make_response
from xhtml2pdf import pisa
from io import BytesIO
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resume.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.secret_key = "my_admin_secret_key"

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)






class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    heading = db.Column(db.String(100))
    name = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    house_no = db.Column(db.String(200))
    landmark = db.Column(db.String(200))
    area = db.Column(db.String(200))
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    objective = db.Column(db.Text)
    qualification = db.Column(db.String(100))
    board = db.Column(db.String(100))
    year = db.Column(db.String(20))
    percentage = db.Column(db.String(20))
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    gender = db.Column(db.String(20))
    father_name = db.Column(db.String(100))
    dob = db.Column(db.String(50))
    language = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    marital_status = db.Column(db.String(50))
    place = db.Column(db.String(100))
    photo_path = db.Column(db.String(200))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create-resume")
def create_resume():
    return render_template("resume.html")

@app.route("/create-biodata")
def create_biodata():
    return render_template("biodata.html")

@app.route("/courses")
def courses():
    return render_template("courses.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms_conditions.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/preview", methods=["POST"])
def preview():
    data = request.form
    photo = request.files.get("photo")
    photo_path = ""

    if photo and photo.filename:
        photo_path = os.path.join("static/uploads", photo.filename)
        photo.save(photo_path)

    return render_template(
        "preview.html",
        data=data,
        photo_path=photo_path
    )


    resume = Resume(
        user_id=session["user_id"],
        heading=data.get("heading"),
        name=data.get("name"),
        job_title=data.get("job_title"),
        house_no=data.get("house_no"),
        landmark=data.get("landmark"),
        area=data.get("area"),
        city=data.get("city"),
        pincode=data.get("pincode"),
        phone=data.get("phone"),
        email=data.get("email"),
        objective=data.get("objective"),
        qualification=data.get("qualification"),
        board=data.get("board"),
        year=data.get("year"),
        percentage=data.get("percentage"),
        skills=data.get("skills"),
        experience=data.get("experience"),
        gender=data.get("gender"),
        father_name=data.get("father_name"),
        dob=data.get("dob"),
        language=data.get("language"),
        nationality=data.get("nationality"),
        marital_status=data.get("marital_status"),
        place=data.get("place"),
        photo_path=photo_path
    )

    db.session.add(resume)
    db.session.commit()

    return render_template(
        "preview.html",
        data=data,
        photo_path=photo_path,
        resume_id=resume.id
    )



@app.route("/create-db")
def create_db():
    db.create_all()
    return "Database created successfully"


@app.route("/resumes")
def resumes():
    if not session.get("user_logged_in"):
        return redirect("/login")

    all_resumes = Resume.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template("saved_resume.html", resumes=all_resumes)

def resume_to_form_data(resume):
    return {
        "heading": resume.heading,
        "name": resume.name,
        "job_title": resume.job_title,
        "house_no": resume.house_no,
        "landmark": resume.landmark,
        "area": resume.area,
        "city": resume.city,
        "pincode": resume.pincode,
        "phone": resume.phone,
        "email": resume.email,
        "objective": resume.objective,
        "qualification": resume.qualification,
        "board": resume.board,
        "year": resume.year,
        "percentage": resume.percentage,
        "skills": resume.skills,
        "experience": resume.experience,
        "gender": resume.gender,
        "father_name": resume.father_name,
        "dob": resume.dob,
        "language": resume.language,
        "nationality": resume.nationality,
        "marital_status": resume.marital_status,
        "place": resume.place,
    }

def create_resume_pdf(data, photo_path=""):
    html = render_template(
        "resume_template.html",
        data=data,
        photo_path=photo_path
    )

    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_file)

    if pisa_status.err:
        return None

    pdf_file.seek(0)
    response = make_response(pdf_file.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=resume.pdf"
    return response

@app.route("/resume/download/<int:id>")
def download_saved_resume(id):
    if not session.get("user_logged_in"):
        return redirect("/login")

    resume = Resume.query.get_or_404(id)

    if resume.user_id != session["user_id"]:
        return redirect("/resumes")

    response = create_resume_pdf(
        resume_to_form_data(resume),
        resume.photo_path or ""
    )

    if response is None:
        return "PDF generate nahi hua", 500

    return response

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    total_resumes = Resume.query.count()
    latest_resumes = Resume.query.order_by(Resume.id.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_resumes=total_resumes,
        latest_resumes=latest_resumes
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(username=username, password=password).first()

        if admin:
            session["admin_logged_in"] = True
            session["admin_id"] = admin.id
            return redirect("/admin")
        else:
            return render_template("admin/login.html", error="Invalid username or password")

    return render_template("admin/login.html")

@app.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        existing_admin = Admin.query.filter_by(username=username).first()

        if existing_admin:
            return render_template(
                "admin/signup.html",
                error="Ye admin username already exists hai"
            )

        if password != confirm_password:
            return render_template(
                "admin/signup.html",
                error="Password match nahi ho raha"
            )

        admin = Admin(username=username, password=password)
        db.session.add(admin)
        db.session.commit()

        return render_template(
            "admin/login.html",
            success="Admin account create ho gaya. Ab login karein."
        )

    return render_template("admin/signup.html")

@app.route("/admin/forgot-password", methods=["GET", "POST"])
def admin_forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        admin = Admin.query.filter_by(username=username).first()

        if not admin:
            return render_template(
                "admin/forgot_password.html",
                error="Admin username nahi mila"
            )

        if new_password != confirm_password:
            return render_template(
                "admin/forgot_password.html",
                error="Password match nahi ho raha"
            )

        admin.password = new_password
        db.session.commit()

        return render_template(
            "admin/login.html",
            success="Admin password reset ho gaya. Ab new password se login karein."
        )

    return render_template("admin/forgot_password.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")

@app.route("/admin/change-password", methods=["GET", "POST"])
def change_password():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    admin = Admin.query.get(session["admin_id"])

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if old_password != admin.password:
            return render_template("admin/change_password.html", error="Old password wrong")

        if new_password != confirm_password:
            return render_template("admin/change_password.html", error="Password not match")

        admin.password = new_password
        db.session.commit()

        return render_template("admin/change_password.html", success="Password changed successfully")

    return render_template("admin/change_password.html")


@app.route("/create-admin")
def create_admin():
    admin = Admin.query.filter_by(username="admin").first()

    if not admin:
        admin = Admin(username="admin", password="12345")
        db.session.add(admin)
        db.session.commit()

    return "Admin created"

@app.route("/resume/edit/<int:id>", methods=["GET", "POST"])
def user_edit_resume(id):
    if not session.get("user_logged_in"):
        return redirect("/login")

    resume = Resume.query.get_or_404(id)

    if resume.user_id != session["user_id"]:
        return redirect("/resumes")

    if request.method == "POST":
        resume.heading = request.form.get("heading")
        resume.name = request.form.get("name")
        resume.job_title = request.form.get("job_title")
        resume.house_no = request.form.get("house_no")
        resume.landmark = request.form.get("landmark")
        resume.area = request.form.get("area")
        resume.city = request.form.get("city")
        resume.pincode = request.form.get("pincode")
        resume.phone = request.form.get("phone")
        resume.email = request.form.get("email")
        resume.objective = request.form.get("objective")
        resume.qualification = request.form.get("qualification")
        resume.board = request.form.get("board")
        resume.year = request.form.get("year")
        resume.percentage = request.form.get("percentage")
        resume.skills = request.form.get("skills")
        resume.experience = request.form.get("experience")
        resume.gender = request.form.get("gender")
        resume.father_name = request.form.get("father_name")
        resume.dob = request.form.get("dob")
        resume.language = request.form.get("language")
        resume.nationality = request.form.get("nationality")
        resume.marital_status = request.form.get("marital_status")
        resume.place = request.form.get("place")

        photo = request.files.get("photo")

        if photo and photo.filename:
            photo_path = os.path.join("static/uploads", photo.filename)
            photo.save(photo_path)
            resume.photo_path = "/" + photo_path.replace("\\", "/")

        db.session.commit()
        return redirect("/resumes")

    return render_template("edit_resume.html", resume=resume)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100))
    photo = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))

def ensure_database_schema():
    with app.app_context():
        db.create_all()

        columns = [
            row[1]
            for row in db.session.execute(
                db.text("PRAGMA table_info(resume)")
            ).fetchall()
        ]

        if "user_id" not in columns:
            db.session.execute(db.text("ALTER TABLE resume ADD COLUMN user_id INTEGER"))
            db.session.commit()

ensure_database_schema()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template("signup.html", error="Email already registered")

        user = User(
            full_name=full_name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session["user_logged_in"] = True
            session["user_id"] = user.id
            session["user_name"] = user.full_name
            return redirect("/user-dashboard")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

    return render_template("login.html")

@app.route("/auth/google")
@app.route("/login/google")
def google_login():
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        return render_template(
            "login.html",
            error="Google login setup nahi hua. Render env vars add karein."
        )

    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/google/callback")
@app.route("/login/google/callback")
def google_callback():
    try:
        google.authorize_access_token()
        user_info = google.get("https://openidconnect.googleapis.com/v1/userinfo").json()
    except Exception:
        return render_template(
            "login.html",
            error="Google login fail ho gaya. Please dobara try karein."
        )

    email = user_info.get("email")

    if not email:
        return render_template(
            "login.html",
            error="Google account se email nahi mila"
        )

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            full_name=user_info.get("name") or email.split("@")[0],
            email=email,
            password="",
            photo=user_info.get("picture")
        )
        db.session.add(user)
    else:
        if not user.full_name:
            user.full_name = user_info.get("name")
        if not user.photo:
            user.photo = user_info.get("picture")

    db.session.commit()

    session["user_logged_in"] = True
    session["user_id"] = user.id
    session["user_name"] = user.full_name

    return redirect("/user-dashboard")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template(
                "forgot_password.html",
                error="Email registered nahi hai"
            )

        if new_password != confirm_password:
            return render_template(
                "forgot_password.html",
                error="Password match nahi ho raha"
            )

        user.password = new_password
        db.session.commit()

        return render_template(
            "login.html",
            success="Password reset ho gaya. Ab new password se login karein."
        )

    return render_template("forgot_password.html")

@app.route("/user-dashboard")
def user_dashboard():

    if not session.get("user_logged_in"):
        return redirect("/login")

    user = User.query.get(session["user_id"])

    return render_template(
        "user_dashboard.html",
        user=user
    )




@app.route("/user/logout")
def user_logout():
    session.pop("user_logged_in", None)
    session.pop("user_id", None)
    session.pop("user_name", None)

    return redirect("/login")



    return render_template("login.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if not session.get("user_logged_in"):
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        user.full_name = request.form.get("full_name")
        user.email = request.form.get("email")
        user.phone = request.form.get("phone")
        user.city = request.form.get("city")

        new_password = request.form.get("password")

        if new_password:
            user.password = new_password

        photo = request.files.get("photo")

        if photo and photo.filename:
            photo_path = os.path.join(
                "static/uploads",
                photo.filename
            )

            photo.save(photo_path)
            user.photo = "/" + photo_path

        db.session.commit()

        return redirect("/profile")

    return render_template(
        "profile.html",
        user=user
    )



@app.route("/download", methods=["POST"])
def download():
    data = request.form
    photo_path = request.form.get("photo_path", "")

    response = create_resume_pdf(data, photo_path)

    if response is None:
        return "PDF generate nahi hua", 500

    return response

@app.route("/save-resume", methods=["POST"])
def save_resume():
    if not session.get("user_logged_in"):
        return redirect("/login")

    data = request.form
    photo_path = request.form.get("photo_path", "")

    resume = Resume(
        user_id=session["user_id"],
        heading=data.get("heading"),
        name=data.get("name"),
        job_title=data.get("job_title"),
        house_no=data.get("house_no"),
        landmark=data.get("landmark"),
        area=data.get("area"),
        city=data.get("city"),
        pincode=data.get("pincode"),
        phone=data.get("phone"),
        email=data.get("email"),
        objective=data.get("objective"),
        qualification=data.get("qualification"),
        board=data.get("board"),
        year=data.get("year"),
        percentage=data.get("percentage"),
        skills=data.get("skills"),
        experience=data.get("experience"),
        gender=data.get("gender"),
        father_name=data.get("father_name"),
        dob=data.get("dob"),
        language=data.get("language"),
        nationality=data.get("nationality"),
        marital_status=data.get("marital_status"),
        place=data.get("place"),
        photo_path=photo_path
    )

    db.session.add(resume)
    db.session.commit()

    return redirect("/resumes")




if __name__ == "__main__":
    app.run(debug=True)
