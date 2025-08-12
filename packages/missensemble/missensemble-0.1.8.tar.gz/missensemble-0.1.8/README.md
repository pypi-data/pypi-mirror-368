# MissEnsemble

MissEnsemble is a generalization of the popular Missforest algorithm for missing value imputation. It generalizes the MissForest algorithm to different ensemble methods. The package follows the scikit-learn API. Ensemble methods currently supported: 

- Random Forests
- XGBoost

MissEnsemble handles different types of input values (e.g., strings, numbers, etc) natively. The only you have to do is to specify which column names belong to which categorics (i.e., numerical, categorical or ordinal variable).

In addition, MissEnsemble has built-in visualization functions for convergence and missing value validation (in case the original values are known).

## Setup
Download it from pypi with:

```bash
pip install missensemble
```

## Usage (Example)

To use it, you need to specify the columns names that imputation should target as strings within lists. Note that categorical, ordinal and numerical values are handled differently. Here is an example where 5 variables are set as target for imputation:

```python
from missensemble import MissEnsemble

# Initialize the MissEnsemble class
estimator = MissEnsemble(categorical_vars=['cat_var1', 'cat_var2'], ordinal_vars=['ord_var'], numerical_vars=['num_var1', 'num_var2'])

# Fit and transform the data
imputed_data = estimator.fit_transform(data)
```
For an extended usage example see the `example.ipynb` notebook. 

## Parameters
The `MissEnsemble` class can receive the following parameters which affects how imputation is performed:

- `n_iter` (int): The number of iterations to perform for imputation.
- `categorical_vars` (list): A list of column names representing categorical variables.
- `ordinal_vars` (list): A list of column names representing ordinal variables.
- `numerical_vars` (list): A list of column names representing numerical variables.
- `ens_method` (str, optional) : The ensemble method to use for imputation. Default is 'forest'.
- `n_estimators` (int, optional) : The number of estimators to use in the ensemble method. Default is 100.
- `random_state` (in, optional) : The random state for reproducibility. Default is 42.
- `print_criteria` (bool, optional) : Whether to print the imputation criteria during fitting. Default is True.

## Visualization methods
The `MissEnsemble` class offers a range of visualization functionalities regarding convergence and imputation checks (the latter only in cases where true values are available).

### Convergence criteria
When the class has been fitted, the `plot_criteria` method can be used to show the minimization path of the stopping criteria. Here is an example which has both numerical and non-numerical arguments: 

```python
estimator.plot_criteria(plot_final=False)
```

which results in the following plot:

![imputation criteria](docs/images/imputation_criteria.png)

### Imputation check
The `check_imputation_fit` method plots divergence of the imputed values as compared to the true values. In the following example, we check the imputation of `var1`: 

```python
estimator.check_imputation_fit(var_name='var1',
                              true_values = data.loc[:, 'var1'], 
                               error_type = 'std_diff', 
                               plot_type = 'hist')
```

which results in the following plot:

![imputation check](docs/images/imputation_check.png)

Different divergence and plot types are offered in this method. 

## Literature
Stekhoven, D. J., & Bühlmann, P. (2012). MissForest—non-parametric missing value imputation for mixed-type data. Bioinformatics, 28(1), 112-118.

