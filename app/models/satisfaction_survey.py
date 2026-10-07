from app import db
from app.models.base_entity import BaseEntity


class SatisfactionSurvey(BaseEntity, db.Model):
    """Une enquête liée à un ticket"""

    __tablename__ = "satisfactionsurveys"

    survey_id = db.Column("surveyid", db.Integer, primary_key=True, autoincrement=True)
    rating = db.Column("surveyrating", db.Integer, nullable=False)
    comment = db.Column("surveycomment", db.Text, nullable=False)

    ticket_id = db.Column("ticketid", db.ForeignKey("tickets.ticketid"), unique=True)
    client_id = db.Column("clientid", db.ForeignKey("users.userid"))

    ticket = db.relationship("Ticket", back_populates="satisfaction_surveys")
    client = db.relationship("User", back_populates="satisfaction_surveys")
