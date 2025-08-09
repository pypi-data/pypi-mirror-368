import pandas as pd
import numpy as np

class Dummy:

    @staticmethod
    def get_univariate_df():
        df = pd.DataFrame({
        'A': np.random.randint(1, 10, size=10),
        'B': np.random.randint(1, 10, size=10),
        'C': np.random.randint(1, 10, size=10),
        'D': np.random.randint(1, 10, size=10),
        'E': np.random.randint(1, 10, size=10),
        'F': np.random.randint(1, 10, size=10)
        })

        missing_indices = np.random.choice(df.index, size=3, replace=False)
        df.loc[missing_indices, 'C'] = np.nan
        return df
    
    @staticmethod
    def get_monotone_df():
        # Create an empty DataFrame
        df = pd.DataFrame(index=range(20), columns=['A', 'B', 'C', 'D', 'E', 'F'])

        # Assigning initial values
        df['A'] = 1
        df['B'] = 2
        df['C'] = 3
        df['D'] = 4
        df['E'] = 5
        df['F'] = 6
        df['G'] = 6

        # Introduce missing values (np.nan) to establish dependencies

        # Random positions for initial None placements that respect the dependencies
        a_missing = np.random.choice(df.index, size=3, replace=False)
        b_missing = np.random.choice(df.index, size=2, replace=False)
        c_missing = np.random.choice(df.index, size=2, replace=False)
        e_missing = np.random.choice(df.index, size=2, replace=False)
        f_missing = np.random.choice(df.index, size=2, replace=False)

        # Place initial missing values
        df.loc[a_missing, 'A'] = np.nan
        df.loc[b_missing, 'B'] = np.nan
        df.loc[c_missing, 'C'] = np.nan
        df.loc[e_missing, 'E'] = np.nan
        df.loc[f_missing, 'F'] = np.nan

        # Enforce dependencies:
        # A -> B, D
        df.loc[df['A'].isna(), ['B', 'D']] = np.nan
        # C -> F (also need to handle A -> B -> C chain reaction)
        df.loc[df['C'].isna(), 'F'] = np.nan
        df.loc[17, "D"] = np.nan

        return df

    @staticmethod
    def get_non_monotone():
        df = pd.DataFrame({
        'A': [None, 2, 3, None],
        'B': [1, None, None, 4],
        'C': [None, None, 3, 4]
        })
        return df
    
    @staticmethod
    def get_mar_df():
        df = pd.DataFrame({
        'A': np.random.randint(0, 100, 100),  # Random integers between 0 and 99
        'B': np.random.normal(50, 10, 100),   # Normally distributed data
        'C': np.random.choice(['X', 'Y', 'Z'], 100),  # Random categorical data
        'D': np.random.randint(0, 100, 100),  # Random integers between 0 and 99
        })
        # Introduce missing values
        # MAR: Missing in 'B' depending on 'A' (e.g., missing if A < 50)
        df.loc[df['A'] < 50, 'B'] = np.nan
        # non-MAR: Missing completely at random in 'A'
        missing_indices = np.random.choice(df.index, size=20, replace=False)  # Randomly pick 20 indices
        df.loc[missing_indices, 'A'] = np.nan
        return df
    

    @staticmethod
    def create_sample_dataframe(num_rows: int=10) -> pd.DataFrame:
        """
        Creates a pandas DataFrame with 3 continuous features, 
        3 categorical (string) features, and 1 datetime feature.
        Each column will have a random number of null values.

        Args:
            num_rows (int): The number of rows in the DataFrame.

        Returns:
            pd.DataFrame: A DataFrame with mixed data types.
        """
        
        # Continuous features
        np.random.seed(42)  # For reproducibility
        continuous_1 = np.random.normal(loc=50, scale=10, size=num_rows)
        continuous_2 = np.random.normal(loc=100, scale=20, size=num_rows)
        continuous_3 = np.random.normal(loc=0, scale=5, size=num_rows)
        
        # Categorical features
        categories = ['A', 'B', 'C']
        categorical_1 = np.random.choice(categories, size=num_rows)
        categorical_2 = np.random.choice(['X', 'Y'], size=num_rows)
        categorical_3 = np.random.choice(['Yes', 'No'], size=num_rows)
        
        # Datetime feature
        datetime_feature = pd.date_range(start='2023-01-01', periods=num_rows, freq='D')
        
        # Create DataFrame
        df = pd.DataFrame({
            'continuous_1': continuous_1,
            'continuous_2': continuous_2,
            'continuous_3': continuous_3,
            'categorical_1': categorical_1,
            'categorical_2': categorical_2,
            'categorical_3': categorical_3,
            'datetime_feature': datetime_feature
        })

        for col in df.columns:
            num_nulls = np.random.randint(1, num_rows)  # Random number of nulls
            null_indices = np.random.choice(df.index, num_nulls, replace=False)  # Random indices for nulls
            df.loc[null_indices, col] = np.nan
        
        return df 
    
    @staticmethod
    def introduce_random_missingness(df, lower_threshold=0.1, upper_threshold=0.3):
        for column in df.columns:
            random_percentage = np.random.uniform(lower_threshold, upper_threshold)
            num_nulls = int(len(df) * random_percentage)
            null_indices = np.random.choice(df.index, size=num_nulls, replace=False)
            df.loc[null_indices, column] = np.nan
        return df
    
    @staticmethod
    def generate_mar_test_data(num_samples=1000, seed=42):
        """
        Generates a synthetic dataset with MAR and MCAR missing patterns.
        
        Args:
            num_samples (int): Number of samples to generate
            seed (int): Random seed for reproducibility
        
        Returns:
            pd.DataFrame: DataFrame with:
            - age: Normally distributed values
            - income: Right-skewed values
            - missing_feature_mar: Feature with MAR missingness (dependent on income)
            - missing_feature_mcar: Feature with MCAR missingness
            - noise: Random noise feature
        """
        np.random.seed(seed)
        
        # Base features
        data = pd.DataFrame({
            'age': np.random.normal(40, 15, num_samples).astype(int),
            'income': np.random.gamma(shape=2, scale=20000, size=num_samples).astype(int),
            'noise': np.random.uniform(0, 1, num_samples)
        })
        
        # Create MAR missingness (dependent on income)
        income_threshold = np.percentile(data['income'], 75)
        mar_missing_mask = data['income'] > income_threshold
        data['missing_feature_mar'] = np.random.normal(0, 1, num_samples)
        data.loc[mar_missing_mask, 'missing_feature_mar'] = np.nan
        
        # Create MCAR missingness (completely random)
        mcar_missing_mask = np.random.rand(num_samples) < 0.3
        data['missing_feature_mcar'] = np.random.normal(0, 1, num_samples)
        data.loc[mcar_missing_mask, 'missing_feature_mcar'] = np.nan
        
        # Add some non-missing related features
        data['age'] = np.clip(data['age'], 18, 100)
        data['income'] = np.clip(data['income'], 20000, 150000)
        
        return data
    
    @staticmethod
    def generate_6_cols(n_rows: int = 100, random_state: int = None) -> pd.DataFrame:
        rng = np.random.RandomState(random_state)
        
        # Base DataFrame
        df = pd.DataFrame({
            "A_no_nulls": rng.normal(size=n_rows),
            "B_some_nulls": rng.normal(size=n_rows),
            "C_no_nulls_int": rng.randint(0, 10, size=n_rows),
            "D_some_nulls_str": rng.choice(["foo", "bar", "baz"], size=n_rows),
            "E_all_nulls": np.nan,
            "F_some_nulls": rng.normal(size=n_rows),
        })
        
        # Introduce ~33% nulls in B_some_nulls
        idx_b = rng.choice(n_rows, size=n_rows // 3, replace=False)
        df.loc[idx_b, "B_some_nulls"] = np.nan
        
        # Introduce ~25% nulls in D_some_nulls_str
        idx_d = rng.choice(n_rows, size=n_rows // 4, replace=False)
        df.loc[idx_d, "D_some_nulls_str"] = None

        # Introduce ~50% nulls in F_some_nulls
        idx_f = rng.choice(n_rows, size=n_rows // 2, replace=False)
        df.loc[idx_f, "F_some_nulls"] = np.nan
        
        return df
