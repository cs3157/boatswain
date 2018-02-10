
from CanvasAuth import CanvasAuth
from CanvasCourse import CanvasCourse
from CanvasUser import CanvasUser

class CanvasApi(CanvasAuth):

    def __init__(self, auth):
        super().__init__(auth)

    def getCourse(self, course_id):
        return self._spawn(CanvasCourse(course_id))

    def getUser(self, user_id):
        return self._spawn(CanvasUser(user_id))
