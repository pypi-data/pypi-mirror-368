from excelsior import Scanner
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "../../test/test_new_ws.xlsx")
scanner = Scanner(file_path)
print(scanner.get_sheets())
editor = scanner.open_editor(scanner.get_sheets()[0])
editor.add_worksheet('Sheet2')
editor.add_worksheet('Sheet3').append_table_at([["10", "20", "30"], ["30", "40", "50"]], "B2")
editor.add_worksheet_at('Title', 0).append_table_at([["1", "2", "3"], ["3", "4", "5"]], "A1")
editor.with_worksheet("Sheet2").append_table_at([["1", "2", "3"], ["3", "4", "5"]], "A1")
editor.save(file_path + "_out.xlsx")
assert 'Sheet2' in Scanner(file_path + "_out.xlsx").get_sheets() 
assert 'Sheet3' in Scanner(file_path + "_out.xlsx").get_sheets() 
assert Scanner(file_path + "_out.xlsx").get_sheets()[0] == "Title"

print('Done')