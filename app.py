from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")