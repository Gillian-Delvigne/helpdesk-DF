from app import db
from app.models.base_entity import BaseEntity
from app.models.ticket_status import TicketStatusEnum
from sqlalchemy import Enum


class TicketStatusHistory(BaseEntity, db.Model):
    """Historique d'un changement de statut d'un ticket."""

    __tablename__ = "ticketstatushistories"

    history_id = db.Column(
        "historyid", db.Integer, primary_key=True, autoincrement=True
    )
    ticket_id = db.Column(
        "ticketid", db.Integer, db.ForeignKey("tickets.ticketid"), nullable=False
    )
    user_id = db.Column(
        "userid", db.Integer, db.ForeignKey("users.userid"), nullable=False
    )
    old_status = db.Column("oldstatus", Enum(TicketStatusEnum), nullable=False)
    new_status = db.Column("newstatus", Enum(TicketStatusEnum), nullable=False)

    # Relations
    ticket = db.relationship("Ticket", back_populates="status_histories")
    user = db.relationship("User", back_populates="ticket_status_histories")

    def __repr__(self):
        return f"<TicketStatusHistory {self.history_id}: {self.old_status} -> {self.new_status}>"
