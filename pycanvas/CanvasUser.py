from CanvasAuth import CanvasAuth

class CanvasUser(CanvasAuth):
    def __init__(self, user_id, auth=None):
        if auth is not None:
            super().__init__(auth)

        self.user_id = user_id
