import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from Parse_data import *
from .driver import Driver


class Heat:
    def __init__(self, session_id: str, load_from_file=False, **kwargs):
        self.session_id = session_id

        if not load_from_file:
            self.raw_data = get_race_results(session_id)
            self._initialize_from_raw_data()
        else:
            self.side_info = kwargs.get('side_info', [])
            self.stint_info = kwargs.get('stint_info', [])
            self.drivers = [Driver.from_dict(d) for d in kwargs.get('drivers', [])]
            self.df_laps = pd.DataFrame(kwargs.get('laps_data', []))

    def _initialize_from_raw_data(self):
        driver_names = get_driver_names(self.raw_data)
        kart_numbers = get_kart_numbers(self.raw_data)
        time_data = get_time_list(self.raw_data)
        self.side_info = get_side_information(self.raw_data)
        self.stint_info = get_stint_info(self.raw_data)

        self.drivers = []
        for i, (name, kart_id) in enumerate(zip(driver_names[1:], kart_numbers[1:])):
            driver = Driver(place=i + 1, name=name, kart_id=kart_id)
            self.drivers.append(driver)

        if time_data:
            headers = time_data[0]
            rows = time_data[1:]
            self.df_laps = pd.DataFrame(rows, columns=headers)

            for i, driver in enumerate(self.drivers):
                col_name = headers[i + 1] if i + 1 < len(headers) else None
                if col_name:
                    times = self.df_laps[col_name].tolist()
                    for time in times:
                        driver.add_time(time)
        else:
            self.df_laps = pd.DataFrame()

    def get_driver_names(self) -> list:
        return ['Driver'] + [d.get_name() for d in self.drivers]

    def get_kart_numbers(self) -> list:
        return ['Kart'] + [d.get_kart_id() for d in self.drivers]

    def get_time_list(self) -> list:
        if self.df_laps.empty:
            return []
        return [self.df_laps.columns.tolist()] + self.df_laps.values.tolist()

    def save(self, filename):
        """Сохраняет заезд в файл JSON"""
        data = {
            'session_id': self.session_id,
            'side_info': self.side_info,
            'stint_info': self.stint_info,
            'drivers': [d.to_dict() for d in self.drivers],
            'laps_data': self.df_laps.to_dict(orient='list')
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filename):
        """Загружает заезд из файла JSON"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл {filename} не найден")

        with open(filename, 'r') as f:
            data = json.load(f)

        return cls(
            session_id=data['session_id'],
            load_from_file=True,
            side_info=data['side_info'],
            stint_info=data['stint_info'],
            drivers=data['drivers'],
            laps_data=data['laps_data']
        )

    def print_results_table(self, data: list = None, header: bool = True):
        if not data:
            print("Нет данных для отображения")
            return

        col_widths = [0] * len(data[0])
        for row in data:
            for i, cell in enumerate(row):
                if i < len(col_widths) and len(cell) > col_widths[i]:
                    col_widths[i] = len(cell)

        for row_idx, row in enumerate(data):
            formatted_row = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    formatted_row.append(cell.ljust(col_widths[i] + 2))

            if header and row_idx == 0:
                print("\033[1m" + "".join(formatted_row) + "\033[0m")
            else:
                print("".join(formatted_row))

    def print_full_results(self):
        driver_names = self.get_driver_names()
        kart_numbers = self.get_kart_numbers()
        time_list = self.get_time_list()

        full_data = [
            driver_names,
            kart_numbers
        ]

        if time_list:
            full_data.extend(time_list)

        print("\nПолные результаты заезда:")
        self.print_results_table(full_data, header=True)

    def generate_results_image(self, filename: str = None):
        if filename is None:
            filename = f"results_{self.session_id}.png"

        full_data = [
            ["Driver"] + self.df_drivers['Driver'].tolist(),
            ["Kart"] + self.df_drivers['Kart'].tolist()
        ]

        time_list = self.get_time_list()
        if time_list:
            full_data.extend(time_list)

        fig, ax = plt.subplots(figsize=(14, 10))
        ax.axis('off')
        ax.axis('tight')
        table = ax.table(
            cellText=full_data,
            loc='center',
            cellLoc='center',
            colLoc='center'
        )

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(3, 2)

        for i in range(len(full_data[0])):
            table[0, i].set_facecolor('#40466e')
            table[0, i].set_text_props(color='white', weight='bold')

            table[1, i].set_facecolor('#f1f1f1')
            table[1, i].set_text_props(color='black', weight='bold')

        for i in range(2, len(full_data)):
            for j in range(len(full_data[0])):
                cell = table[i, j]
                cell_text = full_data[i][j]

                if j == 0:
                    cell.set_facecolor('#e8e8e8')
                    cell.set_text_props(weight='bold')
                    continue

                if cell_text and ' ' in cell_text:
                    cell.set_facecolor('#333333')
                    cell.set_text_props(color='white')

        plt.savefig(filename, bbox_inches='tight', dpi=200)
        plt.close()

        print(f"Изображение результатов сохранено как: {filename}")

    def __str__(self) -> str:
        return f"Heat(session_id={self.session_id}, drivers={len(self.df_drivers)}, laps={len(self.df_laps)})"
