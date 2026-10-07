from app import db
from app.models.base_entity import BaseEntity


class Attachment(BaseEntity, db.Model):
    """Pièce jointe associée à un ticket."""

    __tablename__ = "attachments"

    attachment_id = db.Column(
        "attachmentid", db.Integer, primary_key=True, autoincrement=True
    )
    attachment_filename = db.Column(
        "attachmentfilename", db.String(255), nullable=False
    )
    attachment_path = db.Column("attachmentpath", db.String(500), nullable=False)
    attachment_size = db.Column("attachmentsize", db.Integer, nullable=False)
    ticket_id = db.Column(
        "ticketid", db.Integer, db.ForeignKey("tickets.ticketid"), nullable=False
    )
    author_id = db.Column(
        "authorid", db.Integer, db.ForeignKey("users.userid"), nullable=False
    )

    # Relations
    ticket = db.relationship("Ticket", back_populates="attachments")
    author = db.relationship("User", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment {self.attachment_id}: {self.attachment_filename}>"
