'''
StorageManager.py

'''
import config
from StorageNode import StorageNode, File, Folder
from Sorter import Sorter, SortMetric

class StorageManager:
    def __init__(self): 
        self.root: Folder = Folder()    # The repository root directory itself (the entry point into the repository)
        self.subroot: Folder = Folder()
        self.subroot1: Folder = Folder()

        self.entryRootY: Folder = Folder()
        self.entryRootM: Folder = Folder()
        self.entryRootW: Folder = Folder()
        self.entryRootD: Folder = Folder()

        self.root.setName("Root")
        self.subroot.setName("Continuity") # No folders, except its subfolders, can be added here. No duplicate files allowed.
        self.subroot1.setName("Favorites") # No folders can be added in here. Duplicate files allowed.

        self.entryRootY.setName("Series")
        self.entryRootM.setName("Volumes")
        self.entryRootW.setName("Chapters")
        self.entryRootD.setName("Pages")

        self.Add(self.subroot, self.root)
        self.Add(self.subroot1, self.root)

        self.Add(self.entryRootY, self.subroot)
        self.Add(self.entryRootM, self.subroot)
        self.Add(self.entryRootW, self.subroot)
        self.Add(self.entryRootD, self.subroot)

        self.sorter = Sorter()
        
        
    def DisplayAll(self, metric: SortMetric): 
        if not isinstance(metric, SortMetric):
            raise TypeError(f"metric must be a SortMetric, got {type(metric).__name__}")

        if (config.TEST_MODE): print(f"\n====== StorageManager.DisplayAll ======")
        if (config.TEST_MODE): print(f"Displaying all contents of the root folder...")

        self.sorter.SortByMetric(self.root.children, metric)

        self.DisplayFolder(self.root, metric)
        if (config.TEST_MODE): print(f"====== End StorageManager.DisplayAll ======\n")

    # Recursive function to display all contents of a folder.
    def DisplayFolder(self, folder: Folder, metric: SortMetric):
        if not isinstance(metric, SortMetric):
            raise TypeError(f"metric must be a SortMetric, got {type(metric).__name__}")
            
        self.sorter.SortByMetric(folder.children, metric)

        if (config.TEST_MODE): print(f"\n====== StorageManager.DisplayFolder ======")
        if (config.TEST_MODE): print(f"Displaying folder: {folder}...")
        if (config.TEST_MODE): print(f"Folder: {folder}\n, name: {folder.getName()}\n, parent: {folder.getParent()}")

        for child in folder.children:
            if (isinstance(child, Folder)):
                self.DisplayFolder(child, metric)
            else:
                if (config.TEST_MODE): print(f"File: {child}\n, name: {child.getName()}\n, parent: {child.getParent()}")

        if (config.TEST_MODE): print(f"Displayed all contents of folder: {folder}")
        if (config.TEST_MODE): print(f"====== End StorageManager.DisplayFolder ======\n")

    def DisplayFile(self, file: File):
        if (config.TEST_MODE): print(f"\n====== StorageManager.DisplayFile ======")
        if (config.TEST_MODE): print(f"Displaying file: {file}...")
        if (config.TEST_MODE): print(f"File: {file}\n, name: {file.getName()}\n, parent: {file.getParent()}")
        
        if (config.TEST_MODE): print(f"Contents of file:")
        print(file.displayContents())
        if (config.TEST_MODE): print(f"Displayed contents of file: {file}")
        if (config.TEST_MODE): print(f"====== End StorageManager.DisplayFile ======\n")

    # Adds file or folder to a folder
    # RQ: For the Favorites folder and Entry folders, only files can be added inside.
    # RQ: For the Continuity folder, nothing can be added directly inside; nodes must be added inside its subfolders.
    def Add(self, node: StorageNode, folder: Folder): 
        if (config.TEST_MODE): print(f"\n====== StorageManager.Add ======")
        if (config.TEST_MODE): print(f"Adding node: {node} to folder: {folder}...")

        if folder == self.subroot:
            if (node == self.entryRootY or node == self.entryRootM or node == self.entryRootW or node == self.entryRootD):
                if (config.TEST_MODE): print(f"Adding node: {node} to Continuity folder.")
                folder.children.append(node)
                node.setParent(folder)
                if (config.TEST_MODE): print(f"====== End StorageManager.Add ======\n")
            else:
                if (config.TEST_MODE): print(f"Cannot add node: {node} to Continuity folder."
                                            "Add the nodes inside folders within the Continuity folder.")
                if (config.TEST_MODE): print(f"====== End StorageManager.Add ======\n")
            return
        if folder == self.subroot1 and not isinstance(node, File):
            if (config.TEST_MODE): print(f"Cannot add non-file node: {node} to Favorites folder")
            if (config.TEST_MODE): print(f"====== End StorageManager.Add ======\n")
            return
        
        if folder in [self.entryRootY, self.entryRootM, self.entryRootW, self.entryRootD] and not isinstance(node, File):
            if (config.TEST_MODE): print(f"Cannot add non-file node: {node} to entry folder: {folder}")
            if (config.TEST_MODE): print(f"====== End StorageManager.Add ======\n")
            return

        if (config.TEST_MODE): print(f"{node}: {node.getName()}\n, parent: {node.getParent()}")
        if (config.TEST_MODE): print(f"Folder: {folder}: {folder.getName()}\n, children: {folder.children}\n, parent: {folder.getParent()}")

        folder.children.append(node)
        node.setParent(folder)

        if (config.TEST_MODE): print(f"Node added: {node} to folder: {folder}")
        if (config.TEST_MODE): print(f"====== End StorageManager.Add ======\n")

    def Rename(self, node: StorageNode, new_name:str): 
        if (config.TEST_MODE): print(f"\n====== StorageManager.Rename ======")
        if (config.TEST_MODE): print(f"Renaming node: {node} to new name: {new_name}...")
        if (config.TEST_MODE): print(f"Current name of node: {node.getName()}\n, parent: {node.getParent()}")
        node.setName(new_name)
        if (config.TEST_MODE): print(f"Node renamed to: {node.getName()}")
        if (config.TEST_MODE): print(f"====== End StorageManager.Rename ======\n")

    # The position of the node is moved to the folder's children list.
    # RQ: Nothing can be moved from the Continuity and Favorites folder.
    def Move(self, node: StorageNode, folder: Folder): 
        if (config.TEST_MODE): print(f"\n====== StorageManager.Move ======")
        if (config.TEST_MODE): print(f"Moving node: {node} to folder: {folder}...")

        if node in self.subroot.children:
            if (config.TEST_MODE): print(f"Cannot move node: {node} from Continuity folder")
            if (config.TEST_MODE): print(f"====== End StorageManager.Move ======\n")
            return
        
        # implicitly, there are no folders inside the Favorites folder, only files are allowed.
        if node in self.subroot1.children:
            if (config.TEST_MODE): print(f"Cannot move node: {node} from Favorites folder")
            if (config.TEST_MODE): print(f"====== End StorageManager.Move ======\n")
            return
        
        # Implicitly, there are no folders inside the Y/M/W/D entry folders, only files are allowed.
        if (node in self.entryRootY.children or node in self.entryRootM.children or node in self.entryRootW.children or node in self.entryRootD.children):
            if (config.TEST_MODE): print(f"Cannot move node: {node} from Y/M/W/D entry folders")
            if (config.TEST_MODE): print(f"Duplicating node into some folder...")
            deepCopy = node.deepCopy()
            if (config.TEST_MODE): print(f"Deep copy created: {deepCopy}")

            if (config.TEST_MODE): print(f"Adding deep copy: {deepCopy} to folder: {folder}...")
            self.Add(deepCopy, folder)
            if (config.TEST_MODE): print(f"Deep copy added to folder: {folder}")
            if (config.TEST_MODE): print(f"====== End StorageManager.Move ======\n")
            return

        if (config.TEST_MODE): print(f"node: {node}\n, name: {node.getName()}\n, parent: {node.getParent()}")
        if (config.TEST_MODE): print(f"folder: {folder}\n, name: {folder.getName()}\n, children: {folder.children}\n, parent: {folder.getParent()}")

        if node.getParent():
            if (config.TEST_MODE): print(f"Removing node: {node} from its current parent: {node.getParent()}...")
            node.getParent().Remove(node)
        else:
            if (config.TEST_MODE): print(f"Node: {node} has no current parent")
        
        node.setParent(folder)
        folder.children.append(node)
        if (config.TEST_MODE): print(f"Node moved: {node} to folder: {folder}")
        if (config.TEST_MODE): print(f"====== End StorageManager.Move ======\n")

    # RQ: The root, Favorites, and Continuity folder cannot be deleted.
    def Delete(self, node: StorageNode): 
        if (config.TEST_MODE): print(f"\n====== StorageManager.Delete ======")
        if (config.TEST_MODE): print(f"Deleting node: {node}...")

        # UNIT TEST TODO
        match node:
            case self.subroot | self.subroot1 | self.root:
                if (config.TEST_MODE): print(f"Cannot delete node: {node}, as it is a protected folder")
                if (config.TEST_MODE): print(f"====== End StorageManager.Delete ======\n")
                return
            case self.entryRootY | self.entryRootM | self.entryRootW | self.entryRootD:
                if (config.TEST_MODE): print(f"Cannot delete node: {node}, as it is a protected entry folder inside the Continuity folder")
                if (config.TEST_MODE): print(f"====== End StorageManager.Delete ======\n")
                return
            case _:
                # Delete the node's dependencies
                if (config.TEST_MODE): print(f"Node: {node}\n, name: {node.getName()}\n, parent: {node.getParent()}")
                if node.getParent():
                    if (config.TEST_MODE): print(f"Removing node: {node} from its current parent: {node.getParent()}...")
                    node.getParent().Remove(node)
                    if (config.TEST_MODE): print(f"Node removed from its current parent: {node.getParent()}")
                node.setParent(None)

                if (isinstance(node, Folder)):
                    if (config.TEST_MODE): print(f"Deleting folder node's children...")
                    for child in node.children[:]:
                        self.Delete(child)
                    if (config.TEST_MODE): print(f"Deleted all of folder node's children")

                # Delete the node
                if (config.TEST_MODE): print(f"Deleting node: {node}...")
                node.delete() if hasattr(node, "delete") else None
                if (config.TEST_MODE): print(f"Deleted node: {node}")
                if (config.TEST_MODE): print(f"====== End StorageManager.Delete ======\n")

    def ToggleFavorite(self, file: File): 
        if (config.TEST_MODE): print(f"\n====== StorageManager.ToggleFavorite ======")
        if (config.TEST_MODE): print(f"Toggling favorite status for file: {file}")
        if not isinstance(file, File):
            if (config.TEST_MODE): print(f"Cannot toggle favorite for non-file node: {file}")
            if (config.TEST_MODE): print(f"====== End StorageManager.ToggleFavorite ======\n")
            return

        if file in self.subroot1.children and file.getFavorite():
            self.subroot1.children.remove(file)
            file.setFavorite(False)
            if (config.TEST_MODE): print(f"File: {file}\n, name: {file.getName()}\n, parent: {file.getParent()}")
            if (config.TEST_MODE): print(f"File removed from Favorites folder: {file}")
        else:
            self.subroot1.children.append(file)
            file.setFavorite(True)
            if (config.TEST_MODE): print(f"File: {file}\n, name: {file.getName()}\n, parent: {file.getParent()}")
            if (config.TEST_MODE): print(f"File added to Favorites folder: {file}")
        if (config.TEST_MODE): print(f"====== End StorageManager.ToggleFavorite ======\n")

    # RQ: Files cannot be duplicated to the Continuity folder.
    def DuplicateFile(self, file: File, folder: Folder): 
        if (config.TEST_MODE): print(f"\n====== StorageManager.DuplicateFile ======")
        if (config.TEST_MODE): print(f"Duplicating file: {file} to folder: {folder}")

        if (folder==self.subroot):
            if (config.TEST_MODE): print(f"Cannot duplicate file: {file} to protected folder: {folder}")
            if (config.TEST_MODE): print(f"====== End StorageManager.DuplicateFile ======\n")
            return

        duplicate = file.deepCopy()

        self.Add(duplicate, folder)
        if (config.TEST_MODE): print(f"File duplicated: {duplicate} to folder: {folder}")
        if (config.TEST_MODE): print(f"====== End StorageManager.DuplicateFile ======\n")
    
