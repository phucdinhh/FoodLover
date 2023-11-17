from flask import Flask, request, render_template, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        return render_template('index.html')
    else:
        query = request.form.get('food')
        return redirect(url_for('search', query=query))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "GET":
        query = request.args['query']

        # Setup spoonacular API
        api_get_products_url = 'https://api.spoonacular.com/recipes/complexSearch'
        api_key = os.getenv('SPOONACULAR_API_KEY')

        params = {'query': query, 'addProductInformation': True}

        try:
            headers = {'x-api-key': api_key}
            rq = requests.get(api_get_products_url,
                              params=params, headers=headers)

            if rq.status_code == 200:
                data = rq.json()
                print('rq', data)
                return render_template('search.html', data=data)

            else:
                return jsonify({'error': f'Failed to fetch data. Status code: {rq.status_code}'})
        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'})


@app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
def recipe(recipe_id):
    if request.method == 'GET':

        # Setup spoonacular API
        api_get_product_info_url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
        api_key = os.getenv('SPOONACULAR_API_KEY')

        try:
            headers = {'x-api-key': api_key}
            rq = requests.get(api_get_product_info_url, headers=headers)

            if rq.status_code == 200:
                data = rq.json()
                return render_template('recipe.html', data=data)
            else:
                return jsonify({'error': f'Failed to fetch data. Status code: {rq.status_code}'})

        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)

        redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        print(username, password, confirmation)

        redirect(url_for('login'))