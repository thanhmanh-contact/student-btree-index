class Student:
    def __init__(self, sid, name, gender):
        self.sid = sid
        self.name = name
        self.gender = gender

    def __str__(self):
        return f"{self.sid} | {self.name} | {self.gender}"