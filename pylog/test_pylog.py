import datetime
import unittest

from pylog import events

EVENT_LISTS = { 
    "1": [
        events.CallEvent(file_name="foo.py", line_number=8, function_name="main"),
        events.CallEvent(file_name="bar.py", line_number=22, function_name="somefunc"),
        events.CallEvent(file_name="baz.py", line_number=27, function_name="func3"),
        events.ReturnEvent(file_name="baz.py", line_number=27, function_name="func3"),
        events.ReturnEvent(file_name="bar.py", line_number=22, function_name="somefunc"),
        events.CallEvent(file_name="bar.py", line_number=50, function_name="someotherfunc"),
        events.ReturnEvent(file_name="bar.py", line_number=50, function_name="someotherfunc"),
        events.ReturnEvent(file_name="foo.py", line_number=8, function_name="main"),
    ],
}

class TestEvent(unittest.TestCase):
    """The Event classes"""

    events = {
        "event": {
            "timestamp": "1989-03-11T13:30:01.234567",
            "file_name": "my_file.py",
            "line_number": 7,
        },
    }
    events["line"] = dict(**events["event"])
    events["function"] = dict(
        function_name="some_func",
        **events["event"]
    )
    events["call"] = dict(
        args={"num": 1, "str": "foo"},
        **events["function"]
    )
    events["return"] = dict(
        rval="[1, 2, 3]",
        **events["function"]
    )
    events["exception"] = dict(**events["function"])
    for event_type, event in events.items():
        event["type"] = event_type

    expected_attrs = {
        "timestamp": datetime.datetime(
            year=1989,
            month=3,
            day=11,
            hour=13,
            minute=30,
            second=1,
            microsecond=234567,
        ),
        "file_name": "my_file.py",
        "line_number": 7,
        "function_name": "some_func",
        "args": {"num": 1, "str": "foo"},
        "rval": "[1, 2, 3]",
    }

    def tearDown(self):
        pass

    def test_event(self):
        evt_data = self.events["event"]
        evt = events.Event.from_data(evt_data)
        for attr in ["timestamp", "file_name", "line_number"]:
            self.assertEqual(getattr(evt, attr), self.expected_attrs[attr])
        back_to_data = evt.to_data()
        self.assertEqual(evt_data, back_to_data)

class TestFunction(unittest.TestCase):
    """Tests events.Function"""

    def setUp(self):
        self.function = events.Function(
            name="some_func",
            file_name="foo.py",
            line_number=7,
            called_by=["b", "c"],
        )

    def tearDown(self):
        pass

    def test_key(self):
        self.assertEqual(self.function.key, ("some_func", "foo.py", 7))

    def test_to_data(self):
        self.assertEqual(
            self.function.to_data(),
            {
                "name": "some_func",
                "file_name": "foo.py",
                "line_number": 7,
                "called_by": ["b", "c"],
                "calls": [],
            }
        )

class TestFunctionSet(unittest.TestCase):
    """test events.FunctionSet"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_function(self):
        fset = events.FunctionSet()
        func1 = fset.add_function_from_event(events.event_from_data(TestEvent.events["call"]))
        func2 = fset.add_function("some_other_func", "foo.py", 17)
        fset.add_call(func1, func2)
        self.assertEqual(
            list(sorted(fset.to_data(), key=lambda a: a["name"])),
            [{'called_by': [],
              'calls': [('some_other_func', 'foo.py', 17)],
              'file_name': 'my_file.py',
              'line_number': 7,
              'name': 'some_func'},
             {'called_by': [('some_func', 'my_file.py', 7)],
              'calls': [],
              'file_name': 'foo.py',
              'line_number': 17,
              'name': 'some_other_func'}
            ]
        )
    def test_from_events(self):
        fset = events.FunctionSet.from_events(EVENT_LISTS["1"])
        self.assertEqual(list(sorted(fset.to_data(), key=lambda a: a["name"])),
            [{'called_by': [('somefunc', 'bar.py', 22)],
              'calls': [],
              'file_name': 'baz.py',
              'line_number': 27,
              'name': 'func3'},
             {'called_by': [],
              'calls': [('somefunc', 'bar.py', 22), ('someotherfunc', 'bar.py', 50)],
              'file_name': 'foo.py',
              'line_number': 8,
              'name': 'main'},
             {'called_by': [('main', 'foo.py', 8)],
              'calls': [('func3', 'baz.py', 27)],
              'file_name': 'bar.py',
              'line_number': 22,
              'name': 'somefunc'},
             {'called_by': [('main', 'foo.py', 8)],
              'calls': [],
              'file_name': 'bar.py',
              'line_number': 50,
              'name': 'someotherfunc'}]
        )
    def test_to_flame(self):
        #FIXME add timestamps to events so this test passes
        etree = events.ExecutionTree.from_events(EVENT_LISTS["1"])
        etree.to_flame_chart(100)
        #self.assertEqual(etree.sub_events[0].to_flame_2(100), {
            #'start_time': '2015-05-07T00:37:32.189008',
            #'calls': [
                #{'parent_id': None, 'depth': 0, 'ret_time': 0.000112, 'name': 'main', 'args': None, 'retval': None, 'id': 1, 'call_time': 0.0},
                #{'parent_id': 1, 'depth': 1, 'ret_time': 7.7e-05, 'name': 'somefunc', 'args': None, 'retval': None, 'id': 2, 'call_time': 3.7e-05},
                #{'parent_id': 2, 'depth': 2, 'ret_time': 6.5e-05, 'name': 'func3', 'args': None, 'retval': None, 'id': 3, 'call_time': 5.1e-05},
                #{'parent_id': 1, 'depth': 1, 'ret_time': 0.0001, 'name': 'someotherfunc', 'args': None, 'retval': None, 'id': 4, 'call_time': 8.9e-05}
            #]})
        #self.assertEqual(etree.sub_events[0].to_flame_2(0), {
            #'start_time': '2015-05-07T00:37:32.189008',
            #'calls': [
                #{'parent_id': None, 'depth': 0, 'ret_time': 0.000112, 'name': 'main', 'args': None, 'retval': None, 'id': 1, 'call_time': 0.0},
                #{'parent_id': 1, 'depth': 1, 'ret_time': 7.7e-05, 'name': 'somefunc', 'args': None, 'retval': None, 'id': 2, 'call_time': 3.7e-05},
                #{'parent_id': 1, 'depth': 1, 'ret_time': 0.0001, 'name': 'someotherfunc', 'args': None, 'retval': None, 'id': 4, 'call_time': 8.9e-05}
            #]})

if __name__ == '__main__':
    unittest.main()