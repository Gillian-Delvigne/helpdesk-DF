from app import db
from app.models.base_entity import BaseEntity


class Role(BaseEntity, db.Model):
    """Un rôle applicatif ("CLIENT", "TECHNICIEN", "ADMIN")."""

    __tablename__ = "roles"

    # --- Colonnes ------------------------------------------------------------

    role_id = db.Column("roleid", db.Integer, primary_key=True)
    name = db.Column("rolename", db.String(50), unique=True, index=True)

    # --- Relations -----------------------------------------------------------

    users = db.relationship(
        "UserRole", back_populates="rel_role", cascade="all, delete-orphan"
    )

    # --- Utils ---------------------------------------------------------------

    def __repr__(self):
        return f"<Role {self.role_id} {self.name}>"
