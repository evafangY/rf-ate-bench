class WorkflowState:
    def __init__(self):
        self.current = 0
        self.user_info = {}

    def next(self):
        self.current += 1

    def prev(self):
        if self.current > 0:
            self.current -= 1
