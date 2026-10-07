from app import db
from app.models.base_entity import BaseEntity


class Category(BaseEntity, db.Model):
    __tablename__ = "categories"

    # Base Columns
    category_id = db.Column("categoryid", db.Integer, primary_key=True)
    name = db.Column("categoryname", db.Text, nullable=False, index=True, unique=True)
    description = db.Column("categorydescription", db.String(255), nullable=False)

    # Relationships
    tickets = db.relationship("Ticket", back_populates="category")
    knowledge_articles = db.relationship("KnowledgeArticle", back_populates="category")

    def __repr__(self):
        return f"<Category ['{self.name}' ID: {self.category_id}]>"
