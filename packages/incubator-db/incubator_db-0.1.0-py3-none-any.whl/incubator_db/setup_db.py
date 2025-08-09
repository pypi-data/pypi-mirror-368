import sqlite3
import os
from pathlib import Path
import logging

def get_config_dir()->Path:
    return Path('C:/ProgramData/Incubator')

def get_db_path()->Path:
    return get_config_dir().joinpath("Incubator.db")

def create_db_dir():
    config_path = get_config_dir()
    try:
        if not config_path.exists():
            os.mkdir(config_path)
            logging.info(("Created Directory:", config_path))
    except Exception:
        logging.error((f"Could not create", config_path))


def create_db():
    config_path = get_config_dir()
    db_path = get_db_path()
    try:
        if not config_path.exists():
            create_db_dir()

        if db_path.exists():
            return

        #connetct to db/create empty db
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        #Create table PlateActions
        cursor.execute("""  CREATE TABLE "PlateActions" (
                            "Timestamp" TEXT NOT NULL CONSTRAINT "PK_PlateActions" PRIMARY KEY,
                            "PlateId" TEXT NULL,
                            "Action" TEXT NULL,
                            CONSTRAINT "FK_PlateActions_Plates_PlateId" FOREIGN KEY ("PlateId") REFERENCES "Plates" ("PlateId") ON DELETE RESTRICT)""")

        #create table Plates
        cursor.execute("""  CREATE TABLE "Plates" (
                            "PlateId" TEXT NOT NULL CONSTRAINT "PK_Plates" PRIMARY KEY,
                            "Owner" TEXT NULL,
                            "Location" INTEGER NOT NULL,
                            "Wells" INTEGER NOT NULL,
                            "Format" TEXT NOT NULL DEFAULT '6x8')""")

        try:
            cursor.execute("""  CREATE TABLE "Wells" (
                                "WellId" INTEGER PRIMARY KEY AUTOINCREMENT,
                                "PlateId" TEXT NOT NULL,
                                "location" TEXT NOT NULL,
                                "mediachange" BOOLEAN NOT NULL DEFAULT 0,
                                "isMedia" BOOLEAN NOT NULL DEFAULT 0,
                                FOREIGN KEY ("PlateId") REFERENCES Plates("PlateId") ON DELETE CASCADE,
                                UNIQUE ("plateID", "location"))""")
        except Exception as e:
            print("Wells error: ", e)

        #create table slots
        cursor.execute("""  CREATE TABLE "Slots" (
                            "SlotNumber" INTEGER NOT NULL,
                            "Stacker" INTEGER NOT NULL,
                            "Role" INTEGER NOT NULL,
                            "Occupied" INTEGER NOT NULL,
                            "AssignedPlatePlateId" TEXT NULL,
                            "CurrentPlateId" TEXT NULL,
                            CONSTRAINT "PK_Slots" PRIMARY KEY ("Stacker", "SlotNumber"),
                            CONSTRAINT "FK_Slots_Plates_AssignedPlatePlateId" FOREIGN KEY ("AssignedPlatePlateId") REFERENCES "Plates" ("PlateId") ON DELETE RESTRICT,
                            CONSTRAINT "FK_Slots_Plates_CurrentPlateId" FOREIGN KEY ("CurrentPlateId") REFERENCES "Plates" ("PlateId") ON DELETE RESTRICT) """)

        #create index IX_PlateActions_PlateId
        cursor.execute("""  CREATE INDEX "IX_PlateActions_PlateId" ON "PlateActions" ("PlateId")""")

        #create Index Slots_AssignedPlatePlateId
        cursor.execute("""  CREATE UNIQUE INDEX "IX_Slots_AssignedPlatePlateId" ON "Slots" ("AssignedPlatePlateId")""")

        #create Index Slots_CurrentPlateID
        cursor.execute("""  CREATE INDEX "IX_Slots_CurrentPlateId" ON "Slots" ("CurrentPlateId")""")

        conn.close()

    except sqlite3.Error as e:
        logging.error(msg =("Sqlite Error occurred", e))

create_db()