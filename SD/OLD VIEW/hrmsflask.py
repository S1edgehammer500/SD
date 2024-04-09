from flask import Flask, render_template, redirect, url_for, request #imports flask, RT allows you to render HTML files through flask (url_for is used for using pictures)
app = Flask(__name__) #CONTROL + C TO STOP

@app.route('/')
def index():
    return render_template('home.html')



@app.route("/home/")
def home():
    return render_template("home.html")


@app.route("/menu/")
def menu():
    return render_template("menu.html")

@app.route("/order/")
def order():
    return render_template("order.html")

@app.route("/reserve/")
def reserve():
    return render_template("reserve.html")

@app.route("/inventory/")
def inventory():
    return render_template("inventory.html")

@app.route("/account/")
def account():
    return render_template("account.html")

@app.route("/login/")
def login():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug = True)