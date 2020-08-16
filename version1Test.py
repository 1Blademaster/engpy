import unittest

from version1 import BasicLexer, BasicParser

class MathOpsTest(unittest.TestCase):
    l = BasicLexer()
    p = BasicParser()

    def test_add(self):
        data = '5 add 5'
        data1 = '0 add 0'
        data2 = '10 add 0'

        expected = 10
        expected1 = 0
        expected2 = 10

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_minus(self):
        data = '15 minus 5'
        data1 = '0 minus 0'
        data2 = '0 minus 10'

        expected = 10
        expected1 = 0
        expected2 = -10

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_multiplied(self):
        data = '5 multiplied 5'
        data1 = '0 multiplied 0'
        data2 = '10 multiplied 0'

        expected = 25
        expected1 = 0
        expected2 = 0

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)

    def test_divided(self):
        data = '5 divided 5'
        data1 = '0 divided 5'
        data2 = '5 divided 2'

        expected = 1
        expected1 = 0
        expected2 = 2.5

        result = self.p.parse(self.l.tokenize(data))
        self.assertEqual(result, expected)
        result1 = self.p.parse(self.l.tokenize(data1))
        self.assertEqual(result1, expected1)
        result2 = self.p.parse(self.l.tokenize(data2))
        self.assertEqual(result2, expected2)


if __name__ == '__main__':
    unittest.main()
