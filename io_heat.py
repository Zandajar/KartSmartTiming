import os
from Data_Classes.heat import Heat


def import_heat_data(session_id: str):
    """Импортирует данные заезда и сохраняет их в файл"""
    try:
        os.makedirs("heats_data", exist_ok=True)
        filename = f"heats_data/heat_{session_id}.json"

        heat = Heat(session_id)
        heat.save(filename)

        return filename

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None
