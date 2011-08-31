"""
TODO doc me

"""


import logging
import sys
from datetime import date, time, datetime
from collections import Counter


from petl.profile import Profiler, RowLengths, DistinctValues, BasicStatistics,\
    Types


logger = logging.getLogger('petl')
d, i, w, e = logger.debug, logger.info, logger.warn, logger.error # abbreviations
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_profile_default():
    """TODO doc me"""

    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]

    profiler = Profiler(table)

    d('profile the table with default analyses')
    report = profiler.profile()
    default = report['table']['default'] 
    assert default['fields'] == ('foo', 'bar', 'baz')
    assert default['sample_size'] == 5


def test_profile_row_lengths():
    """TODO doc me"""

    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]

    profiler = Profiler(table)
        
    d('profile with row lengths analysis')
    profiler.add(RowLengths)
    report = profiler.profile()
    row_lengths = report['table']['row_lengths'] 
    assert row_lengths['max_row_length'] == 4
    assert row_lengths['min_row_length'] == 2
    assert row_lengths['mean_row_length'] == 3.


def test_profile_distinct_values():

    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]

    profiler = Profiler(table)

    d('profile with distinct values analysis on field "foo"')
    profiler.add(DistinctValues, field='foo')
    report = profiler.profile()
    distinct_values = report['field']['foo']['distinct_values'] 
    assert distinct_values == Counter({'A': 1, 'B': 2, 'D': 1, 'E': 1})


def test_profile_basic_statistics():

    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]

    profiler = Profiler(table)
    
    d('add basic statistics analysis on field "bar"')
    profiler.add(BasicStatistics, field='bar')
    report = profiler.profile()
    basic_statistics = report['field']['bar']['basic_statistics']
    assert basic_statistics['min'] == 1.0
    assert basic_statistics['max'] == 3.0
    assert basic_statistics['mean'] == 2.0
    assert basic_statistics['sum'] == 6.0
    assert basic_statistics['count'] == 3
    assert basic_statistics['errors'] == 2


def test_profile_types():

    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]

    profiler = Profiler(table)
    
    d('add types analysis on all fields')
    profiler.add(Types) 
    report = profiler.profile()

    foo_types = report['field']['foo']['types'] 
    assert foo_types['actual_types'] == Counter({'str': 4, 'unicode': 1})
    assert foo_types['parse_types'] == Counter()
    assert foo_types['consensus_types'] == Counter({'str': 4, 'unicode': 1})

    bar_types = report['field']['bar']['types'] 
    assert bar_types['actual_types'] == Counter({'int': 1, 
                                                 'str': 2, 
                                                 'unicode': 1, 
                                                 'NoneType': 1})
    assert bar_types['parse_types'] == Counter({'int': 2, 
                                                'float': 2})
    assert bar_types['consensus_types'] == Counter({'int': 3, 
                                                    'float': 2, 
                                                    'str': 2, 
                                                    'unicode': 1,
                                                    'NoneType': 1})

    baz_types = report['field']['baz']['types']
    assert baz_types['actual_types'] == Counter({'int': 1, 
                                                 'float': 1,
                                                 'str': 1,
                                                 'unicode': 1, 
                                                 'ellipsis': 1})
    assert baz_types['parse_types'] == Counter({'float': 2})     
    assert baz_types['consensus_types'] == Counter({'float': 3, 
                                                    'int': 1,
                                                    'str': 1,
                                                    'unicode': 1,
                                                    'ellipsis': 1})



def test_profile_types_datetime():

    table = [['date'],
             [date(1999, 12, 31)],
             ['31/12/99'],
             [' 31/12/1999 '], # throw some ws in as well
             [u'31 Dec 99'],
             ['31 Dec 1999'],
             ['31. Dec. 1999'],
             ['31 December 1999'], 
             ['31. December 1999'], 
             ['Fri 31 Dec 99'],
             ['Fri 31/Dec 99'],
             ['Fri 31 December 1999'],
             ['Friday 31 December 1999'],
             ['12-31'],
             ['99-12-31'],
             ['1999-12-31'], # iso 8601
             ['12/99'],
             ['31/Dec'],
             ['12/31/99'],
             ['12/31/1999'],
             ['Dec 31, 99'],
             ['Dec 31, 1999'],
             ['December 31, 1999'],
             ['Fri, Dec 31, 99'],
             ['Fri, December 31, 1999'],
             ['Friday, 31. December 1999'],
             ['I am not a date.'],
             [None]
             ] 

    profiler = Profiler(table)
    
    d('add types analysis on "date" field')
    profiler.add(Types, field='date') 
    report = profiler.profile()

    date_types = report['field']['date']['types']
    assert date_types['actual_types'] == Counter({'date': 1, 
                                                  'str': 24, 
                                                  'unicode': 1, 
                                                  'NoneType': 1})
    assert date_types['parse_types'] == Counter({'date': 24})
    assert date_types['consensus_types'] == Counter({'date': 25, 
                                                     'str': 24, 
                                                     'unicode': 1, 
                                                     'NoneType': 1})

    table = [['time'],
             [time(13, 37, 46)],
             ['13:37'],
             [' 13:37:46 '], # throw some ws in as well
             [u'01:37 PM'],
             ['01:37:46 PM'],
             ['37:46.00'],
             ['13:37:46.00'], 
             ['01:37:46.00 PM'],
             ['01:37PM'],
             ['01:37:46PM'],
             ['01:37:46.00PM'],
             ['I am not a time.'], 
             [None]
             ] 

    profiler = Profiler(table)
    
    d('add types analysis on "time" field')
    profiler.add(Types, field='time') 
    report = profiler.profile()
    
    time_types = report['field']['time']['types']
    assert time_types['actual_types'] == Counter({'time': 1, 
                                                  'str': 10, 
                                                  'unicode': 1, 
                                                  'NoneType': 1})
    assert time_types['parse_types'] == Counter({'time': 10})
    assert time_types['consensus_types'] == Counter({'time': 11, 
                                                     'str': 10,
                                                     'unicode': 1,
                                                     'NoneType': 1})

    table = [['datetime'],
             [datetime(1999, 12, 31, 13, 37, 46)],
             ['1999-12-31T13:37:46'],
             [' 1999-12-31T13:37:46.00 '],
             [u'1999-12-31 13:37:46'],
             ['1999-12-31 13:37:46.00'],
             ['I am not a datetime.'], 
             [None]
             ] 

    profiler = Profiler(table)
    
    d('add types analysis on "datetime" field')
    profiler.add(Types, field='datetime') 
    report = profiler.profile()
    
    datetime_types = report['field']['datetime']['types']
    assert datetime_types['actual_types'] == Counter({'datetime': 1, 
                                                      'str': 4, 
                                                      'unicode': 1, 
                                                      'NoneType': 1})
    assert datetime_types['parse_types'] == Counter({'datetime': 4})
    assert datetime_types['consensus_types'] == Counter({'datetime': 5, 
                                                         'str': 4,
                                                         'unicode': 1,
                                                         'NoneType': 1})


def test_profile_types_bool():

    table = [['bool'],
             [True],
             [False],
             ['true'],
             [' True '], # throw some ws in as well
             [u'false'],
             ['T'],
             ['f'],
             ['yes'], 
             ['No'], 
             ['Y'],
             ['n'],
             ['1'],
             ['0'],
             ['I am not a bool.'],
             [None]
             ] 

    profiler = Profiler(table)
    
    d('add types analysis on "bool" field')
    profiler.add(Types, field='bool') 
    report = profiler.profile()

    bool_types = report['field']['bool']['types']
    assert bool_types['actual_types'] == Counter({'bool': 2, 
                                                  'str': 11, 
                                                  'unicode': 1, 
                                                  'NoneType': 1})
    assert bool_types['parse_types'] == Counter({'bool': 11,
                                                 'int': 2,
                                                 'float': 2})
    assert bool_types['consensus_types'] == Counter({'bool': 13, 
                                                     'str': 11, 
                                                     'int': 2,
                                                     'float': 2,
                                                     'unicode': 1, 
                                                     'NoneType': 1})
