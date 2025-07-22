import pandas as pd
import matplotlib.pyplot as plt
from Parse_data import *


class Heat:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.raw_data = get_race_results()

        driver_data = get_driver_names(self.raw_data)
        kart_data = get_kart_numbers(self.raw_data)
        time_data = get_time_list(self.raw_data)
        self.side_info = get_side_information(self.raw_data)
        self.stint_info = get_stint_info(self.raw_data)

        if time_data:
            headers = time_data[0]
            self.df_laps = pd.DataFrame(time_data[1:], columns=headers)
        else:
            self.df_laps = pd.DataFrame()

        self.df_drivers = pd.DataFrame({
            'Driver': driver_data[1:],
            'Kart': kart_data[1:]
        }) if driver_data and kart_data else pd.DataFrame(columns=['Driver', 'Kart'])

    def get_driver_names(self) -> list:
        return ['Driver'] + self.df_drivers['Driver'].tolist()

    def get_kart_numbers(self) -> list:
        return ['Kart'] + self.df_drivers['Kart'].tolist()

    def get_time_list(self) -> list:
        if self.df_laps.empty:
            return []

        return [self.df_laps.columns.tolist()] + self.df_laps.values.tolist()

    def get_side_information(self) -> list:
        return self.side_info

    def get_stint_info(self) -> list:
        return self.stint_info

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
