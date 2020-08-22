import unittest

from version3 import BasicLexer, BasicParser, Interpreter

class MathOpsTest(unittest.TestCase):
    l = BasicLexer()
    p = BasicParser()
    i = Interpreter(l, p)

    def test_add(self):
        data = 'output[ 5 add 5 ]'
        data1 = 'output[ 0 add 0 ]'
        data2 = 'output[ 10 add -5 ]'

        expected = 10
        expected1 = 0
        expected2 = 5

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_minus(self):
        data = 'output[ 15 minus 5 ]'
        data1 = 'output[ 0 minus 0 ]'
        data2 = 'output[ 0 minus -10 ]'

        expected = 10
        expected1 = 0
        expected2 = 10

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_multiplied(self):
        data = 'output[ 5 multiplied 5 ]'
        data1 = 'output[ 0 multiplied 0 ]'
        data2 = 'output[ 10 multiplied -2 ]'

        expected = 25
        expected1 = 0
        expected2 = -20

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_divided(self):
        data = 'output[ 5 divided 5 ]'
        data1 = 'output[ 0 divided 5 ]'
        data2 = 'output[ 5 divided -2 ]'

        expected = 1
        expected1 = 0
        expected2 = -2.5

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_parenth(self):
        data = 'output[ ( 5 add  5 ) ]'
        data1 = 'output[ 5 minus ( 5 ) ]'
        data2 = 'output[ 5 multiplied ( 5 divided 2 ) ]'

        expected = 10
        expected1 = 0
        expected2 = 12.5

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

class variablesMathsTest(unittest.TestCase):
    l = BasicLexer()
    p = BasicParser()
    i = Interpreter(l, p)

    def test_var_saved(self):
        data = '''x equals 9
        output[ x ]'''
        data1 = '''x equals 0
        output[ x ]'''

        expected = 9
        expected1 = 0

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)

    def test_var_saved_add(self):
        data = '''x equals 5 add 5
        output[ x ]'''
        data1 = '''x equals 0 add 0
        output[ x ]'''
        data2 = '''x equals 10 add 0
        output[ x ]'''

        expected = 10
        expected1 = 0
        expected2 = 10

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_var_saved_minus(self):
        data = '''x equals 15 minus 5
        output[ x ]'''
        data1 = '''x equals 0 minus 0
        output[ x ]'''
        data2 = '''x equals 0 minus 10
        output[ x ]'''

        expected = 10
        expected1 = 0
        expected2 = -10

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_var_saved_multiplied(self):
        data = '''x equals 5 multiplied 5
        output[ x ]'''
        data1 = '''x equals 0 multiplied 0
        output[ x ]'''
        data2 = '''x equals 10 multiplied 0
        output[ x ]'''

        expected = 25
        expected1 = 0
        expected2 = 0

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_var_saved_divided(self):
        data = '''x equals 5 divided 5
        output[ x ]'''
        data1 = '''x equals 0 divided 5
        output[ x ]'''
        data2 = '''x equals 5 divided 2
        output[ x ]'''

        expected = 1
        expected1 = 0
        expected2 = 2.5

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

    def test_var_in_equation(self):
        data = '''x equals 5
        output[ x add 5 ]'''
        data1 = '''x equals 2 multiplied ( 5 add 5 )
        x equals x add 5
        output[ x ]'''
        data2 = '''x equals 5
        y equals 10
        output[ x add y ]'''

        expected = 10
        expected1 = 25
        expected2 = 15

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)
    
class stringsTest(unittest.TestCase):
    l = BasicLexer()
    p = BasicParser()
    i = Interpreter(l, p)

    def test_var_saved(self):
        data = '''output[ "hello" ]'''
        data1 = '''output[ "123" ]'''
        data2 = '''output[ "!£$%^&*()-_=+{}#~;:'@,<.>/?`" ]'''

        expected = 'hello'
        expected1 = '123'
        expected2 = "!£$%^&*()-_=+{}#~;:'@,<.>/?`"

        result = self.i.output(data)
        self.assertEqual(result, expected)
        result1 = self.i.output(data1)
        self.assertEqual(result1, expected1)
        result2 = self.i.output(data2)
        self.assertEqual(result2, expected2)

if __name__ == '__main__':
    unittest.main()
