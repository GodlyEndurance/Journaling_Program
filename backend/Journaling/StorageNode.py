''' 
StorageNode.py


'''
from __future__ import annotations  # for Folder instance within StorageNode
import config
from Item import Item
from enum import Enum


class EntryType(Enum):
    D = 1  # Page
    W = 2  # Chapter
    M = 3  # Volume
    Y = 4  # Series

class StorageNode:
    def __init__(self):
        self.name = ""
        self.parent: Folder = None
    
    def getName(self):
        if (config.TEST_MODE): print(f"\nGetting name: {self.name}")
        return self.name

    def setName(self, name):
        raise BaseException("setName method to be used within subclass")

    def move(self, destination: Folder):
        raise BaseException("move method to be used within subclass")
    
    def delete(self):
        raise BaseException("delete method to be used within subclass")

    def setParent(self, parent: Folder):
        if (config.TEST_MODE): print(f"\nSetting parent: {parent}")
        self.parent = parent
        if (config.TEST_MODE): print(f"Parent set to: {self.parent}")

    def getParent(self):
        if (config.TEST_MODE): print(f"\nGetting parent: {self.parent}")
        return self.parent


class File(StorageNode):
    def __init__(self):
        super().__init__()
        self.entryType: EntryType = None
        self.entryNum: int = 0
        self.data: str = ""
        self.isFavorite: bool = False
        self.ItemList: list[Item] = []
        self.date_modified: str = ""  # Added date_modified attribute for sorting by date modified

    def getEntryType(self)->EntryType: 
        if (config.TEST_MODE): print(f"\nGetting entry type: {self.entryType}")
        return self.entryType

    def getEntryNum(self)->int: 
        if (config.TEST_MODE): print(f"\nGetting entry num: {self.entryNum}")
        return self.entryNum

    def getData(self)->str: 
        if (config.TEST_MODE): print(f"\nGetting data: {self.data}")
        return self.data

    def getDateModified(self)->str:
        if (config.TEST_MODE): print(f"\nGetting date modified: {self.date_modified}")
        return self.date_modified

    def getFavorite(self)->bool: 
        if (config.TEST_MODE): print(f"\nGetting favorite status: {self.isFavorite}")
        return self.isFavorite

    def setName(self, fileName: str):  # str to be a date
        if (config.TEST_MODE): print(f"\nSetting file name: {fileName}")
        self.name = fileName
        if (config.TEST_MODE): print(f"File name set to: {self.name}")

    def setEntryType(self, entryType: EntryType): 
        if (config.TEST_MODE): print(f"\nSetting entry type: {entryType}")
        self.entryType = entryType
        if (config.TEST_MODE): print(f"Entry type set to: {self.entryType}")

    def setEntryNum(self, entryNum: int): 
        if (config.TEST_MODE): print(f"\nSetting entry num: {entryNum}")
        self.entryNum = entryNum
        if (config.TEST_MODE): print(f"Entry num set to: {self.entryNum}")

    def setData(self, data: str): 
        if (config.TEST_MODE): print(f"\nSetting data: {data}")
        self.data = data
        if (config.TEST_MODE): print(f"Data set to: {self.data}")

    def setFavorite(self, isFavorite: bool):
        if (config.TEST_MODE): print(f"\nSetting favorite status: {isFavorite}")
        self.isFavorite = isFavorite
        if (config.TEST_MODE): print(f"Favorite status set to: {self.isFavorite}")

    def setDateModified(self, date_modified: str):
        if (config.TEST_MODE): print(f"\nSetting date modified: {date_modified}")
        self.date_modified = date_modified
        if (config.TEST_MODE): print(f"Date modified set to: {self.date_modified}")

    def deepCopy(self) -> File:
        duplicate = File()
        duplicate.setName(self.getName())
        duplicate.setData(self.getData())
        duplicate.setEntryType(self.getEntryType())
        duplicate.setEntryNum(self.getEntryNum())
        duplicate.setFavorite(self.getFavorite())
        duplicate.setDateModified(self.getDateModified())
        return duplicate

    def displayContents(self):
        if (config.TEST_MODE): print(f"\nDisplaying contents of file: {self.getName()}")
        return self.entryType, self.entryNum, self.data, self.isFavorite, self.ItemList, self.date_modified

class Folder(StorageNode):
    def __init__(self, isLocked: bool = False):
        super().__init__()
        self.children: list[StorageNode] = []
        self.isLocked = isLocked
        
    def Add(self, node: StorageNode): 
        if (config.TEST_MODE): print(f"\nAdding node {node.getName()} to folder {self.name}")
        self.children.append(node)
        if isinstance(node, File):
            node.setParent(self)
        elif isinstance(node, Folder):
            node.setParent(self)
        if (config.TEST_MODE): print(f"Node {node.getName()} added to folder {self.name}")

    def Remove(self, node: StorageNode): 
        if (config.TEST_MODE): print(f"\nRemoving node {node.getName()} from folder {self.name}")
        self.children.remove(node)
        if (config.TEST_MODE): print(f"Node {node.getName()} removed from folder {self.name}")

    def setName(self, name):
        if (config.TEST_MODE): print(f"\nSetting folder name: {name}")
        self.name = name
        if (config.TEST_MODE): print(f"Folder name set to: {self.name}")

    def move(self, destination: Folder):
        if (config.TEST_MODE): print(f"\nMoving folder {self.name} to destination {destination.getName()}")
        destination.Add(self)
        if (config.TEST_MODE): print(f"Folder {self.name} moved to destination {destination.getName()}")

    def delete(self):
        if (config.TEST_MODE): print(f"\nDeleting folder {self.name}")
        self.children.clear()
        if (config.TEST_MODE): print(f"Folder {self.name} deleted")

    def getChildren(self):
        if (config.TEST_MODE): print(f"\nGetting children of folder {self.name}")
        return self.children
        


