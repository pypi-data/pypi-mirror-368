import typing

import csvdir


def test_simple():
    reader = csvdir.read_dir('tests/data')
    names = reader.names
    assert names == ['people', 'people2']
    iter_reader = iter(reader)
    assert next(iter_reader) == {'id': '1', 'name': 'Odos', 'age': '38'}
    assert next(iter_reader) == {'id': '2', 'name': 'Kayla', 'age': '31'}
    assert next(iter_reader) == {'id': '3', 'name': 'Dexter', 'age': 'two'}
    assert next(iter_reader) == {'id': '4', 'name': 'Joe', 'age': '44'}
    assert next(iter_reader) == {'id': '5', 'name': 'James', 'age': '55'}
    assert next(iter_reader) == {'id': '6', 'name': 'Luke', 'age': '0'}


def test_with_names():
    iter_reader = csvdir.read_dir('tests/data').with_names()
    assert next(iter_reader) == ('people', {'id': '1', 'name': 'Odos', 'age': '38'})
    assert next(iter_reader) == ('people', {'id': '2', 'name': 'Kayla', 'age': '31'})
    assert next(iter_reader) == ('people', {'id': '3', 'name': 'Dexter', 'age': 'two'})
    assert next(iter_reader) == ('people2', {'id': '4', 'name': 'Joe', 'age': '44'})
    assert next(iter_reader) == ('people2', {'id': '5', 'name': 'James', 'age': '55'})
    assert next(iter_reader) == ('people2', {'id': '6', 'name': 'Luke', 'age': '0'})


def test_with_paths():
    iter_reader = csvdir.read_dir('tests/data').with_paths()
    assert next(iter_reader) == ('tests/data/people.csv', {'id': '1', 'name': 'Odos', 'age': '38'})
    assert next(iter_reader) == ('tests/data/people.csv', {'id': '2', 'name': 'Kayla', 'age': '31'})
    assert next(iter_reader) == ('tests/data/people.csv', {'id': '3', 'name': 'Dexter', 'age': 'two'})
    assert next(iter_reader) == ('tests/data/people2.csv', {'id': '4', 'name': 'Joe', 'age': '44'})
    assert next(iter_reader) == ('tests/data/people2.csv', {'id': '5', 'name': 'James', 'age': '55'})
    assert next(iter_reader) == ('tests/data/people2.csv', {'id': '6', 'name': 'Luke', 'age': '0'})