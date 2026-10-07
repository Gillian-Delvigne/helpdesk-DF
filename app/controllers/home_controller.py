from flask import redirect, render_template

from app import app
from app.framework.decorators.inject import inject
from app.services.auth_service import AbstractAuthService


@app.get("/")
@inject
def index(auth_service: AbstractAuthService):
    if auth_service.is_authenticated():
        return redirect("/dashboard")
    return render_template("home/home.html")
