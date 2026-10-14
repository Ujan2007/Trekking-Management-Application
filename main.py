from flask import Flask, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

import sqlite3

app = Flask(__name__)
app.secret_key = "very_secret"

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "GET":

        return render_template('login.html')
    else:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        email = request.form.get("email")
        password = request.form.get("password")

        cursor.execute("SELECT * FROM admin WHERE email = ?", (email,))
        admin = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        users = cursor.fetchone()

        cursor.execute("SELECT * FROM staff WHERE email=?", (email,))
        staff = cursor.fetchone()

        if admin:
            if check_password_hash(admin[2], password):
                conn.close()
                session["email"] = admin[1]
                session["role"]="admin"
                return redirect("/admin")
            else:
                conn.close()
                return "Wrong Password"
        elif users:
            if check_password_hash(users[3], password):
                if users[4] == "blacklisted":
                    conn.close()
                    return "Your account has been blacklisted"
                conn.close()
                session["username"] = users[1]
                session["user_id"] = users[0]
                session["role"]="user"
                return redirect("/user")
            else:
                conn.close()
                return "Wrong Password"
        elif staff:
            if check_password_hash(staff[3], password):
                if staff[5] == "blacklisted":
                    conn.close()
                    return "Your account has been blacklisted"
                elif staff[5] == "inactive":
                    conn.close()
                    return "Your account has been flagged inactive, contact admin!"
                else:
                    conn.close()
                    session["staffname"] = staff[1]
                    session["staff_id"] = staff[0]
                    session["role"]="staff"
                    return redirect("/staff")
            else:
                conn.close()
                return "Invalid Password"
        else:
            conn.close()
            return "No account found"

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        name = request.form.get("name")
        email = request.form.get("email")

        print(name)
        print(email)
        print(request.form.get("password"))
        hashed_pass = generate_password_hash(request.form.get("password"))

        cursor.execute(""" INSERT INTO users(name,email,password_hash)
                           values(?,?,?)""",(name,email,hashed_pass))

        conn.commit()
        conn.close()

        return redirect('/login')

@app.route('/user', methods=['GET','POST'])
def userdashboard():
    if "role" not in session or session["role"]!="user":
        return "Access Denied",403
    if request.method == "GET" and "username" in session:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        id = session["user_id"]
        username = session["username"]

        return f"Welcome {username}"

@app.route('/admin', methods=['GET','POST'])
def admindashboard():
    if "role" not in session or session["role"]!="admin":
        return "Access Denied",403
    
    if request.method == "GET" and "email" in session:
        return "Admin back in the house!"

@app.route('/staff',methods=['GET','POST'])
def staffdashboard():
    if "role" not in session or session["role"]!="staff":
        return "Access Denied",403
    if request.method == "GET" and "staffname" in session:
        staffname = session["staffname"]

        return f"Welcome {staffname}"

if __name__ == '__main__':
    app.run(debug=True)