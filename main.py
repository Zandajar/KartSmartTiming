import os

from io_heat import import_heat_data
from Data_Classes.heat import Heat


TRACKS = {
    "1": "narvskaya",
    "2": "premium",
    "3": "drive",
}


def choose_track() -> str:
    """Интерактивный выбор трека."""
    print("Выберите трек:")
    print("  1) narvskaya")
    print("  2) premium")
    print("  3) drive")

    while True:
        choice = input("Введите цифру (1–3) или имя трека: ").strip().lower()
        if choice in TRACKS:
            return TRACKS[choice]
        if choice in TRACKS.values():
            return choice
        print("Некорректный ввод. Попробуйте ещё раз.")


def input_session_id() -> str:
    """Запрос session_id у пользователя."""
    while True:
        session_id = input("Введите session_id заезда: ").strip()
        if session_id:
            return session_id
        print("session_id не может быть пустым.")


def analyze_heat(session_id: str, track: str) -> Heat:
    """Создаёт объект Heat, парсит сайт и возвращает его."""
    print(f"\nАнализ заезда:")
    print(f"  Трек: {track}")
    print(f"  session_id: {session_id}\n")

    heat = Heat(session_id=session_id, track=track)

    if not heat.drivers:
        print("Не удалось получить данные заезда. Проверьте session_id и трек.")
        return heat

    print(f"Успешно загружены данные заезда.")
    print(f"Пилотов: {len(heat.drivers)}, кругов: {len(heat.df_laps)}\n")

    return heat


def save_heat(heat: Heat) -> str:
    """Сохраняет Heat в JSON и возвращает путь к файлу."""
    os.makedirs("heats_data", exist_ok=True)
    filename = os.path.join("heats_data", f"heat_{heat.track}_{heat.session_id}.json")
    heat.save(filename)
    print(f"Данные заезда сохранены в файл: {filename}")
    return filename


def maybe_print_results(heat: Heat) -> None:
    """По запросу пользователя выводит полные результаты."""
    if not heat.drivers and heat.df_laps.empty:
        return

    answer = input("\nПоказать полные результаты в консоли? (y/n): ").strip().lower()
    if answer in ("y", "yes", "д", "да", ""):
        print("\nПолные результаты заезда:\n")
        heat.print_full_results()
        print()


def maybe_generate_image(heat: Heat) -> None:
    """По запросу пользователя генерирует PNG с таблицей результатов."""
    answer = (
        input("Сгенерировать изображение с таблицей результатов? (y/n): ")
        .strip()
        .lower()
    )
    if answer not in ("y", "yes", "д", "да"):
        return

    try:
        os.makedirs("heats_result", exist_ok=True)
        filename = os.path.join(
            "heats_result", f"heat_{heat.track}_{heat.session_id}.png"
        )
        path = heat.generate_results_image(filename=filename)
        print(f"Изображение сохранено в файл: {path}")
    except Exception as e:
        print(f"Не удалось сгенерировать изображение: {e}")


def interactive_session():
    """Основной цикл CLI."""
    while True:
        print("KartChrono — анализ заезда\n")

        track = choose_track()
        session_id = input_session_id()

        heat = analyze_heat(session_id, track)

        if heat.drivers:
            save_heat(heat)
            maybe_print_results(heat)
            maybe_generate_image(heat)

        print("\n---------------------------------------\n")
        again = input("Проанализировать ещё один заезд? (y/n): ").strip().lower()
        if again not in ("y", "yes", "д", "да"):
            print("\nЗавершение работы.")
            break


if __name__ == "__main__":
    interactive_session()
