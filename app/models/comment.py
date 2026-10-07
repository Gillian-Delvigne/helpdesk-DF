from app import db
from app.models.base_entity import BaseEntity


class Comment(BaseEntity, db.Model):
    """Commentaire publié sur un ticket."""

    __tablename__ = "comments"

    comment_id = db.Column(
        "commentid", db.Integer, primary_key=True, autoincrement=True
    )
    comment_content = db.Column("commentcontent", db.Text, nullable=False)
    author_id = db.Column(
        "authorid", db.Integer, db.ForeignKey("users.userid"), nullable=False
    )
    ticket_id = db.Column(
        "ticketid", db.Integer, db.ForeignKey("tickets.ticketid"), nullable=False
    )

    # Relations

    author = db.relationship("User", back_populates="comments")
    ticket = db.relationship("Ticket", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.comment_id}: {self.comment_content}>"
