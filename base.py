from sqlalchemy import Column, Integer, String, BLOB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True)
    command_string = Column(String, nullable=False)
    length = Column(Integer, nullable=False)
    # store duration of command run time in seconds, rounded up to nearest second
    duration = Column(Integer, nullable=False, default=0)
    output = Column(BLOB)

    def __init__(self, command_string, length, duration, output):
        self.command_string = command_string
        self.length = length
        self.duration = duration
        self.output = output

    def __str__(self):
        """
        Overriding __str__ method for making Command object readable.
        """
        return "CMD: {0}, LENGTH: {1}, DURATION: {2}, OUTPUT: {3} ".format(self.command_string, self.length, self.duration, self.output)

    def to_json(self):
        """
        Serialize the Command object
        """
        return {"command_string": self.command_string, "length": self.length, "duration": self.duration, "output": self.output}
