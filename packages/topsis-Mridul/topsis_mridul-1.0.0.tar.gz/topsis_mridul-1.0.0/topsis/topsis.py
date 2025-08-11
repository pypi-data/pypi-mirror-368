import numpy as np
import pandas as pd
import sys

class Topsis:
    """
    TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    
    A class for implementing the TOPSIS multi-criteria decision-making method.
    """
    
    def __init__(self, data_file=None, weights=None, impacts=None, result_file=None):
        """
        Initialize TOPSIS with parameters.
        
        Args:
            data_file (str): Path to the input CSV file
            weights (list): List of weights for each criterion
            impacts (list): List of impacts ('+' or '-') for each criterion
            result_file (str): Path to save the result CSV file
        """
        self.data_file = data_file
        self.weights = weights
        self.impacts = impacts
        self.result_file = result_file
        self.data = None
        self.scores = None
        
    def validate_inputs(self, args=None):
        """Validate command line inputs or instance variables."""
        if args is not None:
            # Command line mode
            print("Validating inputs...")
            if len(args) != 5:
                raise ValueError("Incorrect number of parameters. Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")

            input_file, weights, impacts, result_file = args[1:]

            # Validate weights and impacts
            weights = weights.split(',')
            impacts = impacts.split(',')

            try:
                weights = [float(w) for w in weights]
            except ValueError:
                raise ValueError("Weights must be numeric and separated by commas.")

            if not all(i in ['+', '-'] for i in impacts):
                raise ValueError("Impacts must be '+' or '-' and separated by commas.")

            print("Inputs validated successfully.")
            return input_file, weights, impacts, result_file
        else:
            # Class mode
            if self.data_file is None or self.weights is None or self.impacts is None:
                raise ValueError("data_file, weights, and impacts must be provided.")
            
            if len(self.weights) != len(self.impacts):
                raise ValueError("Number of weights and impacts must be the same.")
                
            if not all(i in ['+', '-'] for i in self.impacts):
                raise ValueError("Impacts must be '+' or '-'.")
                
            return self.data_file, self.weights, self.impacts, self.result_file

    def load_and_validate_data(self, input_file=None):
        """Load and validate the input data."""
        if input_file is None:
            input_file = self.data_file
            
        print(f"Loading data from '{input_file}'...")
        try:
            self.data = pd.read_csv(input_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{input_file}' not found.")

        print("Data loaded successfully.")
        if self.data.shape[1] < 3:
            raise ValueError("Input file must contain at least three columns.")

        for col in self.data.columns[1:]:
            if not pd.api.types.is_numeric_dtype(self.data[col]):
                raise ValueError(f"Column '{col}' must contain numeric values only.")

        print("Data validation complete.")
        return self.data

    def calculate_topsis(self, data=None, weights=None, impacts=None):
        """Calculate TOPSIS scores."""
        if data is None:
            data = self.data
        if weights is None:
            weights = self.weights
        if impacts is None:
            impacts = self.impacts
            
        print("Performing TOPSIS...")
        # Convert data to numpy array for calculations
        matrix = data.iloc[:, 1:].values

        # Step 1: Normalize the decision matrix
        norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
        print("Normalization complete.")

        # Step 2: Weight the normalized matrix
        weighted_matrix = norm_matrix * weights
        print("Weighting complete.")

        # Step 3: Identify the ideal (best) and anti-ideal (worst) solutions
        ideal_solution = np.zeros(weighted_matrix.shape[1])
        anti_ideal_solution = np.zeros(weighted_matrix.shape[1])

        for i in range(weighted_matrix.shape[1]):
            if impacts[i] == '+':  # Beneficial criterion
                ideal_solution[i] = weighted_matrix[:, i].max()
                anti_ideal_solution[i] = weighted_matrix[:, i].min()
            elif impacts[i] == '-':  # Non-beneficial criterion
                ideal_solution[i] = weighted_matrix[:, i].min()
                anti_ideal_solution[i] = weighted_matrix[:, i].max()

        print("Ideal and anti-ideal solutions identified.")

        # Step 4: Calculate the separation measures
        separation_ideal = np.sqrt(((weighted_matrix - ideal_solution) ** 2).sum(axis=1))
        separation_anti_ideal = np.sqrt(((weighted_matrix - anti_ideal_solution) ** 2).sum(axis=1))
        print("Separation measures calculated.")

        # Step 5: Calculate the TOPSIS score
        self.scores = separation_anti_ideal / (separation_ideal + separation_anti_ideal)
        print("TOPSIS scores calculated.")

        return self.scores

    def save_results(self, result_file=None):
        """Save results to CSV file."""
        if result_file is None:
            result_file = self.result_file
            
        if self.data is None or self.scores is None:
            raise ValueError("No data or scores available. Run calculate_topsis first.")
            
        # Add TOPSIS scores and rank to the data
        result_data = self.data.copy()
        result_data['Topsis Score'] = self.scores
        result_data['Rank'] = result_data['Topsis Score'].rank(ascending=False).astype(int)
        print("Scores and ranks added to the data.")

        # Save the result to a file
        result_data.to_csv(result_file, index=False)
        print(f"Results saved to '{result_file}'.")
        return result_data

    def run(self):
        """Run the complete TOPSIS analysis."""
        try:
            print("Starting TOPSIS analysis...")
            # Validate inputs
            self.validate_inputs()

            # Load and validate the input data
            self.load_and_validate_data()

            # Validate the consistency of weights, impacts, and columns
            if len(self.weights) != len(self.impacts) or len(self.weights) != self.data.shape[1] - 1:
                raise ValueError("Number of weights, impacts, and columns (from 2nd to last) must be the same.")

            print("Consistency of weights, impacts, and columns validated.")

            # Perform TOPSIS
            self.calculate_topsis()

            # Save results
            if self.result_file:
                return self.save_results()
            else:
                # Return results without saving
                result_data = self.data.copy()
                result_data['Topsis Score'] = self.scores
                result_data['Rank'] = result_data['Topsis Score'].rank(ascending=False).astype(int)
                return result_data

        except Exception as e:
            print(f"Error: {e}")
            raise

def validate_inputs(args):
    """Legacy function for command line compatibility."""
    print("Validating inputs...")
    if len(args) != 5:
        raise ValueError("Incorrect number of parameters. Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")

    input_file, weights, impacts, result_file = args[1:]

    # Validate weights and impacts
    weights = weights.split(',')
    impacts = impacts.split(',')

    try:
        weights = [float(w) for w in weights]
    except ValueError:
        raise ValueError("Weights must be numeric and separated by commas.")

    if not all(i in ['+', '-'] for i in impacts):
        raise ValueError("Impacts must be '+' or '-' and separated by commas.")

    print("Inputs validated successfully.")
    return input_file, weights, impacts, result_file

def load_and_validate_data(input_file):
    """Legacy function for command line compatibility."""
    print(f"Loading data from '{input_file}'...")
    try:
        data = pd.read_csv(input_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{input_file}' not found.")

    print("Data loaded successfully.")
    if data.shape[1] < 3:
        raise ValueError("Input file must contain at least three columns.")

    for col in data.columns[1:]:
        if not pd.api.types.is_numeric_dtype(data[col]):
            raise ValueError(f"Column '{col}' must contain numeric values only.")

    print("Data validation complete.")
    return data

def topsis(data, weights, impacts):
    """Legacy function for command line compatibility."""
    print("Performing TOPSIS...")
    # Convert data to numpy array for calculations
    matrix = data.iloc[:, 1:].values

    # Step 1: Normalize the decision matrix
    norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
    print("Normalization complete.")

    # Step 2: Weight the normalized matrix
    weighted_matrix = norm_matrix * weights
    print("Weighting complete.")

    # Step 3: Identify the ideal (best) and anti-ideal (worst) solutions
    ideal_solution = np.zeros(weighted_matrix.shape[1])
    anti_ideal_solution = np.zeros(weighted_matrix.shape[1])

    for i in range(weighted_matrix.shape[1]):
        if impacts[i] == '+':  # Beneficial criterion
            ideal_solution[i] = weighted_matrix[:, i].max()
            anti_ideal_solution[i] = weighted_matrix[:, i].min()
        elif impacts[i] == '-':  # Non-beneficial criterion
            ideal_solution[i] = weighted_matrix[:, i].min()
            anti_ideal_solution[i] = weighted_matrix[:, i].max()

    print("Ideal and anti-ideal solutions identified.")

    # Step 4: Calculate the separation measures
    separation_ideal = np.sqrt(((weighted_matrix - ideal_solution) ** 2).sum(axis=1))
    separation_anti_ideal = np.sqrt(((weighted_matrix - anti_ideal_solution) ** 2).sum(axis=1))
    print("Separation measures calculated.")

    # Step 5: Calculate the TOPSIS score
    scores = separation_anti_ideal / (separation_ideal + separation_anti_ideal)
    print("TOPSIS scores calculated.")

    return scores

def main():
    """Main function for command line usage."""
    try:
        print("Starting TOPSIS analysis...")
        # Validate command-line arguments
        input_file, weights, impacts, result_file = validate_inputs(sys.argv)

        # Load and validate the input data
        data = load_and_validate_data(input_file)

        # Validate the consistency of weights, impacts, and columns
        if len(weights) != len(impacts) or len(weights) != data.shape[1] - 1:
            raise ValueError("Number of weights, impacts, and columns (from 2nd to last) must be the same.")

        print("Consistency of weights, impacts, and columns validated.")

        # Perform TOPSIS
        scores = topsis(data, weights, impacts)

        # Add TOPSIS scores and rank to the data
        data['Topsis Score'] = scores
        data['Rank'] = data['Topsis Score'].rank(ascending=False).astype(int)
        print("Scores and ranks added to the data.")

        # Save the result to a file
        data.to_csv(result_file, index=False)
        print(f"Results saved to '{result_file}'.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()