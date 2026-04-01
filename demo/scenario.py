from matplotlib.pylab import insert

from models.student import Student
from services.student_service import StudentService

def run_demo():
    service = StudentService()

    # 1. Insert
    # service.add(Student(10, "An", "Nam"))
    # service.add(Student(20, "Binh", "Nu"))
    # service.add(Student(5, "An", "Nam"))

    service.add(Student(10, "A", "Nam"))
    service.add(Student(20, "B", "Nu"))
    service.add(Student(5, "C", "Nam"))
    service.add(Student(6, "D", "Nu"))
    service.add(Student(12, "E", "Nam"))
    service.add(Student(30, "F", "Nu"))
    service.add(Student(7, "G", "Nam"))
    service.add(Student(17, "H", "Nu"))


    # 2. Delete
    service.delete(10)

    # 3. Search
    service.search_by_name("An")