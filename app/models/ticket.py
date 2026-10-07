from app import db
from app.models.base_entity import BaseEntity
from app.models.ticket_status import TicketStatusEnum
from sqlalchemy import Enum


class Ticket(BaseEntity, db.Model):
    __tablename__ = "tickets"

    # Base Columns
    ticket_id = db.Column("ticketid", db.Integer, primary_key=True)
    title = db.Column("title", db.String(255), nullable=False)
    description = db.Column("description", db.Text, nullable=False)
    status = db.Column("status", Enum(TicketStatusEnum), nullable=False)
    due_date = db.Column(
        "duedate", db.Date, nullable=False
    )  # derived from priority.delay_hours (?)

    # Foreign Keys
    author_id = db.Column(
        "authorid", db.Integer, db.ForeignKey("users.userid"), nullable=False
    )
    technician_id = db.Column(
        "technicianid", db.Integer, db.ForeignKey("users.userid"), nullable=True
    )
    category_id = db.Column(
        "categoryid", db.Integer, db.ForeignKey("categories.categoryid"), nullable=False
    )
    priority_id = db.Column(
        "priorityid", db.Integer, db.ForeignKey("priorities.priorityid"), nullable=False
    )
    equipment_id = db.Column(
        "equipmentid",
        db.Integer,
        db.ForeignKey("equipments.equipmentid"),
        nullable=False,
    )

    # Relationships
    author = db.relationship(
        "User", foreign_keys=[author_id], back_populates="created_tickets"
    )
    technician = db.relationship(
        "User", foreign_keys=[technician_id], back_populates="assigned_tickets"
    )
    category = db.relationship("Category", back_populates="tickets")
    priority = db.relationship("Priority", back_populates="tickets")
    equipment = db.relationship("Equipment", back_populates="ticket")
    attachments = db.relationship("Attachment", back_populates="ticket")
    comments = db.relationship("Comment", back_populates="ticket")
    satisfaction_surveys = db.relationship(
        "SatisfactionSurvey", back_populates="ticket"
    )
    status_histories = db.relationship("TicketStatusHistory", back_populates="ticket")

    def __repr__(self):
        return f"<Ticket ['{self.title}' ID: {self.ticket_id}]>"
