import unittest

from parser import parse_body

class TestParser(unittest.TestCase):

    def test_parse_body(self):
        test_body = """
        key1: value1
        
        key2: value2

        key3: value3

        """
        expected_result = {"key1": "value1", "key2": "value2", "key3": "value3"}
        self.assertEqual(parse_body(test_body), expected_result)
    
    def test_parse_body_empty(self):
        self.assertEqual(parse_body(""), {})

    def test_parse_body_extended_empty(self):
        empty_body = """

         
          
            
             
               
                

                
                    """
        self.assertEqual(parse_body(empty_body), {})


if __name__ == '__main__':
    unittest.main()
