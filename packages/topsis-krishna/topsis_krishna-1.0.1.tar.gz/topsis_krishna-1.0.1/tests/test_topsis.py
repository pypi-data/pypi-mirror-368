import os
import unittest
import sys

# Add the topsis package directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'topsis')))

from topsis import topsis  # Assuming topsis is a function inside topsis.py

class TestTOPSIS(unittest.TestCase):

    def test_topsis(self):
        # Use the absolute file path for input and output
        input_file = r'C:/Users/krish/Desktop/topsis_package/tests/102366002_data.xlsx'
        output_file = r'C:/Users/krish/Desktop/topsis_package/tests/102366002_result.csv'
        
        # Check if the input file exists
        self.assertTrue(os.path.exists(input_file), f"The file '{input_file}' was not found. Please check the file path.")
        
        # Run the TOPSIS method
        weights = [1, 1, 1, 2, 1]  # Example weights
        impacts = ['+', '+', '-', '+', '+']  # Example impacts
        topsis(input_file, weights, impacts, output_file)
        
        # Check if the output file was created
        self.assertTrue(os.path.exists(output_file), f"The output file '{output_file}' was not created.")

if __name__ == "__main__":
    unittest.main()
