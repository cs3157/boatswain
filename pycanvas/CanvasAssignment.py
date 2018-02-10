class CanvasAssignment(CanvasAuth):
    def __init__(self, assignment_id, course, auth=None):
        if auth is not None:
            super().__init__(auth)

        self.assignment_id = assignment_id

        if not isinstance(course, CanvasCourse):
            course = self._spawn(CanvasCourse(course))
        self.course = course
        
    def getCourse(self):
        return self.course

    def getObj(self):
        API_FMT = '/api/v1/courses/{course_id}/assignments/{id}'

        uri = API_FMT.format(course_id=self.course.course_id,
                id=self.assignment_id)

        return self.session.get_obj(uri)
