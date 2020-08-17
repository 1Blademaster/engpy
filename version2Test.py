import unittest

from version2 import BasicLexer, BasicParser

class MathOpsTest(unittest.TestCase):
    l = BasicLexer()
    p = BasicParser()

    def test_add(self):
        data = '5 add 5'
        data1 = '0 add 0'
        data2 = '10 add -5'

        expected = 10
        expected1 = 0
        expected2 = 5

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_minus(self):
        data = '15 minus 5'
        data1 = '0 minus 0'
        data2 = '0 minus -10'

        expected = 10
        expected1 = 0
        expected2 = 10

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_multiplied(self):
        data = '5 multiplied 5'
        data1 = '0 multiplied 0'
        data2 = '10 multiplied -2'

        expected = 25
        expected1 = 0
        expected2 = -20

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_divided(self):
        data = '5 divided 5'
        data1 = '0 divided 5'
        data2 = '5 divided -2'

        expected = 1
        expected1 = 0
        expected2 = -2.5

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_parenth(self):
        data = '(5 add 5)'
        data1 = '5 minus (5)'
        data2 = '5 multiplied (5 divided 2)'

        expected = 10
        expected1 = 0
        expected2 = 12.5

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

class variablesTest(unittest.TestCase):
    l = BasicLexer()
    p = BasicParser()

    def test_var_saved(self):
        data = 'x equals 9'
        data1 = 'x equals 0'

        expected = 9
        expected1 = 0

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)

    def test_var_saved_add(self):
        data = '''x equals 5 add 5'''
        data1 = '''x equals 0 add 0'''
        data2 = '''x equals 10 add 0'''

        expected = 10
        expected1 = 0
        expected2 = 10

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_var_saved_minus(self):
        data = '''x equals 15 minus 5'''
        data1 = '''x equals 0 minus 0'''
        data2 = '''x equals 0 minus 10'''

        expected = 10
        expected1 = 0
        expected2 = -10

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_var_saved_multiplied(self):
        data = '''x equals 5 multiplied 5'''
        data1 = '''x equals 0 multiplied 0'''
        data2 = '''x equals 10 multiplied 0'''

        expected = 25
        expected1 = 0
        expected2 = 0

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_var_saved_divided(self):
        data = '''x equals 5 divided 5'''
        data1 = '''x equals 0 divided 5'''
        data2 = '''x equals 5 divided 2'''

        expected = 1
        expected1 = 0
        expected2 = 2.5

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_var_in_equation(self):
        data = '''x equals 5
        x add 5'''
        data1 = '''
        x equals 2 multiplied (5 add 5)
        x equals 5
        '''
        data2 = '''
        x equals 5
        y equals 10
        x add y
        '''

        expected = 10
        expected1 = 5
        expected2 = 15

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)
    

if __name__ == '__main__':
    unittest.main()
