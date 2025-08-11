import numpy as np
import pandas as pd

def topsis(input_file, weights, impacts, output_file):
    try:
        # Validate parameters
        if not input_file or not weights or not impacts or not output_file:
            raise ValueError("All parameters (inputFileName, Weights, Impacts, resultFileName) must be provided.")

        if not isinstance(weights, list) or not isinstance(impacts, list):
            raise ValueError("Weights and impacts must be provided as lists.")
        if len(weights) != len(impacts):
            raise ValueError("Number of weights and impacts must match.")
        if not all(impact in ['+', '-'] for impact in impacts):
            raise ValueError("Impacts must only contain '+' or '-'.")
        
        # Read input file as Excel
        try:
            data = pd.read_excel(input_file)  # Use read_excel for .xlsx file
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{input_file}' was not found. Please check the file path.")

        print("Initial Dataset:")
        print(data)

        # Validate data format
        if data.shape[1] < 3:
            raise ValueError("Input file must contain at least three columns (one identifier and at least two criteria).")

        object_names = data.iloc[:, 0]  # Object names (first column)
        numerical_data = data.iloc[:, 1:]  # Numerical criteria columns

        # Check if all criteria are numeric
        if not numerical_data.apply(pd.to_numeric, errors='coerce').notnull().all().all():
            raise ValueError("All criteria columns (from the 2nd column onward) must contain numeric values only.")

        if len(weights) != numerical_data.shape[1]:
            raise ValueError("Number of weights must match the number of criteria columns.")

        # Normalize the data
        normalized_data = numerical_data / np.sqrt((numerical_data ** 2).sum())
        print("\nNormalized Data:")
        print(normalized_data)

        # Apply weights
        weights = np.array(weights, dtype=float)
        weighted_data = normalized_data * weights
        print("\nWeighted Data:")
        print(weighted_data)

        # Determine ideal best and worst values
        ideal_best = []
        ideal_worst = []
        for i, impact in enumerate(impacts):
            if impact == '+':
                ideal_best.append(weighted_data.iloc[:, i].max())
                ideal_worst.append(weighted_data.iloc[:, i].min())
            else:
                ideal_best.append(weighted_data.iloc[:, i].min())
                ideal_worst.append(weighted_data.iloc[:, i].max())
        print("\nIdeal Best Values:")
        print(ideal_best)
        print("\nIdeal Worst Values:")
        print(ideal_worst)

        # Calculate distances to ideal best and worst
        distance_best = np.sqrt(((weighted_data - ideal_best) ** 2).sum(axis=1))
        distance_worst = np.sqrt(((weighted_data - ideal_worst) ** 2).sum(axis=1))
        print("\nDistance to Ideal Best:")
        print(distance_best)
        print("\nDistance to Ideal Worst:")
        print(distance_worst)

        # Calculate TOPSIS scores
        scores = distance_worst / (distance_best + distance_worst)
        print("\nTOPSIS Scores:")
        print(scores)

        # Add scores and ranks to the data
        data['Topsis Score'] = scores
        data['Rank'] = scores.rank(ascending=False).astype(int)
        print("\nFinal Dataset with Scores and Ranks:")
        print(data)

        # Save the results to the output file
        data.to_csv(output_file, index=False)
        print(f"\nResults successfully saved to {output_file}")

    except ValueError as ve:
        print(f"ValueError: {ve}")
    except FileNotFoundError as fnfe:
        print(f"FileNotFoundError: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Command-line interface for the TOPSIS package"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='TOPSIS Decision Making Tool')
    parser.add_argument('input_file', help='Input Excel file path')
    parser.add_argument('weights', help='Comma-separated weights (e.g., "1,1,1,2")')
    parser.add_argument('impacts', help='Comma-separated impacts (e.g., "+,+,-,+")')
    parser.add_argument('output_file', help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Parse weights and impacts
    weights = [float(w.strip()) for w in args.weights.split(',')]
    impacts = [i.strip() for i in args.impacts.split(',')]
    
    # Call the topsis function
    topsis(args.input_file, weights, impacts, args.output_file)

if __name__ == "__main__":
    main()
