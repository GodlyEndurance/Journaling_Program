'''
ItemActionHistory.py

'''

from Command import Command
import config
class ItemActionHistory():
    def __init__(self):
        self.actionStack: list[Command] = []

    # Records the execution of a command and adds it to the action stack.
    def Execute(self, command: Command): 
        if (config.TEST_MODE): print(f"\nExecuting command: {command}...")
        self.actionStack.append(command)
        if (config.TEST_MODE): print(f"Added command to action stack: {command}")

        if (config.TEST_MODE): print(f"Executing command: {command}...")
        command.Execute()
        if (config.TEST_MODE): print(f"Executed command: {command}")

    def Undo(self): 
        if self.actionStack:
            if (config.TEST_MODE): print(f"\nGetting command from action stack...")
            command = self.actionStack.pop()
            if (config.TEST_MODE): print(f"Undo executing for command: {command}...")
            command.Undo()
            if (config.TEST_MODE): print(f"Undo executed for command: {command}")
        else:
            if (config.TEST_MODE): print(f"\nNo command to undo.")