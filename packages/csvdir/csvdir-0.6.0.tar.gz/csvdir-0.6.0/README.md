A Python package used to iterate through a directory of csv files and read each row as a dict.

Install
```console
pip install csvdir
```

Examples
```sh
>>> import csvdir

>>> reader = csvdir.read_dir('data/')
>>> reader.names
['people1', 'people2']
>>> reader.paths
['data/people1.csv', 'data/people2.csv']

>>> for row in reader:
...    print(row)
...
{'id': '1', 'name': 'Odos', 'age': '38'},
{'id': '2', 'name': 'Kayla', 'age': '31'},
{'id': '3', 'name': 'Dexter', 'age': 'two'},
{'id': '4', 'name': 'Joe', 'age': '44'},
{'id': '5', 'name': 'James', 'age': '55'},
{'id': '6', 'name': 'Luke', 'age': '0'}

>>> for name, row in reader.with_names():
...    print(name, row)
...
'people1' {'id': '1', 'name': 'Odos', 'age': '38'},
'people1' {'id': '2', 'name': 'Kayla', 'age': '31'},
'people1' {'id': '3', 'name': 'Dexter', 'age': 'two'},
'people2' {'id': '4', 'name': 'Joe', 'age': '44'},
'people2' {'id': '5', 'name': 'James', 'age': '55'},
'people2' {'id': '6', 'name': 'Luke', 'age': '0'}

>>> for path, row in reader.with_paths():
...    print(path, row)
...
'data/people1.csv' {'id': '1', 'name': 'Odos', 'age': '38'},
'data/people1.csv' {'id': '2', 'name': 'Kayla', 'age': '31'},
'data/people1.csv' {'id': '3', 'name': 'Dexter', 'age': 'two'},
'data/people2.csv' {'id': '4', 'name': 'Joe', 'age': '44'},
'data/people2.csv' {'id': '5', 'name': 'James', 'age': '55'},
'data/people2.csv' {'id': '6', 'name': 'Luke', 'age': '0'}
```