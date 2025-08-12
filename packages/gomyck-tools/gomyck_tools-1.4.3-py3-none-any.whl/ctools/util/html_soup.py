from bs4 import BeautifulSoup

from ctools.ex import exception_handler


@exception_handler(fail_return=['解析错误'], print_exc=True)
def table2list(html, include_header=True, recursive_find=True,
               table_tag='table', table_class=None, table_attrs: dict = {},
               row_tag='tr', row_class=None, row_attrs: dict = {},
               header_cell_tag='th', header_cell_class=None, header_cell_attrs: dict = {},
               cell_tag='td', cell_class=None, cell_attrs: dict = {}):
  soup = BeautifulSoup(markup=html, features='html.parser')
  if table_class:
    table = soup.find(table_tag, class_=table_class, **table_attrs)
  else:
    table = soup.find(table_tag, **table_attrs)
  if row_class:
    all_row = table.find_all(row_tag, class_=row_class, recursive=recursive_find, **row_attrs)
  else:
    all_row = table.find_all(row_tag, recursive=recursive_find, **row_attrs)
  rows = []
  if include_header:
    if header_cell_class:
      header = [i.text for i in all_row[0].find_all(header_cell_tag, class_=header_cell_class, recursive=recursive_find, **header_cell_attrs)]
    else:
      header = [i.text for i in all_row[0].find_all(header_cell_tag, recursive=recursive_find, **header_cell_attrs)]
    rows.append(header)
  for tr in all_row[1 if include_header else 0:]:
    if cell_class:
      td = tr.find_all(cell_tag, class_=cell_class, recursive=recursive_find, **cell_attrs)
    else:
      td = tr.find_all(cell_tag, recursive=recursive_find, **cell_attrs)
    row = [i.text for i in td]
    rows.append(row)
  return rows
