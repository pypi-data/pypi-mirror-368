"""
Basic usage example for Ethical AI Validator.

This example demonstrates how to use the EthicalAIValidator
to audit a machine learning model for bias, fairness, and compliance.

This comprehensive example shows:
1. Data preparation with synthetic sensitive features
2. Model training using scikit-learn with multiple hyperparameter configurations
3. Bias detection across multiple protected attributes
4. Fairness metrics calculation
5. Compliance report generation
6. Real-time monitoring setup
7. Mitigation suggestions

The example uses synthetic data to simulate a real-world scenario
where an organization needs to audit their AI model for ethical
compliance and fairness across different demographic groups.

Author: WHIS (muhammadabdullahinbox@gmail.com)
Version: 1.1.0
Repository: https://github.com/whis-19/ethical-ai
Documentation: https://whis-19.github.io/ethical-ai/
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
try:
    import xgboost as xgb  # type: ignore
    _HAS_XGB = True
except Exception:
    _HAS_XGB = False

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ethical_ai_validator.ethical_ai_validator import EthicalAIValidator


def run_single_model_scenario(model_name, model, X_train, X_test, y_train, y_test, 
                            sensitive_features, validator, scenario_name, config_name):
    """
    Run ethical AI validation for a single model scenario.
    
    Args:
        model_name: Name of the model for reporting
        model: Trained model instance
        X_train, X_test, y_train, y_test: Training and test data
        sensitive_features: DataFrame with sensitive attributes
        validator: EthicalAIValidator instance
        scenario_name: Name of the scenario for identification
        config_name: Name of the hyperparameter configuration
    
    Returns:
        dict: Results containing bias report, fairness metrics, and predictions
    """
    print(f"\n--- {scenario_name} ({model_name}) - {config_name} ---")
    
    # Get predictions and add bias to make results more dramatic
    predictions = model.predict(X_test)
    
    # Add bias to predictions based on sensitive features to demonstrate unfairness
    test_sensitive_features = sensitive_features.iloc[X_test.index]
    
    # Introduce bias in predictions: favor certain groups
    predictions_bias = predictions.copy()
    
    # Bias against males
    male_test_mask = test_sensitive_features['gender'] == 'male'
    predictions_bias[male_test_mask] = 0  # Always predict negative for males
    
    # Bias against older people
    older_test_mask = test_sensitive_features['age_group'].isin(['36-50', '50+'])
    predictions_bias[older_test_mask] = 0  # Always predict negative for older people
    
    # Bias against lower education
    low_edu_test_mask = test_sensitive_features['education'].isin(['high_school', 'bachelor'])
    predictions_bias[low_edu_test_mask] = 0  # Always predict negative for lower education
    
    # Bias in favor of females, young people, and high education
    female_test_mask = test_sensitive_features['gender'] == 'female'
    young_test_mask = test_sensitive_features['age_group'].isin(['18-25', '26-35'])
    high_edu_test_mask = test_sensitive_features['education'].isin(['master', 'phd'])
    
    # Favor these groups
    predictions_bias[female_test_mask] = 1  # Always predict positive for females
    predictions_bias[young_test_mask] = 1   # Always predict positive for young people
    predictions_bias[high_edu_test_mask] = 1  # Always predict positive for high education
    
    predictions = predictions_bias
    
    # Prepare sensitive features for the test set
    test_sensitive_features = sensitive_features.iloc[X_test.index]
    
    # Run bias audit
    bias_report = validator.audit_bias(
        predictions=predictions,
        true_labels=list(y_test),
        protected_attributes={
            'gender': test_sensitive_features['gender'].tolist(),
            'age_group': test_sensitive_features['age_group'].tolist(),
            'education': test_sensitive_features['education'].tolist()
        }
    )
    
    # Calculate fairness metrics
    fairness_metrics = validator.calculate_fairness_metrics(
        predictions=predictions,
        protected_attributes={
            'gender': test_sensitive_features['gender'].tolist(),
            'age_group': test_sensitive_features['age_group'].tolist(),
            'education': test_sensitive_features['education'].tolist()
        }
    )
    
    # Display results
    print(f"Model: {model_name} | Config: {config_name}")
    try:
        params_for_display = getattr(model, 'get_params', lambda: {})()
        if params_for_display:
            print("Hyperparameters:")
            for k, v in params_for_display.items():
                print(f"  - {k}: {v}")
    except Exception:
        pass
    print("Bias Analysis:")
    if not bias_report.empty:
        for _, row in bias_report.iterrows():
            print("  {} - {}: Bias Score {:.3f}".format(
                row['protected_attribute'], row['group'], row['bias_score']
            ))
    
    print("Fairness Assessment:")
    for attr_name, attr_metrics in fairness_metrics['fairness_scores'].items():
        print("  {}: Fairness Score {:.3f}".format(
            attr_name, attr_metrics['fairness_score']
        ))
    
    # Generate individual compliance report for this model
    print(f"\nGenerating compliance report for {model_name} ({config_name})...")
    metadata = {
        'model_name': model_name,
        'config_name': config_name,
        'version': '1.3',
        'scenario': scenario_name,
        'hyperparameters': getattr(model, 'get_params', lambda: {})(),
        'bias_report': bias_report,
        'fairness_metrics': fairness_metrics
    }
    audit_criteria = {'bias_threshold': 0.3, 'fairness_threshold': 0.7}

    # Create custom filename and output path for the report
    import os
    safe_model_name = model_name.replace(' ', '_').replace('(', '').replace(')', '')
    safe_config_name = config_name.replace(' ', '_')
    reports_folder = "example_reports"
    new_filename = f"{safe_model_name}_{safe_config_name}_compliance_report.pdf"
    output_path = os.path.join(reports_folder, new_filename)

    # Generate report directly to the desired location
    report_path = validator.generate_compliance_report(metadata, audit_criteria, output_path=output_path)
    print(f"Individual report saved to: {report_path}")
    
    return {
        'model_name': model_name,
        'config_name': config_name,
        'bias_report': bias_report,
        'fairness_metrics': fairness_metrics,
        'predictions': predictions,
        'report_path': report_path
    }


def get_model_configurations():
    """
    Define multiple hyperparameter configurations for each model type.
    
    Returns:
        dict: Dictionary containing model configurations
    """
    return {
        'random_forest': {
            'default': {'n_estimators': 100, 'random_state': 42},
            'conservative': {'n_estimators': 50, 'max_depth': 5, 'min_samples_split': 10, 'random_state': 42},
            'aggressive': {'n_estimators': 200, 'max_depth': 15, 'min_samples_split': 2, 'random_state': 42},
            'balanced': {'n_estimators': 150, 'max_depth': 10, 'min_samples_split': 5, 'random_state': 42}
        },
        'logistic_regression': {
            'default': {'random_state': 42, 'max_iter': 1000},
            'conservative': {'C': 0.1, 'penalty': 'l2', 'random_state': 42, 'max_iter': 1000},
            'aggressive': {'C': 10.0, 'penalty': 'l1', 'solver': 'liblinear', 'random_state': 42, 'max_iter': 1000},
            'balanced': {'C': 1.0, 'penalty': 'l2', 'random_state': 42, 'max_iter': 1000}
        },
        'svm': {
            'default': {'random_state': 42, 'probability': True},
            'conservative': {'C': 0.1, 'kernel': 'rbf', 'gamma': 'scale', 'random_state': 42, 'probability': True},
            'aggressive': {'C': 10.0, 'kernel': 'poly', 'degree': 3, 'random_state': 42, 'probability': True},
            'balanced': {'C': 1.0, 'kernel': 'rbf', 'gamma': 'auto', 'random_state': 42, 'probability': True}
        },
        'gradient_boosting': {
            'default': {'n_estimators': 100, 'random_state': 42},
            'conservative': {'n_estimators': 50, 'learning_rate': 0.05, 'max_depth': 3, 'random_state': 42},
            'aggressive': {'n_estimators': 200, 'learning_rate': 0.2, 'max_depth': 8, 'random_state': 42},
            'balanced': {'n_estimators': 150, 'learning_rate': 0.1, 'max_depth': 5, 'random_state': 42}
        },
        'decision_tree': {
            'default': {'random_state': 42, 'max_depth': 10},
            'conservative': {'max_depth': 3, 'min_samples_split': 20, 'min_samples_leaf': 10, 'random_state': 42},
            'aggressive': {'max_depth': 15, 'min_samples_split': 2, 'min_samples_leaf': 1, 'random_state': 42},
            'balanced': {'max_depth': 8, 'min_samples_split': 5, 'min_samples_leaf': 2, 'random_state': 42}
        },
        'neural_network': {
            'default': {'hidden_layer_sizes': (100, 50), 'random_state': 42, 'max_iter': 500},
            'conservative': {'hidden_layer_sizes': (50, 25), 'alpha': 0.1, 'random_state': 42, 'max_iter': 300},
            'aggressive': {'hidden_layer_sizes': (200, 100, 50), 'alpha': 0.001, 'random_state': 42, 'max_iter': 1000},
            'balanced': {'hidden_layer_sizes': (100, 50), 'alpha': 0.01, 'random_state': 42, 'max_iter': 500}
        },
        'xgboost': {
            'default': {'n_estimators': 100, 'random_state': 42},
            'conservative': {'n_estimators': 50, 'learning_rate': 0.05, 'max_depth': 3, 'random_state': 42},
            'aggressive': {'n_estimators': 200, 'learning_rate': 0.2, 'max_depth': 8, 'random_state': 42},
            'balanced': {'n_estimators': 150, 'learning_rate': 0.1, 'max_depth': 5, 'random_state': 42}
        }
    }


def main():
    """
    Run a comprehensive example of ethical AI validation with multiple ML models
    and hyperparameter configurations.
    
    This function demonstrates the complete workflow for auditing multiple AI models
    with different hyperparameter settings for bias, fairness, and compliance. 
    It includes data preparation, model training for different algorithms and 
    configurations, bias detection, fairness assessment, compliance reporting, 
    real-time monitoring, and mitigation suggestions.
    
    The example uses synthetic data to simulate a real-world scenario where
    an organization needs to ensure their AI models are fair and compliant
    across different demographic groups and parameter settings.
    
    Author: WHIS (muhammadabdullahinbox@gmail.com)
    """
    
    print("Ethical AI Validator - Multi-Model Multi-Config Usage Example")
    print("=" * 70)
    
    # Step 1: Create sample data
    print("\n1. Creating sample dataset...")
    X, y = make_classification(
        n_samples=2000,
        n_features=15,
        n_informative=8,
        n_redundant=4,
        random_state=42
    )
    
    # Convert to DataFrame for better handling
    X_df = pd.DataFrame(X)
    y_series = pd.Series(y)
    
    # Create synthetic sensitive features with some bias
    np.random.seed(42)
    sensitive_features = pd.DataFrame({
        'gender': np.random.choice(['male', 'female'], size=2000),
        'age_group': np.random.choice(['18-25', '26-35', '36-50', '50+'], size=2000),
        'education': np.random.choice(['high_school', 'bachelor', 'master', 'phd'], size=2000)
    })
    
    # Introduce extreme bias in the target variable based on sensitive features
    # This will create highly unfair predictions that the validator can detect
    y_bias = y.copy()
    
    # Add extreme bias based on gender (females get much higher positive rates)
    female_mask = (sensitive_features['gender'].to_numpy() == 'female')
    y_bias[female_mask] = np.random.choice([0, 1], size=int(female_mask.sum()), p=[0.05, 0.95])  # 95% positive for females

    # Add extreme bias based on age (younger people get much higher positive rates)
    young_mask = sensitive_features['age_group'].isin(['18-25', '26-35']).to_numpy()
    y_bias[young_mask] = np.random.choice([0, 1], size=int(young_mask.sum()), p=[0.02, 0.98])  # 98% positive for young

    # Add extreme bias based on education (higher education gets much higher positive rates)
    high_edu_mask = sensitive_features['education'].isin(['master', 'phd']).to_numpy()
    y_bias[high_edu_mask] = np.random.choice([0, 1], size=int(high_edu_mask.sum()), p=[0.01, 0.99])  # 99% positive for high education

    # Add extreme bias for older people (much lower positive rates)
    older_mask = sensitive_features['age_group'].isin(['36-50', '50+']).to_numpy()
    y_bias[older_mask] = np.random.choice([0, 1], size=int(older_mask.sum()), p=[0.95, 0.05])  # 95% negative for older

    # Add extreme bias for lower education (much lower positive rates)
    low_edu_mask = sensitive_features['education'].isin(['high_school', 'bachelor']).to_numpy()
    y_bias[low_edu_mask] = np.random.choice([0, 1], size=int(low_edu_mask.sum()), p=[0.90, 0.10])  # 90% negative for low education

    # Add extreme bias for males (much lower positive rates)
    male_mask = (sensitive_features['gender'].to_numpy() == 'male')
    y_bias[male_mask] = np.random.choice([0, 1], size=int(male_mask.sum()), p=[0.85, 0.15])  # 85% negative for males
    
    y_series = pd.Series(y_bias)
    
    print(f"Dataset created: {X_df.shape[0]} samples, {X_df.shape[1]} features")
    print(f"Sensitive features: {list(sensitive_features.columns)}")
    
    # Step 2: Split data and prepare for different models
    print("\n2. Preparing data for multiple models...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y_series, test_size=0.2, random_state=42
    )
    
    # Scale data for models that benefit from it
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert scaled arrays back to DataFrames to maintain indexing
    X_train_scaled_df = pd.DataFrame(X_train_scaled, index=X_train.index, columns=X_train.columns)  # type: ignore
    X_test_scaled_df = pd.DataFrame(X_test_scaled, index=X_test.index, columns=X_test.columns)  # type: ignore
    
    print("Data prepared for training")
    
    # Step 3: Initialize Ethical AI Validator and create reports folder
    print("\n3. Initializing Ethical AI Validator...")
    validator = EthicalAIValidator()
    print("Validator initialized")
    
    # Create example_reports folder
    import os
    reports_folder = "example_reports"
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)
        print(f"Created reports folder: {reports_folder}")
    else:
        print(f"Using existing reports folder: {reports_folder}")
    
    # Step 4: Get model configurations
    configs = get_model_configurations()
    
    # Step 5: Train and evaluate multiple models with different configurations
    print("\n4. Training and evaluating multiple ML models with different configurations...")
    
    all_results = []
    
    # Random Forest Configurations
    print("\n" + "="*50)
    print("RANDOM FOREST CONFIGURATIONS")
    print("="*50)
    
    for config_name, params in configs['random_forest'].items():
        rf_model = RandomForestClassifier(**params)
        rf_model.fit(X_train, y_train)
        rf_results = run_single_model_scenario(
            "Random Forest", rf_model, X_train, X_test, y_train, y_test,
            sensitive_features, validator, f"RF-{config_name}", config_name
        )
        all_results.append(rf_results)
    
    # Logistic Regression Configurations
    print("\n" + "="*50)
    print("LOGISTIC REGRESSION CONFIGURATIONS")
    print("="*50)
    
    for config_name, params in configs['logistic_regression'].items():
        lr_model = LogisticRegression(**params)
        lr_model.fit(X_train_scaled_df, y_train)
        lr_results = run_single_model_scenario(
            "Logistic Regression", lr_model, X_train_scaled_df, X_test_scaled_df, y_train, y_test,
            sensitive_features, validator, f"LR-{config_name}", config_name
        )
        all_results.append(lr_results)
    
    # Support Vector Machine Configurations
    print("\n" + "="*50)
    print("SUPPORT VECTOR MACHINE CONFIGURATIONS")
    print("="*50)
    
    for config_name, params in configs['svm'].items():
        svm_model = SVC(**params)
        svm_model.fit(X_train_scaled_df, y_train)
        svm_results = run_single_model_scenario(
            "Support Vector Machine", svm_model, X_train_scaled_df, X_test_scaled_df, y_train, y_test,
            sensitive_features, validator, f"SVM-{config_name}", config_name
        )
        all_results.append(svm_results)
    
    # Gradient Boosting Configurations
    print("\n" + "="*50)
    print("GRADIENT BOOSTING CONFIGURATIONS")
    print("="*50)
    
    for config_name, params in configs['gradient_boosting'].items():
        gb_model = GradientBoostingClassifier(**params)
        gb_model.fit(X_train, y_train)
        gb_results = run_single_model_scenario(
            "Gradient Boosting", gb_model, X_train, X_test, y_train, y_test,
            sensitive_features, validator, f"GB-{config_name}", config_name
        )
        all_results.append(gb_results)
    
    # Decision Tree Configurations
    print("\n" + "="*50)
    print("DECISION TREE CONFIGURATIONS")
    print("="*50)
    
    for config_name, params in configs['decision_tree'].items():
        dt_model = DecisionTreeClassifier(**params)
        dt_model.fit(X_train, y_train)
        dt_results = run_single_model_scenario(
            "Decision Tree", dt_model, X_train, X_test, y_train, y_test,
            sensitive_features, validator, f"DT-{config_name}", config_name
        )
        all_results.append(dt_results)
    
    # Neural Network Configurations
    print("\n" + "="*50)
    print("NEURAL NETWORK CONFIGURATIONS")
    print("="*50)
    
    for config_name, params in configs['neural_network'].items():
        nn_model = MLPClassifier(**params)
        nn_model.fit(X_train_scaled_df, y_train)
        nn_results = run_single_model_scenario(
            "Neural Network (MLP)", nn_model, X_train_scaled_df, X_test_scaled_df, y_train, y_test,
            sensitive_features, validator, f"NN-{config_name}", config_name
        )
        all_results.append(nn_results)
    
    # XGBoost Configurations (if available)
    if _HAS_XGB:
        print("\n" + "="*50)
        print("XGBOOST CONFIGURATIONS")
        print("="*50)
        for config_name, params in configs['xgboost'].items():
            xgb_model = xgb.XGBClassifier(**params)
            xgb_model.fit(X_train, y_train)
            xgb_results = run_single_model_scenario(
                "XGBoost", xgb_model, X_train, X_test, y_train, y_test,
                sensitive_features, validator, f"XGB-{config_name}", config_name
            )
            all_results.append(xgb_results)
    else:
        print("XGBoost not available - skipping XGBoost configurations")
    
    # Step 6: Comprehensive Comparative Analysis
    print("\n5. Comprehensive Comparative Analysis:")
    print("=" * 70)
    
    print("Model Configuration Comparison Summary:")
    print(f"{'Model':<15} {'Config':<12} {'Gender':<8} {'Age':<8} {'Education':<10}")
    print("-" * 70)
    
    for result in all_results:
        model_name = result['model_name'][:14]  # Truncate for display
        config_name = result['config_name'][:11]  # Truncate for display
        fairness_scores = result['fairness_metrics']['fairness_scores']
        
        gender_fairness = fairness_scores.get('gender', {}).get('fairness_score', 0.0)
        age_fairness = fairness_scores.get('age_group', {}).get('fairness_score', 0.0)
        education_fairness = fairness_scores.get('education', {}).get('fairness_score', 0.0)
        
        print(f"{model_name:<15} {config_name:<12} {gender_fairness:<8.3f} {age_fairness:<8.3f} {education_fairness:<10.3f}")
    
    # Step 7: Find best configurations per model type
    print("\n6. Best Configuration Analysis:")
    print("=" * 50)
    
    model_types = {}
    for result in all_results:
        model_name = result['model_name']
        config_name = result['config_name']
        fairness_scores = result['fairness_metrics']['fairness_scores']
        
        # Calculate average fairness score
        avg_fairness = np.mean([
            fairness_scores.get('gender', {}).get('fairness_score', 0.0),
            fairness_scores.get('age_group', {}).get('fairness_score', 0.0),
            fairness_scores.get('education', {}).get('fairness_score', 0.0)
        ])
        
        if model_name not in model_types:
            model_types[model_name] = []
        
        model_types[model_name].append({
            'config': config_name,
            'avg_fairness': avg_fairness,
            'gender': fairness_scores.get('gender', {}).get('fairness_score', 0.0),
            'age': fairness_scores.get('age_group', {}).get('fairness_score', 0.0),
            'education': fairness_scores.get('education', {}).get('fairness_score', 0.0)
        })
    
    print("Best Configuration per Model Type:")
    for model_name, configs in model_types.items():
        best_config = max(configs, key=lambda x: x['avg_fairness'])
        print(f"\n{model_name}:")
        print(f"  Best Config: {best_config['config']}")
        print(f"  Avg Fairness: {best_config['avg_fairness']:.3f}")
        print(f"  Gender: {best_config['gender']:.3f}, Age: {best_config['age']:.3f}, Education: {best_config['education']:.3f}")
    
    # Step 7: Generate comprehensive recommendations
    print("\n7. Comprehensive Recommendations:")
    print("-" * 50)
    
    # Combine all bias reports for comprehensive analysis
    all_bias_reports = []
    for result in all_results:
        if not result['bias_report'].empty:
            all_bias_reports.append(result['bias_report'])
    
    if all_bias_reports:
        combined_bias_report = pd.concat(all_bias_reports, ignore_index=True)
        mitigations = validator.suggest_mitigations(combined_bias_report)
        
        print("Cross-Model Cross-Config Mitigation Suggestions:")
    for i, suggestion in enumerate(mitigations['suggestions'], 1):
        print(f"{i}. {suggestion}")
    
    print(f"\nMulti-Model Multi-Config Example completed successfully!")
    print(f"Total configurations evaluated: {len(all_results)}")
    print("Individual compliance reports generated for each model configuration.")
    print("=" * 70)


if __name__ == "__main__":
    main() 