from app import app
import os
import json
import requests
import pandas as pd
import glob
from bs4 import BeautifulSoup
from flask import render_template, request, redirect, url_for
from config import headers
from app import utils

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extract")
def display_form():
    return render_template("extract.html")

@app.route("/extract", methods=["POST"])
def extract():
    product_id = request.form.get('product_id')
    next_page = f"https://www.ceneo.pl/{product_id}#tab=reviews"
    response = requests.get(next_page, headers=headers)
    if response.status_code == 200:
        page_dom = BeautifulSoup(response.text, "html.parser")
        product_name = utils.extract_feature(page_dom, "h1")
        opinions_count = utils.extract_feature(page_dom, "a.product-review__link > span")
        if not opinions_count:
            error="Dla produktu o podanym id nie ma jeszcze żadnych opinii"
            return render_template("extract.html", error=error)
    else:
        error="Nie znaleziono produktu o podanym id"
        return render_template("extract.html", error=error)
    all_opinions = []
    while next_page:
        print(next_page)
        response = requests.get(next_page, headers=headers)
        if response.status_code == 200:
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions = page_dom.select("div.js_product-review:not(.user-post--highlight)")
            for opinion in opinions:
                single_opinion = {
                    key: utils.extract_feature(opinion, *value)
                    for key, value in utils.selectors.items()
                }
                all_opinions.append(single_opinion)
            try:
                next_page = "https://www.ceneo.pl"+utils.extract_feature(page_dom, "a.pagination__next", "href")
            except TypeError:
                next_page = None
        else: print(response.status_code)
    if not os.path.exists("./app/data"):
        os.mkdir("./app/data")
    if not os.path.exists("./app/data/opinions"):
        os.mkdir("./app/data/opinions")
    with open(f"./app/data/opinions/{product_id}.json", "w", encoding="UTF-8") as jf:
        json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
    return redirect(url_for('product', product_id=product_id, product_name=product_name))

# TO DO

@app.route("/products")
def products():

    all_products = []
    path = "/data/opinions"
    for filename in glob.glob(os.path.join(path, '*.json')): #only process .JSON files in folder.      
    with open(filename, encoding='utf-8', mode='r') as currentFile:

        average = 0
        pros_count = 0
        cons_count = 0

        rate_vaules = filename["stars"].split('/')[0]
        for value in rate_values:
            average += value
            if(filename['recommendation'] == 'Polecam'){
                pros_count += 1
            }
            if(filename['recommendation'] == 'Nie polecam'){
                cons_count += 1
            }
        average = average / len(rate_values)


        single_product = {
            "id": filename,
            "all_pros_count": pros_count
            "all_cons_count": cons_count
            "average_stars": average
        }
        all_products.append(single_product)

    with open(f"./app/data/sumarize.json", "w", encoding="UTF-8") as jf:
    json.dump(all_products, jf, indent=4, ensure_ascii=False)

    return render_template("products.html")

@app.route("/author")
def author():
    return render_template("author.html")

@app.route("/product/<product_id>")
def product(product_id):
    product_name=request.args.get('product_name')
    opinions = pd.read_json(f"./app/data/opinions/{product_id}.json")
    return render_template("product.html", product_id=product_id, product_name=product_name, opinions=opinions.to_html(table_id='opinions', classes=['display']))
