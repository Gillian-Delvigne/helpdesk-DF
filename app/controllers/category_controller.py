from app.framework.decorators.auth_required import auth_required
from app.framework.decorators.inject import inject
from flask import render_template
from app import app
from app.forms.categories.category_form import CategoryForm
from app.services.category_service import CategoryService

@app.route("/categories/create", methods=["GET", "POST"])
@auth_required("ADMIN")
@inject
def create_category(
    category_service: CategoryService
):
    form = CategoryForm()
    if form.validate_on_submit():
        category_service.insert(form)
        return "SUCCESS", 201
    return render_template("categories/create.html", form=form)