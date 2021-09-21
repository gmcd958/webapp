from flask import Blueprint, render_template

import library.utilities.utilities as utilities


home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():
    return render_template(
        'home/home.html',
        selected_articles=utilities.get_selected_books(),
        tag_urls=utilities.get_genres_and_urls()
    )
