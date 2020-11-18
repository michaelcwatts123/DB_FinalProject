from flask import Blueprint, render_template, redirect, url_for, request

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/driver_lookup', methods=['POST'])
def driver_lookup():
    driver = request.form.get('driver_lookup')
    print(driver)
    return redirect(url_for('main.index'))


