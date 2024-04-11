from flask import Flask, render_template, redirect, url_for, request #imports flask, RT allows you to render HTML files through flask (url_for is used for using pictures)
app = Flask(__name__) #CONTROL + C TO STOP

@app.route('/')
def index():
    return render_template('homepagev2.html')

if __name__ == '__main__':
    app.run(debug = True)

# return render_template('homepagev2.html')
# return render_template('base.html')


# Andre Barnett - 22025153