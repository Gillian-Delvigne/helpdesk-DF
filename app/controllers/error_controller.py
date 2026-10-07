from app import app
from flask import render_template


@app.errorhandler(401)
def unauthorized(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500
