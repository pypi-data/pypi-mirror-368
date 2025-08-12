import re
import pandas as pd

pd.options.display.width = None


class DataframeCleaner:
    def __init__(self, frame: pd.DataFrame):
        self.df = frame.copy()
        self._strip_values()
        self._remove_nans()

    def _strip_values(self):
        """
        Стрипает все строковые значения в датафрейме.
        """
        self.df = self.df.map(lambda x: x.strip() if isinstance(x, str) else x)

    def _remove_nans(self):
        """
        Удаляет полностью пустые (все NaN) колонки и строки.
        """
        self.df = self.df.dropna(how='all', axis=1)
        self.df = self.df.dropna(how='all', axis=0).reset_index(drop=True)

    @staticmethod
    def _excel_addr_to_indices(addr: str):
        """
        Преобразует адрес ячейки Excel (например, "A1", "BC12") в кортеж (row_idx, col_idx),
        где row_idx и col_idx — целочисленные индексы (0-основанные).
        """
        # Мачим буквы (колонка) и цифры (строка)
        m = re.match(r'^([A-Za-z]+)(\d+)$', addr)
        if not m:
            raise ValueError(f"Неправильный формат адреса ячейки: '{addr}'")
        col_letters = m.group(1).upper()
        row_number = int(m.group(2))

        # Переводим буквенную часть в число (A→1, B→2, ..., Z→26, AA→27 и т.д.)
        col_idx = 0
        for char in col_letters:
            col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
        col_idx -= 1  # сделать 0-основанным

        row_idx = row_number - 1  # 0-основанный индекс строки

        return row_idx, col_idx

    def adj_by_row_index(self, key: str):
        """
        Если key похоже на адрес ячейки (например, "A1"), получает из него row_idx,
        иначе ищет строку, где встречается значение key.
        Далее устанавливает имена колонок по найденной строке и обрезает всё до этой строки включительно.

        Возвращает изменённый датафрейм.
        """
        # Проверяем, задан ли key как адрес ячейки
        addr_pattern = r'^[A-Za-z]+\d+$'
        if re.match(addr_pattern, key):
            # Это адрес ячейки
            row_idx, col_idx = self._excel_addr_to_indices(key)

            # Проверяем, что индексы в пределах df
            max_row = len(self.df) - 1
            max_col = len(self.df.columns) - 1
            if row_idx > max_row or col_idx > max_col:
                raise IndexError(f"Адрес '{key}' выходит за пределы DataFrame "
                                 f"({max_row + 1} строк, {max_col + 1} столбцов).")

            # Получаем название колонок из указанной строки
            self.df.columns = self.df.iloc[row_idx].values
            # Оставляем только строки начиная с row_idx+1 (после строки с заголовками)
            self.df = self.df.drop(index=range(row_idx + 1)).reset_index(drop=True)
        else:
            # Обычный поиск по значению
            row_idxs = self.df.index[self.df.eq(key).any(axis=1)].tolist()
            if not row_idxs:
                raise ValueError(f"Значение '{key}' не найдено ни в одной строке.")
            first_row = row_idxs[0]
            self.df.columns = self.df.loc[first_row].values
            self.df = self.df.drop(index=range(first_row + 1)).reset_index(drop=True)

        return self.df

    def remove_duplicated_cols(self):
        """
        Удаляет повторяющиеся названия колонок, оставляя только первые вхождения.
        """
        self.df = self.df.loc[:, ~self.df.columns.duplicated()]
        return self.df

    def __repr__(self):
        return self.df.__repr__()


if __name__ == '__main__':
    # Пример использования:
    df = pd.read_excel(r'C:\Users\SLAlnazarov\Documents\Python\01062025\NewWorkbook.xlsx')
    cleaner = DataframeCleaner(df)

    # Пример 1: установка заголовков по значению "Name"
    cleaner.adj_by_row_index("A1")
    cleaner.remove_duplicated_cols()
    print(cleaner.df)

    # Пример 2: установка заголовков по адресу "A1"
    # cleaner = DataframeCleaner(df)  # заново, если нужно повторно
    # cleaner.adj_by_row_index("A1")
    # cleaner.remove_duplicated_cols()
    # print(cleaner.df)
