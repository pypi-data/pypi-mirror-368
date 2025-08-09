import re

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .db import DB

class GUI:
    def __init__(self, master: str | None = None):
        """
        Parameters
        master : ttk.Window | None
            optional, depends on the use case of the GUI,
            can be integrated into another ttk.Window as a TopLevel or as a standalone GUI
        """
        self.root = ttk.Toplevel(master) if master else ttk.Window(title="Incubator Data Base", themename="vapor")
        self.root.geometry("1200x800")
        self.db = DB()
        self.tables = self.db.get_tables()
        print("Tabellen:", self.tables)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=12)

        style = ttk.Style()
        style.configure("Default.TButton")

        self.bool_slot = False
        self.bool_plate_actions = False
        self.bool_plates = False
        self.bool_wells = False

        self.button_slots = ttk.Button(text="Slots", command=self.callback_slots)
        self.button_plates = ttk.Button(text="Plates", command = self.callback_plates, bootstyle = "light")
        self.button_plate_actions = ttk.Button(text="PlateActions", command = self.callback_plate_actions)
        self.button_wells = ttk.Button(text = "Wells", command = self.callback_wells)

        self.button_slots.grid(column=0, row=0, sticky='nsew', ipady=12)
        self.button_plates.grid(column=1, row= 0, sticky='nsew', ipady=12)
        self.button_plate_actions.grid(column=2, row=0, sticky='nsew', ipady=12)
        self.button_wells.grid(column = 3, row = 0, sticky="nsew", ipady=12)

        self.tree_plates = ttk.Treeview(self.root)
        self.tree_plate_actions = ttk.Treeview(self.root)
        self.tree_slots = ttk.Treeview(self.root)
        self.tree_wells = ttk.Treeview(self.root)

        self.frame_entry = ttk.Frame(self.root)
        self.frame_entry.grid(row = 1, column=0, columnspan=4, sticky="nsew")
        self.entry_widgets = []#
        self.save_button = ttk.Button(self.root, text="Enter", command=self.save_entry, bootstyle = "success")
        self.save_button.grid(row=0, column=3, sticky="se", ipadx = 5, ipady = 5)
        self.update_entry_fields(self.db.get_columns_from_table("plates"))

        self.button_list = [self.button_wells, self.button_plates, self.button_plate_actions, self.button_slots]

        self.init_tree_plates()
        self.init_tree_plate_actions()
        self.init_tree_slots()
        self.init_tree_wells()
        self.insert_data()
        self.current_tree = self.tree_plates
        self.current_tree.grid()


    def get_root(self)->ttk.Window:
        return self.root

    def init_tree_plates(self):
        columns = self.db.get_columns_from_table(self.tables[1])
        self.tree_plates["columns"] = columns

        self.tree_plates.column("#0", width=0, stretch=False)
        self.tree_plates.heading("#0", text="")

        for i in columns:
            self.tree_plates.column(i, anchor=CENTER)
            self.tree_plates.heading(i, text=i, anchor=CENTER)

        self.tree_plates.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=5)
        self.tree_plates.grid_remove()

    def init_tree_slots(self):
        columns = self.db.get_columns_from_table(self.tables[4])
        self.tree_slots["columns"] = columns

        self.tree_slots.column("#0", width=0, stretch=False)
        self.tree_slots.heading("#0", text="")

        for i in columns:
            self.tree_slots.column(i, anchor=CENTER)
            self.tree_slots.heading(i, text = i, anchor=CENTER)

        self.tree_slots.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=5)
        self.tree_slots.grid_remove()

    def init_tree_plate_actions(self):
        columns = self.db.get_columns_from_table(self.tables[0])
        self.tree_plate_actions["columns"] = columns

        self.tree_plate_actions.column("#0", width=0, stretch=False)
        self.tree_plate_actions.heading("#0", text="")

        for i in columns:
            self.tree_plate_actions.column(i, anchor=CENTER)
            self.tree_plate_actions.heading(i, text=i, anchor=CENTER)

        self.tree_plate_actions.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=5)
        self.tree_plate_actions.grid_remove()

    def init_tree_wells(self):
        columns = self.db.get_columns_from_table(self.tables[2])

        self.tree_wells["columns"] = columns
        self.tree_wells.column("#0", width=0, stretch=False)
        self.tree_wells.heading("#0", text="")

        for i in columns:
            self.tree_wells.column(i, anchor=CENTER)
            self.tree_wells.heading(i, text=i, anchor=CENTER)

        self.tree_wells.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=5)
        self.tree_wells.grid_remove()

    def insert_data(self):
        table_data_plate_action: list[tuple] = self.db.get_table_data(self.tables[0])
        table_data_plates: list[tuple] = self.db.get_table_data(self.tables[1])
        table_data_slots: list[tuple] = self.db.get_table_data(self.tables[4])
        table_data_wells: list[tuple] = self.db.get_table_data(self.tables[2])

        for i in range(len(table_data_plate_action)):
            self.tree_plate_actions.insert(parent="", index = 'end', iid=i, text="Parent", values=table_data_plate_action[i])

        for i in range(len(table_data_plates)):
            self.tree_plates.insert(parent="", index = 'end', iid=i, text="Parent", values=table_data_plates[i])

        for i in range(len(table_data_slots)):
            self.tree_slots.insert(parent="", index = 'end', iid=i, text="Parent", values=table_data_slots[i])

        for i in range(len(table_data_wells)):
            self.tree_wells.insert(parent="", index = 'end', iid=i, text="Parent", values=table_data_wells[i])


    def callback_slots(self):
        if self.bool_slot:
            return

        self.bool_plates = False
        self.bool_plate_actions = False
        self.bool_slot = True
        self.current_tree.grid_remove()
        self.current_tree = self.tree_slots
        self.current_tree.grid()
        for i in range(4):
            self.reset_button_state(self.button_list[i])
        self.button_slots.configure(bootstyle="light")

        self.update_entry_fields(self.db.get_columns_from_table(self.tables[4]))

        #update data
        self.tree_slots.delete(*self.tree_slots.get_children())
        table_data = self.db.get_table_data("Slots")
        for row in table_data:
            self.tree_slots.insert("", "end", values=row)

    def callback_plates(self):
        if self.bool_plates:
            return

        self.bool_slot = False
        self.bool_plate_actions = False
        self.bool_plates = True
        self.current_tree.grid_remove()
        self.current_tree = self.tree_plates
        self.current_tree.grid()
        for i in range(4):
            self.reset_button_state(self.button_list[i])
        self.button_plates.configure(bootstyle="light")

        self.update_entry_fields(self.db.get_columns_from_table(self.tables[1]))

        self.tree_plates.delete(*self.tree_plates.get_children())
        table_data = self.db.get_table_data("Plates")
        for row in table_data:
            self.tree_plates.insert("", "end", values=row)

    def callback_plate_actions(self):
        if self.bool_plate_actions:
            return

        self.bool_plates = False
        self.bool_slot = False
        self.bool_plate_actions = True
        self.bool_wells = False
        self.current_tree.grid_remove()
        self.current_tree = self.tree_plate_actions
        self.current_tree.grid()
        for i in range(4):
            self.reset_button_state(self.button_list[i])
        self.button_plate_actions.configure(bootstyle="light")

        self.update_entry_fields(self.db.get_columns_from_table(self.tables[0]))

        self.tree_plate_actions.delete(*self.tree_plate_actions.get_children())
        table_data = self.db.get_table_data("PlateActions")
        for row in table_data:
            self.tree_plate_actions.insert("", "end", values=row)

    def callback_wells(self):
        if self.bool_wells:
            return

        self.bool_wells = True
        self.bool_plates = False
        self.bool_slot = False
        self.bool_plate_actions = False
        self.current_tree.grid_remove()
        self.current_tree = self.tree_wells
        self.current_tree.grid()
        for i in range(4):
            self.reset_button_state(self.button_list[i])
        self.button_wells.configure(bootstyle="light")

        self.update_entry_fields(self.db.get_columns_from_table(self.tables[2]))

        self.tree_wells.delete(*self.tree_wells.get_children())
        table_data = self.db.get_table_data("Wells")
        for row in table_data:
            self.tree_wells.insert("", "end", values=row)

    def reset_button_state(self, button: ttk.Button):
        button.configure(bootstyle = "Neutral Button")

    def update_entry_fields(self, columns: list[str]):

        for widget in self.entry_widgets:
            widget.destroy()

        self.entry_widgets.clear()

        for i in range(10):
            self.frame_entry.columnconfigure(i, weight=0)

        for index, col in enumerate(columns):
            self.frame_entry.columnconfigure(index, weight = 1)
            entry = ttk.Entry(self.frame_entry, width=15)
            entry.grid(row = 0, column=index, sticky="nsew", ipady = 8)
            self.entry_widgets.append(entry)

    def save_entry(self):
        if not self.current_tree:
            return

        # Zuordnung: TreeView → Tabellenname
        tree_to_table = {
            self.tree_plate_actions: self.tables[0],
            self.tree_plates: self.tables[1],
            self.tree_wells: self.tables[2],
            self.tree_slots: self.tables[4],
        }

        table_name = tree_to_table.get(self.current_tree)
        if not table_name:
            return

        # Spaltennamen holen & Eingabewerte erfassen
        columns = self.db.get_columns_from_table(table_name)
        values = [entry.get() for entry in self.entry_widgets]
        data = dict(zip(columns, values))

        try:
            if table_name == "Plates":

                format = data.get("Format", "6x8")
                if not re.fullmatch(r"\d+x\d+", format):
                    raise ValueError(f"Invaild format: '{format}' (expected example '6x8')")

                wells = int(data.get("Wells", 0))
                rows, cols = map(int, format.lower().split("x"))
                expected_wells = rows * cols
                if wells != expected_wells:
                    wells = expected_wells


                self.db.register_plate_with_wells(
                    plate_id=data["PlateId"],
                    owner=data.get("Owner", ""),
                    location=int(data["Location"]),
                    wells=wells,
                    format=format
                )

            elif table_name == "Slots":
                self.db.register_slot(
                    slot=int(data["SlotNumber"]),
                    stacker=int(data["Stacker"]),
                    role=int(data["Role"]),
                    occupied=int(data["Occupied"]),
                    assigned_id=data["AssignedPlatePlateId"],
                    current_id=data["CurrentPlateId"]
                )

            elif table_name == "Wells":
                self.db.register_well(
                    plate_id=data["plateID"],
                    location=data["location"],
                    mediachange=bool(int(data.get("mediachange", 0))),
                    is_media=bool(int(data.get("is_media", 0)))
                )

            elif table_name == "PlateActions":
                self.db.write_plate_action(
                    time_stamp=data["Timestamp"],
                    plate_id=data["PlateId"],
                    action=data["Action"]
                )

            # Erfolg: Zeile in TreeView einfügen
            self.current_tree.insert("", "end", values=values)

        except Exception as e:
            print(f"Fehler beim Speichern in '{table_name}': {e}")

