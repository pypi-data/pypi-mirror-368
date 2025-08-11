# TOPSIS Program

## What is this program?

This Python program helps in decision-making by ranking different options based on multiple criteria. It uses a method called **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)** to calculate a score for each option and rank them from best to worst.

## What does it do?

The program takes data about different options, with several criteria for each option, and ranks them. You can specify the importance of each criterion (called **weights**) and whether you want the criteria to be a benefit (+) or a cost (-). After running the program, it gives you a rank for each option based on the calculations.

## How does it work?

1. **Input File**: You provide a file that lists the options and their values for each criterion.
2. **Weights**: You specify how important each criterion is.
3. **Impacts**: You specify if the criterion is a benefit (like higher values are better) or a cost (like lower values are better).
4. **Output File**: The program calculates a score for each option, adds the rank, and saves the results to a new file.

## Requirements

Make sure you have Python installed, and you will need to install a library called `pandas` to read and write the data files. You can install it by running:

```bash
pip install pandas
1. Prepare the Files
Input File: This is a CSV file with the data you want to process. It must have at least three columns: the first one for the name of the options (e.g., M1, M2, M3), and the others for the values of different criteria.

Example of Input Data (101556-data.csv):

Object	Criterion1	Criterion2	Criterion3
M1	100	200	300
M2	150	250	350
M3	120	220	330
Weights and Impacts: These are provided as comma-separated values. The weights tell you how important each criterion is, and the impacts tell you if a higher value is better (use +) or if a lower value is better (use -).
2. Running the Program
Run the program from the command line by typing:

bash
Copy
Edit
python <YourFileName.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>
<YourFileName.py>: The name of your Python program (e.g., 101556.py).
<InputDataFile>: The input data file (e.g., 101556-data.csv).
<Weights>: The importance of each criterion (e.g., "1,1,1,2").
<Impacts>: Whether each criterion is a benefit (+) or a cost (-) (e.g., "+,+,-,+").
<ResultFileName>: The name of the output file where the results will be saved (e.g., 101556-result.csv).
Example Command:
bash
Copy
Edit
python 101556.py 101556-data.csv "1,1,1,2" "+,+,-,+" 101556-result.csv
This will read the 101556-data.csv, calculate the Topsis scores, and save the result in 101556-result.csv.

What Does the Program Do?
Read Data: The program reads the input file and checks if it has at least 3 columns.
Normalize: It normalizes the values so that they can be compared fairly.
Apply Weights: It multiplies the values by the specified weights.
Ideal Solutions: The program identifies the best (ideal) and worst (negative-ideal) solutions.
Calculate Scores: It calculates a score for each option based on how close it is to the ideal solution.
Rank: It ranks the options based on the scores.
Error Handling
The program checks for:

Correct number of inputs (file names, weights, impacts).
If the file exists.
If the input data file has valid numbers and enough columns.
If the number of weights and impacts matches the number of criteria.
If the impacts are valid (either + or -).
Example of Output
After running the program, it will produce an output file that looks like this:

Object	Criterion1	Criterion2	Criterion3	Topsis Score	Rank
M1	100	200	300	0.75	1
M2	150	250	350	0.80	2
M3	120	220	330	0.70	3
The Topsis Score tells you how good each option is, and the Rank shows the best to worst alternatives.

Contributing
Feel free to make improvements or fix bugs by forking the repository and submitting a pull request.

License
This project is open source under the MIT License.

