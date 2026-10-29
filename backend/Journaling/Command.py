'''
Command.py

'''
# from abc import ABC, abstractmethod
import StorageNode
from Item import Item

class Command():
    def __init__(self, file: StorageNode.File, item: Item = None): 
        self.file = file
        self.item = item

    def Execute(self): pass

    def Undo(self): pass

class AddItemCommand(Command):
    def __init__(self, file: StorageNode.File, item: Item):
        super().__init__(file, item) 

    def Execute(self): 
        self.file.ItemList.append(self.item)

    def Undo(self): 
        if self.item in self.file.ItemList:
            self.file.ItemList.remove(self.item)

class EditItemCommand(Command):
    def __init__(self, file: StorageNode.File, item: Item, newText: str):
        super().__init__(file, item)
        self.oldText = item.get_content()
        self.newText = newText

    def Execute(self): 
        self.item.set_content(self.newText)

    def Undo(self): 
        self.item.set_content(self.oldText)

class DeleteItemCommand(Command):
    def __init__(self, file: StorageNode.File, item: Item, position):
        super().__init__(file, item)
        self.position: int = position

    def Execute(self): 
        if 0 <= self.position < len(self.file.ItemList):
            self.file.ItemList.pop(self.position)

    def Undo(self): 
        if 0 <= self.position <= len(self.file.ItemList):
            self.file.ItemList.insert(self.position, self.item)