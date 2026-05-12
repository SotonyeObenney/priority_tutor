from flask import render_template
from . import admin

@admin.route('/admin')
def index():
    return render_template('admin/index.html')