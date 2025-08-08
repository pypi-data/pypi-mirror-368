# =======================================================================
#
#  This file is part of WebWidgets, a Python package for designing web
#  UIs.
#
#  You should have received a copy of the MIT License along with
#  WebWidgets. If not, see <https://opensource.org/license/mit>.
#
#  Copyright(C) 2025, mlaasri
#
# =======================================================================

from webwidgets.utility.representation import ReprMixin


class TestRepresentation:
    def test_repr_without_attributes(self):
        """Test case without any attributes"""
        class EmptyClass(ReprMixin):
            pass
        empty_obj = EmptyClass()
        assert str(empty_obj) == "EmptyClass()"

    def test_repr_with_none_value(self):
        """Test case with None value for an attribute"""
        class MyClass(ReprMixin):
            def __init__(self, a, b=None):
                self.a = a
                self.b = b
        obj = MyClass(1)
        assert str(obj) == "MyClass(a=1, b=None)"

    def test_repr_with_multiple_attributes(self):
        """Test case with multiple attributes"""
        class ComplexClass(ReprMixin):
            def __init__(self, a, b, c=None, d=None):
                self.a = a
                self.b = b
                self.c = c
                self.d = d
        obj = ComplexClass(1, 2, c=3, d=4)
        assert str(obj) == "ComplexClass(a=1, b=2, c=3, d=4)"

    def test_repr_with_multiple_types(self):
        """Test case with multiple types of attributes"""
        class MixedTypeClass(ReprMixin):
            def __init__(self, a: int, b: float, c: str):
                self.a = a
                self.b = b
                self.c = c
        obj = MixedTypeClass(1, 2.5, "test")
        assert str(obj) == "MixedTypeClass(a=1, b=2.5, c='test')"

    def test_repr_with_large_number_of_attributes(self):
        """Test case with a large number of attributes"""
        class LargeObject(ReprMixin):
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        obj = LargeObject(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10)
        assert str(
            obj) == "LargeObject(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10)"

    def test_repr_with_nested_objects(self):
        """Test case with nested object as attribute"""
        class Inner(ReprMixin):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        class Outer(ReprMixin):
            def __init__(self, obj=None):
                self.obj = obj
        complex_obj = Outer(obj=Inner(a=1, b=2))
        assert str(complex_obj) == "Outer(obj=Inner(a=1, b=2))"

    def test_repr_with_nested_list(self):
        """Test case with list of objects as attribute"""
        class Inner(ReprMixin):
            def __init__(self, a):
                self.a = a

        class Outer(ReprMixin):
            def __init__(self):
                self.obj = [Inner(1), Inner(2)]
        obj = Outer()
        assert str(obj) == "Outer(obj=[Inner(a=1), Inner(a=2)])"

    def test_repr_with_nested_dict(self):
        """Test case with list of objects as attribute"""
        class Inner(ReprMixin):
            def __init__(self, a):
                self.a = a

        class Outer(ReprMixin):
            def __init__(self):
                self.d = {
                    "1": Inner(1),
                    "2": Inner(2)
                }
        obj = Outer()
        assert str(obj) == "Outer(d={'1': Inner(a=1), '2': Inner(a=2)})"

    def test_repr_with_nested_dict_of_list(self):
        """Test case with dict containing list of objects as attribute"""
        class Inner(ReprMixin):
            def __init__(self, a):
                self.a = a

        class Outer(ReprMixin):
            def __init__(self):
                self.d = {
                    "odd": [Inner(1), Inner(3)],
                    "even": [Inner(2)]
                }
        obj = Outer()
        assert str(obj) == "Outer(d={'odd': [Inner(a=1), " \
            "Inner(a=3)], 'even': [Inner(a=2)]})"
