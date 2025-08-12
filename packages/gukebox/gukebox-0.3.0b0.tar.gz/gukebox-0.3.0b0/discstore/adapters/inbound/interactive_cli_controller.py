import logging
from typing import Optional

from discstore.adapters.inbound.cli_display import display_library_line, display_library_table
from discstore.domain.entities.disc import Disc, DiscMetadata, DiscOption
from discstore.domain.use_cases.add_disc import AddDisc
from discstore.domain.use_cases.edit_disc import EditDisc
from discstore.domain.use_cases.list_discs import ListDiscs
from discstore.domain.use_cases.remove_disc import RemoveDisc

LOGGER = logging.getLogger("discstore")


class InteractiveCLIController:
    def __init__(self, add_disc: AddDisc, list_discs: ListDiscs, remove_disc: RemoveDisc, edit_disc: EditDisc):
        self.add_disc = add_disc
        self.list_discs = list_discs
        self.remove_disc = remove_disc
        self.edit_disc = edit_disc

    def run(self) -> None:
        while True:
            print("\n=== Discstore management ===")
            print("1. Add a CD")
            print("2. Remove a CD")
            print("3. List all CDs")
            print("4. Edit a CD")
            print("5. Exit")

            choix = input("Your choice: ")
            self.handle_command(choix)

    def handle_command(self, command: str, args: Optional[dict] = None) -> None:
        args = args or {}
        try:
            if command == "1":
                self.add_disc_flow()
            elif command == "2":
                self.remove_disc_flow()
            elif command == "3":
                self.list_discs_flow()
            elif command == "4":
                self.edit_disc_flow()
            elif command == "5":
                print("See you soon!")
                exit(0)
            else:
                print("Invalid choice")
        except Exception as err:
            print(f"Error: {err}")
            LOGGER.error("Error during handling command", err)

    def add_disc_flow(self) -> None:
        print("\n-- Add a CD --")
        tag = input("Tag: ").strip()
        uri = input("URI: ").strip()
        option = DiscOption()
        metadata = DiscMetadata()

        disc = Disc(uri=uri, metadata=metadata, option=option)
        self.add_disc.execute(tag, disc)
        print("✅ CD successfully added")

    def list_discs_flow(self) -> None:
        print("\n-- List all CDs --")
        mode = input("Mode (table/line): ").strip()

        discs = self.list_discs.execute()
        if mode == "table" or mode == "":
            display_library_table(discs)
            return
        if mode == "line":
            display_library_line(discs)
            return
        print(f"Displaying mode not implemented yet: {mode}")

    def remove_disc_flow(self) -> None:
        print("\n-- Remove a CD --")
        tag = input("Tag: ").strip()
        self.remove_disc.execute(tag)
        print("🗑️ CD successfully removed")

    def edit_disc_flow(self) -> None:
        print("\n-- Edit a CD --")
        tag = input("Tag: ").strip()
        uri = input("URI: ").strip()
        option = DiscOption()
        metadata = DiscMetadata()

        disc = Disc(uri=uri, metadata=metadata, option=option)
        self.edit_disc.execute(tag, disc)
        print("✅ CD successfully edited")
