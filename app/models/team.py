from app import db
from app.models.base_entity import BaseEntity


class Team(BaseEntity, db.Model):
    """Une équipe de support"""

    __tablename__ = "teams"

    # --- Colonnes ------------------------------------------------------------

    team_id = db.Column("teamid", db.Integer, primary_key=True)
    name = db.Column("teamname", db.String(50), unique=True, index=True)
    description = db.Column("teamdescription", db.Text, nullable=True)

    # --- Relations -----------------------------------------------------------

    members = db.relationship("User", back_populates="team")

    # --- Utils ---------------------------------------------------------------

    def __repr__(self):
        return f"<User {self.user_id} {self.name} {self.email}>"
