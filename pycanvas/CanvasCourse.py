class CanvasCourse(CanvasAuth):
    def __init__(self, course_id, auth=None):
        if auth is not None:
            super().__init__(auth)

        self.course_id = course_id

    def getAssignment(self, assignment_id):
        return self._spawn(CanvasAssignment(assignment_id, self))

    def getUsers(self):
        API_FMT = '/api/v1/courses/{course_id}/users'

        uri = API_FMT.format(course_id=self.course_id)
        print(uri)

        l = self.session.get_iter(uri)
        return l
