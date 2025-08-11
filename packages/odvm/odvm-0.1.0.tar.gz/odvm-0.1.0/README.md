
<div style="text-align: center; font-size: 2.5em; font-weight: bold; color: #4F46E5; letter-spacing: 2px;">
    <span style="color: #4F46E5;">O</span>
    <span style="color: #7C3AED;">D</span>
    <span style="color: #A78BFA;">V</span>
    <span style="color: #C4B5FD;">M</span>
</div>


<div align="center">
  <img src="https://img.shields.io/badge/AutoML-Intelligent_Automation-4F46E5?style=for-the-badge&logo=openai&logoColor=white" alt="AutoML">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Status-Beta-10B981?style=for-the-badge&logo=statuspal&logoColor=white" alt="Beta">
  <img src="https://img.shields.io/badge/License-MIT-000000?style=for-the-badge&logo=mit&logoColor=white" alt="MIT">
</div>

<div align="center" style="margin: 2rem 0; font-family: 'Segoe UI', sans-serif;">
  <h3 style="font-size: 1.5rem; color: #4F46E5; letter-spacing: 0.05em;">
    <span style="background: linear-gradient(90deg, #4F46E5, #A78BFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
      From Raw Data to Intelligent Insights
    </span>
  </h3>
  <p style="font-style: italic; color: #6B7280; font-size: 1.1rem;">
    Where data clarity meets <strong style="color: #7C3AED;">decision power</strong> through automated intelligence
  </p>
</div>


</div>

## Overview

**ODVM** is a modular AutoML pipeline that automates the entire data science workflow:

**Exploratory Data Analysis (EDA)** →  **Smart Preprocessing** → **Model Selection & Training** → **Reporting** 

Multi-backend support (Pandas, Dask) and extensible architecture accelerate your ML projects while maintaining transparency.

---

## Documentation Summary

| Module / Class                       | Method / Function          | Description (Humanized)                                               | Sample Code Example                                       |
|------------------------------------|---------------------------|----------------------------------------------------------------------|-----------------------------------------------------------|
| **core.runner.ODVM**                | `__init__`                | Initialize the pipeline with data, target column, and config settings.| ```python\nodvm = ODVM(data="data.csv", target="price", config=config)\n``` |
|                                    | `_load_data`              | Load data from file path or DataFrame.                               | ```python\ndf = odvm._load_data("data.csv")\n```                        |
|                                    | `_validate`               | Check that the target column exists in the dataset.                  | ```python\nodvm._validate()\n```                                         |
|                                    | `run`                     | Run the full pipeline with options for each stage (EDA, preprocessing, modeling, reporting, deployment). | ```python\nodvm.run(eda=True, preprocess=True, model=True)\n```         |
|                                    | `run_eda`                 | Perform exploratory data analysis with charts and stats.             | ```python\nodvm.run_eda()\n```                                           |
|                                    | `run_preprocessing`       | Clean, encode, split, and scale the data preparing for modeling.     | ```python\nodvm.run_preprocessing()\n```                                 |
|                                    | `run_modeling`            | Select, tune, train, and evaluate models automatically.              | ```python\nodvm.run_modeling()\n```                                      |
|                                    | `generate_report`         | (Work in progress) Generate detailed performance reports.            | ```python\nodvm.generate_report()\n```                                   |
|                                    | `deploy_model`            | (Work in progress) Deploy model via REST API or dashboard.           | ```python\nodvm.deploy_model()\n```                                      |
|                                    | `save_best_model`         | Save the best trained model to a pickle file for later use.          | ```python\nodvm.save_best_model(results, models_dict)\n```               |
| **assistant.task_detector.TaskDetector** | `detect`                  | Automatically detect task type: classification, regression, clustering, etc. | ```python\ntask_info = TaskDetector(df, target="price").detect()\n```   |
| **eda.analyzer.EDAAnalyzer**       | `get_shape`               | Get the shape of the dataset (rows and columns).                      | ```python\nrows, cols = analyzer.get_shape()\n```                        |
|                                    | `get_columns_info`        | Get information about columns and their data types.                   | ```python\ninfo = analyzer.get_columns_info()\n```                       |
|                                    | `missing_values`          | Analyze and report missing values in each column.                     | ```python\nmissings = analyzer.missing_values()\n```                     |
|                                    | `save_summary`            | Save EDA summary statistics to a JSON file.                           | ```python\nanalyzer.save_summary("eda_summary.json")\n```                |
| **eda.visualizer.EDAVisualizer**   | `plot_distributions`      | Plot distributions for numerical and categorical features.            | ```python\nvisualizer.plot_distributions()\n```                          |
|                                    | `plot_boxplots`           | Plot boxplots to check outliers and spread.                           | ```python\nvisualizer.plot_boxplots()\n```                               |
|                                    | `plot_correlation`        | Plot correlation heatmap for numerical features.                      | ```python\nvisualizer.plot_correlation()\n```                            |
|                                    | `plot_target_distribution`| Plot distribution of the target variable.                             | ```python\nvisualizer.plot_target_distribution()\n```                    |
|                                    | `plot_pairplot`           | Plot pairwise scatterplots for features.                              | ```python\nvisualizer.plot_pairplot()\n```                               |
| **preprocess.cleaner.DataCleaner** | `clean`                   | Clean data by handling missing values, duplicates, and outliers.      | ```python\ncleaned_df = cleaner.clean()\n```                             |
| **preprocess.encoder.Encoder**     | `encode`                  | Encode categorical/text features to numerical form.                   | ```python\nencoded_df = encoder.encode()\n```                            |
| **preprocess.scaler.Scaler**       | `fit_transform`           | Fit scaler on training data and transform it.                         | ```python\nX_train_scaled = scaler.fit_transform(X_train)\n```          |
|                                    | `transform`               | Transform validation/test data using fitted scaler.                   | ```python\nX_test_scaled = scaler.transform(X_test)\n```                 |
| **preprocess.splitter.DataSplitter** | `split`                   | Split dataset into train, validation, and test sets.                   | ```python\nX_train, X_val, X_test, y_train, y_val, y_test = splitter.split()\n``` |
| **modeling.model_selector.ModelSelector** | `get_models`              | Get a dictionary of models suitable for the detected task.            | ```python\nmodels = selector.get_models()\n```                           |
| **modeling.tuner.ModelTuner**      | `tune`                    | Tune model hyperparameters using grid or random search.               | ```python\nbest_model = tuner.tune()\n```                                |
| **modeling.trainer.ModelTrainer**  | `train_all`               | Train all selected (and tuned) models.                                | ```python\ntrained_models, params = trainer.train_all()\n```             |
| **modeling.evaluator.ModelEvaluator** | `evaluate`                | Evaluate models on test data and return performance metrics.           | ```python\nresults = evaluator.evaluate()\n```                           |
| **reporting.report_builder.ReportBuilder** | `build`                   | Build performance reports in HTML or Excel format.                     | ```python\nreport.build()\n```                                           |

---

## Quick Start Example

```python
from core.runner import ODVM

config = {
    "eda": {"visualize": True, "save_summary": True},
    "preprocessing": {"missing_strategy": "mean", "encoding": "label", "scaling": "standard"},
    "split": {"test_size": 0.2, "val_size": 0.1, "random_state": 42},
    "modeling": {"allowed_models": ["LinearRegression"], "tuning": True, "cv": 3, "scoring": "r2"}
}

odvm = ODVM(data="data/housing.csv", target="median_house_value", config=config)
odvm.run(eda=True, preprocess=True, model=True)

```
## Contributing

We welcome all contributions, big or small!

To get started:

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Open a Pull Request

---

### Contact

[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:omnia18ayman@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/omnia-ayman-1b8340269/)
