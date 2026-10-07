from app.framework.decorators.auth_required import auth_required
from app.framework.decorators.inject import inject
from flask import render_template
from app import app
from app.forms.priorities.priority_form import PriorityForm
from app.services.priority_service import PriorityService

@app.route("/priorities/create", methods=["GET", "POST"])
@auth_required("ADMIN")
@inject
def create_priority(
    priority_service: PriorityService
):
    form = PriorityForm()
    if form.validate_on_submit():
        priority_service.insert(form)
        return "SUCCESS", 201
    return render_template("priorities/create.html", form=form)