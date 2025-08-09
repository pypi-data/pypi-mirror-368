class WallboxError(Exception):

    def __init__(self, message=None, kind=None, field=None, key=None):
        self.kind = kind
        self.field = field
        self.message = message or "An error occurred"
        self.key = key
        super().__init__(self.__str__())

    def __str__(self):
        details = []
        if self.kind:
            details.append(f"Kind: {self.kind}")
        if self.field:
            details.append(f"Field: {self.field}")
        if self.key:
            details.append(f"URI: {self.key}")
        details.append(f"Message: {self.message}")
        return " | ".join(details)
