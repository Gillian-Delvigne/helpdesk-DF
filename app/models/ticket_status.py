import enum

class TicketStatusEnum(enum.Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

    @property
    def label_fr(self):
        return {
            TicketStatusEnum.NEW: "Nouveau",
            TicketStatusEnum.IN_PROGRESS: "En cours",
            TicketStatusEnum.BLOCKED: "Bloqué",
            TicketStatusEnum.RESOLVED: "Résolu",
            TicketStatusEnum.CLOSED: "Clos",
        }[self]
    
    @classmethod
    def values(cls):
        return [status.value for status in cls]