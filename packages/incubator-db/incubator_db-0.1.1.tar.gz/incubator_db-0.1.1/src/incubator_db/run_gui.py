def run_gui():
    from .db_gui import GUI
    gui = GUI()
    root=gui.get_root()
    root.mainloop()

run_gui()