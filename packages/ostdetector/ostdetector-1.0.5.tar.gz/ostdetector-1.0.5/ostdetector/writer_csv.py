import csv
import os
# from datetime import datetime

class WriterCSV:
  def __init__(self, name, path='data'):
    self.name = name
    self.path = path

  def write(self, head, rows):
    parent = os.path.dirname(self.path)
    if parent == "":
        os.makedirs(self.path, exist_ok=True)
    # csv_filename = f"{self.path}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.name}.csv"
    csv_filename = f"{self.path}/{self.name}.csv"
    with open(csv_filename, 'w') as file:
        write = csv.writer(file, delimiter =";")
        write.writerow(head)
        write.writerows(rows)