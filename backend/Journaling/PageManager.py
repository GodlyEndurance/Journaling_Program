'''
PageManager.py

'''

import ItemActionHistory
import StorageManager
import StorageNode
import config
from Command import Command, AddItemCommand, EditItemCommand, DeleteItemCommand
from Item import Item

'''
Context:

"Item" refers to a bullet point within a page's (3) columns. 
'''

class PageManager():
    def __init__(self, history: ItemActionHistory, storage: StorageManager):
        self.history = history
        self.storage = storage
        
    def Undo(self):
        self.history.Undo()

    # Creates a File and puts it into the specified Folder
    # RQ: For Y/M/W/D entries within their respective folders
    def CreatePage(self, node: StorageNode.StorageNode, folder: StorageNode.Folder):
        if (config.TEST_MODE): print(f"\n====== PageManager.CreatePage ======")
        if (config.TEST_MODE): print(f"Creating page: {node} in folder: {folder}")

        if (node.getName() is None):
            if (config.TEST_MODE): print(f"Invalid page name for node: {node}")
            return
        if (folder == self.storage.subroot): # if folder is the protected Continuity folder
            if (config.TEST_MODE): print(f"Cannot create page: {node} directly in the Continuity folder."
                                        "Add the page inside one of its subfolders.")
            return
        
        for child in folder.children:
            if child.getName() == node.getName():
                if (config.TEST_MODE): print(f"Cannot create page: {node} in folder: {folder} as a page with the same name already exists")
                return
        
        self.storage.Add(node, folder)
        if (config.TEST_MODE): print(f"Page created: {node} in folder: {folder}")
        if (config.TEST_MODE): print(f"====== End PageManager.CreatePage ======\n")

    def AddItem(self, file: StorageNode.File, item: Item):
        if (config.TEST_MODE): print(f"\n====== PageManager.AddItem ======")
        if (config.TEST_MODE): print(f"Adding item: {item} to file: {file}")
        self.history.Execute(AddItemCommand(file, item))
        if (config.TEST_MODE): print(f"Item added: {item} to file: {file}")
        if (config.TEST_MODE): print(f"====== End PageManager.AddItem ======\n")

    def EditItem(self, file: StorageNode.File, item: Item, newText: str):
        if (config.TEST_MODE): print(f"\n====== PageManager.EditItem ======")
        if (config.TEST_MODE): print(f"Editing item: {item} in file: from '{item.get_content()}' to  '{newText}' from {file}")
        self.history.Execute(EditItemCommand(file, item, newText))
        if (config.TEST_MODE): print(f"Item edited: {item} in file: from '{item.get_content()}' to '{newText}' from {file}")
        if (config.TEST_MODE): print(f"====== End PageManager.EditItem ======\n")

    def DeleteItem(self, file: StorageNode.File, item: Item, position: int):
        if (config.TEST_MODE): print(f"\n====== PageManager.DeleteItem ======")
        if (config.TEST_MODE): print(f"Deleting item: {item} at position: {position} from file: {file}")

        if (len(file.ItemList) <= position or len(file.ItemList) == 0):
            if (config.TEST_MODE): print(f"Invalid position: {position} for file: {file}")
            if (config.TEST_MODE): print(f"====== End PageManager.DeleteItem ======\n")
            return

        self.history.Execute(DeleteItemCommand(file, item, position))
        if (config.TEST_MODE): print(f"Item deleted: {item} at position: {position} from file: {file}")
        if (config.TEST_MODE): print(f"====== End PageManager.DeleteItem ======\n")

