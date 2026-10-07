from app import db
from app.models.base_entity import BaseEntity


class UserRole(BaseEntity, db.Model):
    """Table d'association User <-> Role (many-to-many)."""

    __tablename__ = "userroles"

    # --- Colonnes ------------------------------------------------------------

    role_id = db.Column("roleid", db.ForeignKey("roles.roleid"), primary_key=True)
    user_id = db.Column("userid", db.ForeignKey("users.userid"), primary_key=True)

    # --- Relations -----------------------------------------------------------

    rel_user = db.relationship("User", back_populates="roles")
    rel_role = db.relationship("Role", back_populates="users")

    # --- Utils ---------------------------------------------------------------

    def __repr__(self):
        return f"<UserRole user={self.user_id} role={self.role_id}>"
