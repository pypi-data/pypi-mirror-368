TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)

TOPSIS is a Python library for implementing the Technique for Order of Preference by Similarity to Ideal Solution, a multi-criteria decision-making method. This library allows users to rank alternatives based on given criteria, weights, and impacts.

Installation

You can install the library via pip:

pip install topsis-Mridul

Usage

Command-line Usage

The library can be used directly from the command line. Here's the general syntax:

python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>

Example

Create an input file, data.csv:

Name,C1,C2,C3,C4
A,250,16,12,5
B,200,32,8,3
C,300,24,10,4
D,275,20,11,4
E,225,28,9,2

Run the command:

python topsis.py data.csv "0.25,0.25,0.25,0.25" "+,+,-,+" result.csv

The output result.csv will contain:

Name,C1,C2,C3,C4,Topsis Score,Rank
A,250,16,12,5,0.64,2
B,200,32,8,3,0.43,4
C,300,24,10,4,0.78,1
D,275,20,11,4,0.56,3
E,225,28,9,2,0.36,5

Python Library Usage

Importing the Library

You can also use the library directly in Python:

from topsis import Topsis

# Input data
data = "data.csv"
weights = [0.25, 0.25, 0.25, 0.25]
impacts = ["+", "+", "-", "+"]
result_file = "result.csv"

# Perform TOPSIS
Topsis(data, weights, impacts, result_file)
print(f"Results saved in {result_file}")

Parameters

InputDataFile: A CSV file with the first column as the name of the alternatives and the rest as numeric criteria.

Weights: A comma-separated string of numeric weights (e.g., "0.25,0.25,0.25,0.25").

Impacts: A comma-separated string of impacts for each criterion, either + (positive impact) or - (negative impact).

ResultFileName: The name of the output CSV file where results will be saved.

Features

Validate input file format and values.

Handle missing or invalid values gracefully.

Normalize and weight criteria.

Calculate TOPSIS scores and rankings.

Limitations

All criteria must be numeric.

The number of weights and impacts must match the number of criteria.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Contributing

Feel free to open issues or create pull requests to improve the library!


