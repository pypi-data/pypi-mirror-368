import sqlite3
import logging
import re

from .setup_db import create_db, get_db_path

class DB:
    def __init__(self)->None:
        create_db()

        self.conn = sqlite3.connect(get_db_path())
        self.cursor = self.conn.cursor()

    def get_location_from_plate_id(self, plate_id: str) -> int:
        self.cursor.execute("SELECT Location FROM Plates WHERE PlateId = ?", (plate_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_owner_from_plate_id(self, plate_id: str) -> str:
        self.cursor.execute("SELECT Owner FROM Plates WHERE PlateId = ?", (plate_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_plate_ids_from_owner(self, owner: str) -> list:
        self.cursor.execute("SELECT PlateId FROM Plates WHERE Owner = ?", (owner,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_plate_ids_from_location(self, location: int) -> list:
        self.cursor.execute("SELECT PlateId FROM Plates WHERE Location = ?", (location,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_role_from_plate_id(self, plate_id: str) -> int:
        self.cursor.execute(
            "SELECT Role FROM Slots WHERE CurrentPlateId = ? OR AssignedPlatePlateId = ?",
            (plate_id, plate_id)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_current_plate_id_from_slot_stacker(self, slot: int, stacker: int) -> str:
        self.cursor.execute(
            "SELECT CurrentPlateId FROM Slots WHERE SlotNumber = ? AND Stacker = ?",
            (slot, stacker)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_assigned_plate_id_from_slot_stacker(self, slot: int, stacker: int) -> str:
        self.cursor.execute(
            "SELECT AssignedPlatePlateId FROM Slots WHERE SlotNumber = ? AND Stacker = ?",
            (slot, stacker)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_slot_stacker_from_assigned_plate_id(self, plate_id: str) -> tuple:
        self.cursor.execute(
            "SELECT SlotNumber, Stacker FROM Slots WHERE AssignedPlatePlateId = ?",
            (plate_id,)
        )
        return self.cursor.fetchone()

    def get_slot_stacker_from_current_plate_id(self, plate_id: str) -> tuple:
        self.cursor.execute(
            "SELECT SlotNumber, Stacker FROM Slots WHERE CurrentPlateId = ?",
            (plate_id,)
        )
        return self.cursor.fetchone()

    def get_tables(self)->list:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def get_columns_from_table(self, table: str)->list:
        self.cursor.execute(f"PRAGMA table_info({table})")
        return [row[1] for row in self.cursor.fetchall()]

    def get_table_data(self, table)->list[tuple[any]]:
        self.cursor.execute(f"SELECT * FROM {table}")
        return self.cursor.fetchall()

    def get_all_slots_from_role_stacker(self, role: int, stacker: int) -> list:
        self.cursor.execute(
            "SELECT SlotNumber FROM Slots WHERE Role = ? AND Stacker = ?",
            (role, stacker)
        )
        return [row[0] for row in self.cursor.fetchall()]

    #Well methods
    def get_well_id_from_plate_id_location(self, plate_id: str, location: str) -> str:
        try:
            self.cursor.execute(
                "SELECT WellId FROM Wells WHERE plateID = ? AND location = ?",
                (plate_id, location)
            )
            row = self.cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting WellId for {location} on plate {plate_id}: {e}")
            return None

    def get_media_from_location_plate_id(self, plate_id: str, location: str) -> dict:
        try:
            self.cursor.execute(
                "SELECT isMedia, mediachange FROM Wells WHERE plateID = ? AND location = ?",
                (plate_id, location)
            )
            row = self.cursor.fetchone()
            if row:
                return {
                    "is_media": bool(row[0]),
                    "mediachange": bool(row[1])
                }
            return {}
        except sqlite3.Error as e:
            logging.error(f"Error fetching media info for {location} on plate {plate_id}: {e}")
            return {}

    def get_well_row(self, plate_id: str, location: str) -> dict:
        try:
            self.cursor.execute(
                "SELECT * FROM Wells WHERE plateID = ? AND location = ?",
                (plate_id, location)
            )
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return {}
        except sqlite3.Error as e:
            logging.error(f"Error fetching row for {location} on plate {plate_id}: {e}")
            return {}

    def get_plate_format_as_tuple(self, plate_id: str) -> tuple[int, int]:
        try:
            self.cursor.execute("SELECT Format FROM Plates WHERE PlateId = ?", (plate_id,))
            result = self.cursor.fetchone()

            if not result or not result[0]:
                raise ValueError(f"No format found for plate ID '{plate_id}'.")

            format_str = result[0]

            if not re.fullmatch(r"\d+x\d+", format_str):
                raise ValueError(f"Invalid format string '{format_str}' in database.")

            rows, cols = map(int, format_str.lower().split("x"))
            return rows, cols


        except Exception as e:
            logging.error(f"Error retrieving format for plate '{plate_id}': {e}")
            raise

    def set_role_from_plate_id(self, plate_id: str, role: int):
        try:
            self.cursor.execute(
                "UPDATE Slots SET Role = ? WHERE CurrentPlateId = ? OR AssignedPlatePlateId = ?",
                (role, plate_id, plate_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting role for plate {plate_id}: {e}")

    def set_role_from_slot_stacker(self, slot: int, stacker: int, role: int):
        try:
            self.cursor.execute(
                "UPDATE Slots SET Role = ? WHERE SlotNumber = ? AND Stacker = ?",
                (role, slot, stacker)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting role for slot {slot}, stacker {stacker}: {e}")

    def set_current_plate_id_from_slot_stacker(self, slot: int, stacker: int, plate_id: str):
        try:
            self.cursor.execute(
                "UPDATE Slots SET CurrentPlateId = ? WHERE SlotNumber = ? AND Stacker = ?",
                (plate_id, slot, stacker)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting current plate {plate_id} for slot {slot}, stacker {stacker}: {e}")

    def set_assigned_plate_id_from_slot_stacker(self, slot: int, stacker: int, plate_id: str):
        try:
            self.cursor.execute(
                "UPDATE Slots SET AssignedPlatePlateId = ? WHERE SlotNumber = ? AND Stacker = ?",
                (plate_id, slot, stacker)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error assigning plate {plate_id} to slot {slot}, stacker {stacker}: {e}")

    def set_owner_from_plate_id(self, plate_id: str, owner: str):
        try:
            self.cursor.execute(
                "UPDATE Plates SET Owner = ? WHERE PlateId = ?",
                (owner, plate_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting owner {owner} for plate {plate_id}: {e}")

    def set_location_from_plate_id(self, plate_id: str, location: int):
        try:
            self.cursor.execute(
                "UPDATE Plates SET Location = ? WHERE PlateId = ?",
                (location, plate_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting location {location} for plate {plate_id}: {e}")

    def register_slot(self, slot: int, stacker: int, role: int, occupied: int, assigned_id: str, current_id: str):
        try:
            self.cursor.execute(
                """ INSERT INTO Slots (Stacker, SlotNumber, Role, Occupied, AssignedPlatePlateId, CurrentPlateId)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                (stacker, slot, role, occupied, assigned_id, current_id)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Slot ({stacker}, {slot}) already exists – skipping insert.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting slot ({stacker}, {slot}): {e}")

    def register_plate(self, plate_id: str, owner: str, location: int, wells: int = 48, format: str = "6x8"):

        if not re.fullmatch(r"\d+x\d+", format):
            raise ValueError(f"Invalid format '{format}'. Expected format like '6x8'.")

        try:
            self.cursor.execute(
                "INSERT INTO Plates (PlateId, Owner, Location, Wells, Format) VALUES (?, ?, ?, ?, ?)",
                (plate_id, owner, location, wells, format)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Plate {plate_id} already exists – skipping insert.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting plate {plate_id}: {e}")

    def register_plate_with_wells(self, plate_id: str, owner: str, location: int, wells: int = 48, format: str = "6x8"):
        try:
            self.register_plate(plate_id = plate_id, owner = owner, location=location, wells = wells, format = format)

            format_rows, format_cols = map(int, format.lower().split("x"))

            for row in range(format_rows):
                row_letter = chr(ord('A') + row)  # A, B, C, ...
                for col in range(1, format_cols + 1):
                    location_label = f"{row_letter}{col}"  # z. B. A1, B3, F8
                    self.register_well(plate_id=plate_id, location=location_label)

            logging.info(f"Plate {plate_id} with wells created successfully.")

        except sqlite3.IntegrityError:
            logging.warning(f"Plate {plate_id} already exists – skipping insert.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting plate {plate_id}: {e}")
        except Exception as e:
            logging.error(f"Unexpected Error on {plate_id}: {e}")

    def update_well(self, plate_id: str, location: str, is_media: bool = False, mediachange: bool = False):
        try:
            self.cursor.execute(
                "UPDATE Wells SET isMedia = ?, mediachange = ? WHERE plateID = ? AND location = ?",
                (int(is_media), int(mediachange), plate_id, location)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error updating well at {location} on plate {plate_id}: {e}")

    def register_well(self, plate_id: str, location: str, mediachange: bool = False, is_media: bool = False):
        try:
            self.cursor.execute(
                "INSERT INTO Wells (plateID, location, mediachange, isMedia) VALUES (?, ?, ?, ?)",
                (plate_id, location, int(mediachange), int(is_media))
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Well {location} for plate {plate_id} already exists – skipping insert.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting well {location} for plate {plate_id}: {e}")


    def write_plate_action(self, time_stamp: str, plate_id: str, action: str):
        try:
            self.cursor.execute(
                "INSERT INTO PlateActions (Timestamp, PlateId, Action) VALUES (?, ?, ?)",
                (time_stamp, plate_id, action)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Action at {time_stamp} already exists – skipping.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting plate action at {time_stamp}: {e}")