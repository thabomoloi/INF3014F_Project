from flask import render_template, request, redirect, url_for

from .. import main


@main.route('/')
def home():
    return render_template('corepages/index.html')


@main.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        query = request.args.get('query')

        if query:
            return '<h1></h1>'

    return redirect(url_for('main.home'))
