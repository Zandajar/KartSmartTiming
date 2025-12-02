import requests
from bs4 import BeautifulSoup

VALID_TRACKS = {"narvskaya", "premium", "drive"}


def get_race_results(session_id: str, track: str = "narvskaya"):
    """
    Загружает HTML заезда и возвращает список строк таблицы:
    [
        ["Driver", "Имя1", "Имя2", ...],
        ["Kart", "12", "21", ...],
        ["1", "28.766 P3 +0.123", "28.543 P1", ...],
        ...
        ["Best", "27.901", "28.074", ...],
        ["Avg",  ...],
        ["Dev",  ...]
    ]
    """
    if track not in VALID_TRACKS:
        raise ValueError(
            f"Unknown track '{track}'. Must be one of: {', '.join(VALID_TRACKS)}"
        )

    url = f"https://timing.batyrshin.name/tracks/{track}/heats/{session_id}"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.select_one("table.heat-result")

    if table is None:
        print("Не найдена таблица .heat-result — возможно неверный session_id.")
        return []

    results = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        row_text = [" ".join(c.get_text(strip=True).split()) for c in cells]
        if any(row_text):
            results.append(row_text)

    return results


def find_subarray_index(data, word: str) -> int:
    for index, row in enumerate(data):
        if row and row[0].strip() == word:
            return index
    return -1


def get_driver_names(data):
    for row in data:
        if row and row[0].lower() == "driver":
            return row
    return []


def get_kart_numbers(data):
    for row in data:
        if row and row[0].lower() == "kart":
            return row
    return []


def get_time_list(data):
    driver_idx = None
    kart_idx = None

    for i, row in enumerate(data):
        if not row:
            continue
        first = row[0].lower()
        if first == "driver":
            driver_idx = i
        elif first == "kart":
            kart_idx = i

    if driver_idx is None or kart_idx is None:
        return []

    start_idx = kart_idx + 1
    best_idx = find_subarray_index(data, "Best")
    end_idx = best_idx if best_idx != -1 else len(data)

    lap_rows = [row for row in data[start_idx:end_idx] if row and row[0].isdigit()]

    if not lap_rows:
        return []

    drivers = data[driver_idx][1:]
    headers = ["Lap"] + drivers
    expected = len(headers)

    result = [headers]

    for row in lap_rows:
        if len(row) < expected:
            row = row + [""] * (expected - len(row))
        result.append(row[:expected])

    return result


def get_side_information(data):
    side = []
    for row in data:
        if not row:
            continue
        if row[0] in ("Best", "Avg", "Dev"):
            side.append(row)
    return side
