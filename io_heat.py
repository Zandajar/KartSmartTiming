import os
from Data_Classes.heat import Heat


def import_heat_data(session_id: str, track: str = "narvskaya"):
    os.makedirs("heats_data", exist_ok=True)
    filename = f"heats_data/heat_{track}_{session_id}.json"

    heat = Heat(session_id, track=track)
    heat.save(filename)

    return filename
