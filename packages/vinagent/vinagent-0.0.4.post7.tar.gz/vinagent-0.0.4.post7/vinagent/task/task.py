from vinagent.agent import Agent
class Task():
    def __init__(self, 
        task_name: str,
        description: str,
        expected_output: str,
        agent: Agent
    ):
        self.task_name = task_name
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
