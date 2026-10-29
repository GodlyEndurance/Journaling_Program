'''
main.py

'''
import PageManager
import ItemActionHistory
import StorageManager
import StorageNode

import argparse
import config


def main():
    parser = argparse.ArgumentParser(description="Journaling Program")

    args = parser.parse_args()

    # Initialization of PageManager, ItemActionHistory, and StorageManager
    if config.TEST_MODE: print("Initializing Program...")
    aH = ItemActionHistory.ItemActionHistory()

    sM = StorageManager.StorageManager()
    pM = PageManager.PageManager(aH, sM)

    if config.TEST_MODE: print("Program Initialized.")


if __name__ == "__main__":
    main()