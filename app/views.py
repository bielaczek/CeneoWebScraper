from app import app
from flask import render_template

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/exctract')
def index():
    return render_template("extract.html")

@app.route('/products')
def index():
    return render_template("products.html")

@app.route('/author')
def index():
    return render_template("author.html")

@app.route('/product/<product_id>')
def index():
    return render_template("product.html")