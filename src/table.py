from prettytable import PrettyTable


class Table:
    def __init__(self):
        pass
    def add_row_table(self, table: PrettyTable, args: list):
        table.add_rows([args])