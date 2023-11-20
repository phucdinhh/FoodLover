from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import db
from .models.user import User
from .models.favorite import Favorite
import os
import requests

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        username = None
        if current_user.is_authenticated:
            username = current_user.username
        return render_template('index.html', username=username)
    else:
        query = request.form.get('food')
        return redirect(url_for('main.search', query=query))


@main.route('/search', methods=['GET', 'POST'])
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


@main.route('/recipe/<int:recipe_id>', methods=['GET', 'PUT'])
def recipe(recipe_id):
    if request.method == 'GET':

        # Setup spoonacular API
        api_get_product_info_url = f'https://api.spoonacular.com/recipes/{
            recipe_id}/information'
        api_key = os.getenv('SPOONACULAR_API_KEY')

        try:
            headers = {'x-api-key': api_key}
            rq = requests.get(api_get_product_info_url, headers=headers)

            if rq.status_code == 200:
                data = rq.json()

                isFavorite = None

                if current_user.is_authenticated:
                    user_id = current_user.id
                    isFavorite = db.session.execute(db.select(Favorite).filter_by(
                        user_id=user_id, recipe_id=recipe_id)).first()

                return render_template('recipe.html', data=data, isFavorite=isFavorite)
            else:
                return jsonify({'error': f'Failed to fetch data. Status code: {rq.status_code}'})

        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'})
    else:
        user_id = current_user.id

        isFavorite = Favorite.query.filter_by(
            user_id=user_id, recipe_id=recipe_id).first()

        if not isFavorite:
            newFavorite = Favorite(user_id=user_id, recipe_id=recipe_id)
            db.session.add(newFavorite)
            db.session.commit()
        else:
            db.session.delete(isFavorite)
            db.session.commit()

        return jsonify({'message': 'success'})


@main.route('/favorites', methods=['GET', 'DELETE'])
@login_required
def favorites():
    if request.method == 'GET':
        user_id = current_user.id

        listFavorite = Favorite.query.filter_by(user_id=user_id).all()

        recipeIds = []

        for favorite in listFavorite:
            recipeIds.append(favorite.recipe_id)

        api_get_product_info_url = f'https://api.spoonacular.com/recipes/informationBulk'
        api_key = os.getenv('SPOONACULAR_API_KEY')

        strRecipeIds = [str(id) for id in recipeIds]

        payload = {'ids': ','.join(strRecipeIds)}

        try:
            headers = {'x-api-key': api_key}
            rq = requests.get(api_get_product_info_url,
                              headers=headers, params=payload)

            if rq.status_code == 200:
                data = rq.json()
                return render_template('favorites.html', data=data)
            else:
                return jsonify({'error': f'Failed to fetch data. Status code: {rq.status_code}'})

        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'})

    else:
        data = request.get_json()
        print("req data", data)

        deletedFavorite = Favorite.query.filter_by(
            user_id=current_user.id, recipe_id=data['recipe_id']).first()

        db.session.delete(deletedFavorite)
        db.session.commit()

        return 'deleted'
