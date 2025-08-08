import unittest
from typing import Any
from src.StructResult.result import Simple, Error, List, Null


class TestResultProtocols(unittest.TestCase):
    def setUp(self) -> None:
        self.exception1 = ValueError("Error 1")
        self.exception2 = TypeError("Error 2")
        self.exception_group = ExceptionGroup("msg", [self.exception1, self.exception2])

    def test_simple_ok(self) -> None:
        res = Simple[int](value=42)
        self.assertEqual(res.value, 42)
        self.assertIsNone(res.err)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 42)
        self.assertEqual(list(res), [42, None])

    def test_simple_err(self) -> None:
        res = Simple[int](value=42)
        res.append_err(self.exception1)
        self.assertEqual(res.value, 42)
        self.assertIsNotNone(res.err)
        self.assertFalse(res.is_ok())
        with self.assertRaises(ExceptionGroup):
            res.unwrap()
        self.assertEqual(list(res), [42, res.err])

    def test_null(self) -> None:
        self.assertFalse(Null().is_ok())

    def test_error(self) -> None:
        err = Error(self.exception1, msg="test")
        self.assertIsNotNone(err.err)
        self.assertFalse(err.is_ok())

    def test_list_append(self) -> None:
        lst = List[int]()
        lst.append(Simple[int](value=1))
        lst.append(Simple[int](value=2))
        self.assertEqual(lst.value, [1, 2])
        self.assertIsNone(lst.err)
        self.assertTrue(lst.is_ok())

    def test_list_append_with_errors(self) -> None:
        lst = List[int]()
        res1 = Simple[int](value=1)
        res1.append_err(self.exception1)
        res2 = Simple[int](value=2)
        res2.append_err(self.exception2)

        lst.append(res1)
        lst.append(res2)

        self.assertEqual(lst.value, [1, 2])
        self.assertIsNotNone(lst.err)
        if lst.err is not None:
            self.assertEqual(len(lst.err.exceptions), 2)
        self.assertFalse(lst.is_ok())

    def test_list_add_operator(self) -> None:
        lst = List[int]()
        res1 = Simple[int](value=1)
        res2 = Simple[int](value=2)
        lst += res1
        lst += res2
        self.assertEqual(lst.value, [1, 2])

    def test_propagate_err(self) -> None:
        target = Simple[str](msg="target")
        source_ok = Simple[str](value="ok")
        source_err = Simple[str](value="err")
        source_err.append_err(self.exception1)

        # Propagate from OK result
        result = target.propagate_err(source_ok)
        self.assertEqual(result, "ok")
        self.assertIsNone(target.err)

        # Propagate from error result
        result = target.propagate_err(source_err)
        self.assertEqual(result, "err")
        self.assertIsNotNone(target.err)
        if target.err is not None:
            self.assertEqual(len(target.err.exceptions), 1)

    def test_error_grouping(self) -> None:
        grouper = Simple[Any](msg="group")
        grouper.append_err(self.exception1)
        grouper.append_err(self.exception2)

        self.assertIsNotNone(grouper.err)
        if grouper.err is not None:
            self.assertEqual(len(grouper.err.exceptions), 2)
            self.assertEqual(grouper.err.message, "group")

    def test_exception_group_merging(self) -> None:
        grouper = Simple[Any](msg="group")
        group1 = ExceptionGroup("group", [self.exception1])
        group2 = ExceptionGroup("group", [self.exception2])

        grouper.append_err(group1)
        grouper.append_err(group2)

        self.assertIsNotNone(grouper.err)
        if grouper.err is not None:
            self.assertEqual(len(grouper.err.exceptions), 2)
            self.assertEqual(grouper.err.message, "group")

    def test_different_message_groups(self) -> None:
        grouper = Simple[Any](msg="main")
        group = ExceptionGroup("other", [self.exception1])

        grouper.append_err(group)

        self.assertIsNotNone(grouper.err)
        # Should be wrapped in a new group with "main" message
        if grouper.err is not None:
            self.assertEqual(grouper.err.message, "other")
            self.assertEqual(len(grouper.err.exceptions), 1)
        self.assertIsInstance(grouper.err, ExceptionGroup)

    def test_simple_append(self) -> None:
        simple = Simple[Any]()
        res_ok = Simple[int](value=42)
        res_err = Simple[int](value=0)
        res_err.append_err(self.exception1)

        # Append OK result
        simple.set(res_ok)
        self.assertEqual(simple.value, 42)
        self.assertIsNone(simple.err)

        # Append error result
        simple.set(res_err)
        self.assertEqual(simple.value, 0)
        self.assertIsNotNone(simple.err)

    def test_list_multiple_appends(self) -> None:
        lst = List[int]()
        res1 = Simple[int](value=1)
        res2 = Simple[int](value=2)
        res3 = Simple[int](value=3)
        res3.append_err(self.exception1)

        lst.append(res1)
        lst.append(res2)
        lst.append(res3)

        self.assertEqual(lst.value, [1, 2, 3])
        self.assertIsNotNone(lst.err)
        if lst.err is not None:
            self.assertEqual(len(lst.err.exceptions), 1)
