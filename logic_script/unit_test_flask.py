import unittest
from src.logic_script import convert_time

class Basic_tests(unittest.TestCase):
    obj_convert_test = convert_time.TimeConvertet()

    def test_convert_test_normal(self):
        sample = [('00:00', '7:10', '8:00'),('00:00', '7:10', '8:00'),('00:00', '8:10', '8:00'),
                  ('01:20', '10:10', '8:00'), ('04:00', '20:10', '17:00'), ('7:00', '7:10', '8:00')]
        answer = [0,0,1,1,1,0]
        for i, tup in enumerate(sample):
            print(f'sample {tup} answers {answer[i]}')
        # func = self.obj_convert_test.convert_test()


if __name__ == '__main__':
    unittest.main()



