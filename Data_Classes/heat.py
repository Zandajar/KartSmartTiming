import os
import json

import pandas as pd
import matplotlib.pyplot as plt

from Parse_data import (
    get_race_results,
    get_driver_names,
    get_kart_numbers,
    get_time_list,
    get_side_information,
)
from .driver import Driver


class Heat:
    """Класс, описывающий один заезд (heat) на конкретном треке."""

    def __init__(
        self,
        session_id: str,
        track: str = "narvskaya",
        load_from_file: bool = False,
        **kwargs,
    ) -> None:
        """
        :param session_id: ID заезда на сайте timing.batyrshin.name
        :param track: 'narvskaya', 'premium', 'drive'
        :param load_from_file: если True — инициализация из JSON-данных
        """
        self.session_id = session_id
        self.track = track  # <-- новый атрибут трека
        self.side_info = []
        self.drivers = []
        self.df_laps = pd.DataFrame()

        if not load_from_file:
            # загружаем сырые данные с сайта для нужного трека
            raw_data = get_race_results(session_id, track=self.track)
            self._initialize_from_raw_data(raw_data)
        else:
            # восстановление из JSON
            self.track = kwargs.get("track", self.track)
            self.side_info = kwargs.get("side_info", [])
            drivers_data = kwargs.get("drivers", [])

            for d in drivers_data:
                driver = Driver(
                    place=d.get("place"),
                    name=d.get("name"),
                    kart_id=d.get("kart_id"),
                )
                for t in d.get("times", []):
                    driver.add_time(t)
                self.drivers.append(driver)

            self._reconstruct_df_laps()

    def _initialize_from_raw_data(self, raw_data) -> None:
        """Инициализирует объект Heat из сырых данных таблицы сайта."""
        if not raw_data:
            self.side_info = []
            self.drivers = []
            self.df_laps = pd.DataFrame()
            return

        driver_row = get_driver_names(raw_data)
        kart_row = get_kart_numbers(raw_data)
        time_data = get_time_list(raw_data)
        self.side_info = get_side_information(raw_data)

        # создаём пилотов
        self.drivers = []
        for place, (name, kart_id) in enumerate(
            zip(driver_row[1:], kart_row[1:]), start=1
        ):
            name = str(name).strip()
            kart = str(kart_id).strip()
            if kart.isdigit():
                kart_val = int(kart)
            else:
                kart_val = kart
            driver = Driver(place=place, name=name, kart_id=kart_val)
            self.drivers.append(driver)

        # создаём DataFrame с кругами и наполняем times у пилотов
        if time_data and len(time_data) > 1:
            headers = time_data[0]
            rows = time_data[1:]
            self.df_laps = pd.DataFrame(rows, columns=headers)

            # заполняем времена кругов у каждого пилота
            # предполагаем, что порядок колонок совпадает с порядком driver_row
            for idx, driver in enumerate(self.drivers):
                col_idx = idx + 1  # 0 - "Lap", дальше пилоты
                if col_idx < len(headers):
                    col_name = headers[col_idx]
                    if col_name in self.df_laps.columns:
                        for t in self.df_laps[col_name].tolist():
                            driver.add_time(t)
        else:
            self.df_laps = pd.DataFrame()

    def _reconstruct_df_laps(self) -> None:
        """Восстанавливает DataFrame df_laps из данных self.drivers (при загрузке из файла)."""
        if not self.drivers:
            self.df_laps = pd.DataFrame()
            return

        max_laps = max(len(driver.times) for driver in self.drivers)
        data_dict = {}

        # первая колонка — номер круга
        data_dict["Lap"] = [f"{i + 1}" for i in range(max_laps)]

        for driver in self.drivers:
            times = driver.times + [""] * (max_laps - len(driver.times))
            data_dict[driver.name] = times

        self.df_laps = pd.DataFrame(data_dict)

    def get_driver_names(self):
        """Возвращает строку вида: ['Driver', 'Имя1', 'Имя2', ...]."""
        return ["Driver"] + [d.get_name() for d in self.drivers]

    def get_kart_numbers(self):
        """Возвращает строку вида: ['Kart', 12, 21, ...]."""
        return ["Kart"] + [d.get_kart_id() for d in self.drivers]

    def get_time_list(self):
        """Возвращает полную таблицу кругов: заголовок + строки."""
        if self.df_laps.empty:
            return []
        header = self.df_laps.columns.tolist()
        rows = self.df_laps.values.tolist()
        return [header] + rows

    def save(self, filename: str) -> None:
        """Сохраняет заезд в файл JSON."""
        drivers_data = []
        for driver in self.drivers:
            drivers_data.append(
                {
                    "place": driver.place,
                    "name": driver.name,
                    "kart_id": driver.kart_id,
                    "times": driver.times,
                }
            )

        data = {
            "session_id": self.session_id,
            "track": self.track,
            "side_info": self.side_info,
            "drivers": drivers_data,
        }

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filename: str) -> "Heat":
        """Загружает заезд из файла JSON."""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл {filename} не найден")

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        session_id = data.get("session_id", "")
        track = data.get("track", "narvskaya")
        side_info = data.get("side_info", [])
        drivers = data.get("drivers", [])

        heat = cls(
            session_id=session_id,
            track=track,
            load_from_file=True,
            side_info=side_info,
            drivers=drivers,
        )
        return heat

    def print_results_table(self, data=None, header: bool = True) -> None:
        """Печатает красивую таблицу в консоль."""
        if data is None:
            data = self.get_time_list()

        if not data:
            print("Нет данных для отображения")
            return

        # вычисляем ширину колонок
        col_count = len(data[0])
        col_widths = [0] * col_count
        for row in data:
            for i, cell in enumerate(row):
                cell_str = "" if cell is None else str(cell)
                col_widths[i] = max(col_widths[i], len(cell_str))

        def format_row(row):
            return " | ".join(
                ("" if cell is None else str(cell)).ljust(col_widths[i])
                for i, cell in enumerate(row)
            )

        start_idx = 0
        if header:
            print(format_row(data[0]))
            print("-+-".join("-" * w for w in col_widths))
            start_idx = 1

        for row in data[start_idx:]:
            print(format_row(row))

    def print_full_results(self) -> None:
        """Печатает полную таблицу: Driver / Kart + круги."""
        if not self.drivers and self.df_laps.empty:
            print("Нет данных для отображения")
            return

        time_data = self.get_time_list()
        if not time_data:
            print("Нет данных кругов для отображения")
            return

        driver_row = self.get_driver_names()
        kart_row = self.get_kart_numbers()

        num_cols = len(time_data[0])

        def pad(row):
            return row + [""] * (num_cols - len(row))

        full_data = [
            pad(driver_row),
            pad(kart_row),
        ]
        full_data.extend(time_data)

        self.print_results_table(full_data, header=True)

    def generate_results_image(self, filename=None) -> str:
        """Генерирует PNG с таблицей результатов и возвращает путь к файлу."""
        time_data = self.get_time_list()
        if not time_data:
            raise ValueError("Нет данных кругов для генерации изображения")

        driver_row = self.get_driver_names()
        kart_row = self.get_kart_numbers()

        num_cols = len(time_data[0])

        def pad(row):
            return row + [""] * (num_cols - len(row))

        full_data = [
            pad(driver_row),
            pad(kart_row),
        ]
        full_data.extend(time_data)

        if filename is None:
            os.makedirs("heats_result", exist_ok=True)
            # можно включить трек в имя файла, чтобы не путались:
            filename = os.path.join(
                "heats_result", f"heat_{self.track}_{self.session_id}.png"
            )

        fig, ax = plt.subplots(figsize=(num_cols * 1.2, len(full_data) * 0.4))
        ax.axis("off")

        table = ax.table(
            cellText=full_data,
            loc="center",
            cellLoc="center",
        )

        # стилизация: первая строка — заголовки Driver, Kart,...
        for j in range(len(full_data[0])):
            cell = table[0, j]
            cell.set_facecolor("#f1f1f1")
            cell.set_text_props(weight="bold")

        # вторая строка — Kart
        for j in range(len(full_data[0])):
            cell = table[1, j]
            cell.set_facecolor("#f1f1f1")
            cell.set_text_props(color="black", weight="bold")

        # остальные строки
        for i in range(2, len(full_data)):
            for j in range(len(full_data[0])):
                cell = table[i, j]
                cell_text = "" if full_data[i][j] is None else str(full_data[i][j])
                if j == 0:
                    cell.set_facecolor("#e8e8e8")
                    cell.set_text_props(weight="bold")
                elif cell_text and " " in cell_text:
                    cell.set_facecolor("#333333")
                    cell.set_text_props(color="white")

        plt.savefig(filename, bbox_inches="tight", dpi=200)
        plt.close()

        return filename

    def __str__(self) -> str:
        return (
            f"Heat(session_id={self.session_id}, "
            f"track={self.track}, "
            f"drivers={len(self.drivers)}, "
            f"laps={len(self.df_laps)})"
        )
