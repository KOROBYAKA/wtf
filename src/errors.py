class ConfigError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class MissingFieldError(ConfigError):
    def __init__(self, section_name, field_name):
        self.msg = f"Missing required configuration field: the field {field_name} must be defined in {section_name}."
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"

class ConfigConflictError(ConfigError):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"

class InvalidFieldError(ConfigError):
    def __init__(self, field_name, value):
        self.msg = f"Invalid configuration field: {field_name} has invalid value {value}"
        super().__init__(self.msg)
    def __str__(self):
        return f"{self.msg}"

class MissingSectionError(ConfigError):
    def __init__(self, section):
        self.msg = f"Missing required configuration section: the section {section} must be defined in config"
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"

