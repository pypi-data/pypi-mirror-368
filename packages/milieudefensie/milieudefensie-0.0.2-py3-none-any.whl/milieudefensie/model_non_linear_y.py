# Standard libraries
import time

# Data handling
import numpy as np
import pandas as pd

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Progress tracking
from tqdm.auto import tqdm

# Scikit-learn components
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.inspection import permutation_importance

# Metrics
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
    classification_report
)

# Models
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    AdaBoostClassifier,
    HistGradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Specialized ensemble models
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# Model interpretation
import shap
pio.renderers.default = 'browser'


def generate_example_dataset(n_samples=1000, random_state=42):
    """
    Generate synthetic dataset for classification examples.
    
    Parameters:
    - n_samples: Number of samples to generate
    - random_state: Random seed for reproducibility
    
    Returns:
    - DataFrame with features and two target variables:
        - y_binary: Binary target (yes/no)
        - y_multiclass: Multiclass target with 5 categories
    """
    np.random.seed(random_state)
    
    # Generate core features with some underlying patterns
    X, y = make_classification(
        n_samples=n_samples,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        random_state=random_state
    )
    
    # Create binary target (yes/no)
    y_binary = np.where(y > 0, 'yes', 'no')
    
    # Create correlated multiclass target
    y_multiclass = np.select(
        [
            (y > 1.5),
            (y > 0.5),
            (y > -0.5),
            (y > -1.5),
            (y <= -1.5)
        ],
        [
            'Interested',
            'Maybe in the future',
            'not Interested',
            'Already have it',
            'Dont call me again'
        ],
        default='not Interested'  # Explicit default value with same dtype
    )
    
    # Create categorical features
    channels = [
        'Deurtotdeurwerving', 'Donatiemailing', 'Prospectmailing',
        'Straatwerving', 'Telemarketingreactivatie', 'Telemarketingupgrade',
        'Telemarketingwelkom', 'Website'
    ]
    first_inflow_channel = np.random.choice(channels, size=n_samples)
    
    gender = np.random.choice(['male', 'female', 'other'], 
                             size=n_samples, 
                             p=[0.45, 0.5, 0.05])
    
    # Create continuous features
    age = np.random.normal(loc=45, scale=15, size=n_samples).astype(int)
    age = np.clip(age, 18, 90)
    woz_waarde = np.random.uniform(2, 20, size=n_samples).round(1)
    
    # Create binary features
    optin_newsletter = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    member = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])
    major_donor_2024 = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
    middle_donor_2024 = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    
    # Build DataFrame
    data = {
        'optin_newsletter': optin_newsletter,
        'member': member,
        'major_donor_2024': major_donor_2024,
        'middle_donor_2024': middle_donor_2024,
        'gender_male': (gender == 'male').astype(int),
        'gender_female': (gender == 'female').astype(int),
        'gender_other': (gender == 'other').astype(int),
        'age': age,
        'woz_waarde': woz_waarde,
        'y_binary': y_binary,
        'y_multiclass': y_multiclass
    }
    
    # Add channel dummies
    for channel in channels:
        data[f'first_inflow_channel_{channel}'] = (first_inflow_channel == channel).astype(int)
    
    df = pd.DataFrame(data)
    
    # Add some correlation between targets
    df.loc[df['y_binary'] == 'yes', 'y_multiclass'] = np.random.choice(
        ['Interested', 'Maybe in the future', 'Already have it'],
        size=df['y_binary'].eq('yes').sum(),
        p=[0.6, 0.3, 0.1]
    )
    
    return df


class ClassificationAnalyzer:
    """
    A comprehensive class for comparing classification models, analyzing feature importance,
    and generating predictions.
    """
    
    def __init__(self, y, X, feature_names=None, random_state=42):
        """
        Initialize the analyzer with target and features.
        
        Parameters:
        - y: Target variable (binary, multiclass numeric, or text)
        - X: Feature matrix (DataFrame or array)
        - feature_names: List of feature names (optional)
        - random_state: Random seed for reproducibility
        """
        # Validate y shape
        y_array = np.array(y)
        if len(y_array.shape) > 1 and y_array.shape[1] != 1:
            raise ValueError("y should be a 1D array or column vector")
        
        self.y = y_array.ravel() if len(y_array.shape) > 1 else y_array
        self.X = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X, columns=feature_names)
        self.random_state = random_state
        self.feature_names = feature_names if feature_names else self.X.columns.tolist()
        self.label_encoder = None
        self.class_names = None
        self.results = None
        self.models = {}
        self.best_model = None
        
        
        # Encode target if text
        self._encode_target()
        
    def _encode_target(self):
        """Encode text targets to numeric if needed."""
        if pd.api.types.is_object_dtype(self.y) or pd.api.types.is_string_dtype(self.y):
            from sklearn.preprocessing import LabelEncoder
            self.label_encoder = LabelEncoder()
            self.y_encoded = self.label_encoder.fit_transform(self.y).ravel()
            self.class_names = self.label_encoder.classes_
        else:
            self.y_encoded = np.array(self.y).ravel()
            self.class_names = np.unique(self.y)
    
    def compare_models(self, test_train=True, test_size=0.25):
        """
        Compare multiple classification models with guaranteed metric availability.
        """
        # Validate data and initialize
        if not hasattr(self, 'models') or self.models is None:
            self.models = {}
        
        y_encoded = self.y_encoded.ravel()
        is_binary = len(self.class_names) == 2
        
        # Train-test split
        if test_train:
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, y_encoded,
                test_size=test_size,
                random_state=self.random_state,
                stratify=y_encoded if len(self.class_names) > 2 else None
            )
        else:
            X_train, X_test, y_train, y_test = self.X, self.X, y_encoded, y_encoded

        # Initialize models
        self.models = {
            "Gradient Boosting": GradientBoostingClassifier(
                learning_rate=0.01, max_depth=8, n_estimators=150,
                random_state=self.random_state
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=100, max_depth=10,
                random_state=self.random_state
            ),
            "XGBoost": XGBClassifier(
                learning_rate=0.01, max_depth=8, n_estimators=150,
                random_state=self.random_state, eval_metric='logloss'
            ),
            "Logistic Regression": LogisticRegression(
                max_iter=1000, random_state=self.random_state,
                multi_class='ovr' if is_binary else 'multinomial'
            ),
            "Hist Gradient Boosting": HistGradientBoostingClassifier(
                random_state=self.random_state
            ),
            "CatBoost": CatBoostClassifier(verbose=0, random_state=self.random_state)
        }

        # Evaluation metrics
        results = []
        for name, model in tqdm(self.models.items(), desc="Evaluating models"):
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                # Base metrics that always work
                metrics = {
                    'Model': name,
                    'Accuracy': accuracy_score(y_test, y_pred),
                    'Balanced_Accuracy': balanced_accuracy_score(y_test, y_pred)
                }

                # Add metrics that might fail
                try:
                    if is_binary:
                        metrics.update({
                            'Precision': precision_score(y_test, y_pred, zero_division=0),
                            'Recall': recall_score(y_test, y_pred, zero_division=0),
                            'F1': f1_score(y_test, y_pred, zero_division=0)
                        })
                        if hasattr(model, 'predict_proba'):
                            metrics['ROC_AUC'] = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
                    else:
                        metrics.update({
                            'F1_Macro': f1_score(y_test, y_pred, average='macro', zero_division=0)
                        })
                        if hasattr(model, 'predict_proba'):
                            metrics['ROC_AUC_OVR'] = roc_auc_score(
                                y_test, model.predict_proba(X_test),
                                multi_class='ovr'
                            )
                except Exception as metric_error:
                    print(f"Metrics failed for {name}: {str(metric_error)}")

                results.append(metrics)
                
            except Exception as e:
                print(f"Model {name} failed: {str(e)}")
                continue

        # Create results DataFrame with guaranteed columns
        guaranteed_columns = ['Model', 'Accuracy', 'Balanced_Accuracy']
        if is_binary:
            guaranteed_columns.extend(['Precision', 'Recall', 'F1'])
        else:
            guaranteed_columns.append('F1_Macro')
        
        # Ensure all columns exist
        self.results = pd.DataFrame(results)
        for col in guaranteed_columns:
            if col not in self.results.columns:
                self.results[col] = np.nan

        # Sort by best available metric
        sort_options = ['F1', 'Balanced_Accuracy', 'Accuracy'] if is_binary else ['F1_Macro', 'Balanced_Accuracy', 'Accuracy']
        for metric in sort_options:
            if metric in self.results.columns and not self.results[metric].isnull().all():
                self.results = self.results.sort_values(metric, ascending=False)
                break

        # Store best model
        self.best_model = self.models[self.results.iloc[0]['Model']] if not self.results.empty else None

        return {
            'results': self.results,
            'models': self.models,
            'best_model': self.best_model,
            'label_encoder': self.label_encoder,
            'class_names': self.class_names
        }
    
    def analyze_feature_importance(self, method='auto', n_features=10, plot=True):
        """
        Analyze feature importance using specified method.
        
        Parameters:
        - method: 'auto' (best available), 'permutation', 'shap', or 'native'
        - n_features: Number of top features to show
        - plot: Whether to display visualization
        
        Returns:
        - DataFrame with importance scores
        """
        if self.best_model is None:
            raise ValueError("No model trained yet. Run compare_models() first.")
        
        # Native importance
        if method in ['auto', 'native'] and hasattr(self.best_model, 'feature_importances_'):
            importance = self.best_model.feature_importances_
            imp_df = pd.DataFrame({
                'Feature': self.feature_names,
                'Importance': importance
            }).sort_values('Importance', ascending=False)
            
            if plot:
                self._plot_importance(imp_df.head(n_features), 
                                    "Native Feature Importance",
                                    "Importance Score")
            return imp_df
        
        # Permutation importance
        if method in ['auto', 'permutation']:
            result = permutation_importance(
                self.best_model, self.X, self.best_model.predict(self.X),
                n_repeats=10, random_state=self.random_state
            )
            
            imp_df = pd.DataFrame({
                'Feature': self.feature_names,
                'Importance': result.importances_mean,
                'Std': result.importances_std
            }).sort_values('Importance', ascending=False)
            
            if plot:
                self._plot_importance(imp_df.head(n_features), 
                                     "Permutation Importance",
                                     "Mean Accuracy Decrease ± Std Dev",
                                     xerr='Std')
            return imp_df
        
        # SHAP values
        if method in ['auto', 'shap']:
            try:
                explainer = shap.Explainer(self.best_model)
                shap_values = explainer(self.X)
                
                if plot:
                    plt.figure(figsize=(10, 6))
                    shap.plots.beeswarm(shap_values, max_display=n_features, show=False)
                    plt.title('SHAP Feature Importance')
                    plt.tight_layout()
                    plt.show()
                
                return pd.DataFrame({
                    'Feature': self.feature_names,
                    'Importance': np.abs(shap_values.values).mean(axis=0)
                }).sort_values('Importance', ascending=False)
                
            except Exception as e:
                print(f"SHAP analysis failed: {str(e)}")
                if method == 'shap':
                    raise
                return self.analyze_feature_importance(method='permutation')
        
        raise ValueError(f"Invalid method: {method}. Choose: 'auto', 'native', 'permutation', or 'shap'")
    
    def _plot_importance(self, data, title, xlabel, xerr=None):
        """Helper function to plot feature importance."""
        plt.figure(figsize=(10, 6))
        ax = data.plot.barh(x='Feature', y='Importance', xerr=xerr, color='skyblue')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel('Features')
        plt.tight_layout()
        plt.show()
    
    def generate_predictions(self, relation_ids=None, save_as_csv=False, 
                        csv_name='predictions.csv', include_features=False,
                        X_new=None):
        """
        Generate predictions with class probabilities.
        
        Parameters:
        - relation_ids: Optional DataFrame/series with IDs to include
        - save_as_csv: Whether to save to CSV
        - csv_name: Output filename
        - include_features: Whether to include input features in output
        - X_new: Optional new feature matrix to make predictions on (uses self.X if None)
        
        Returns:
        - DataFrame with predictions and probabilities
        """
        if self.best_model is None:
            raise ValueError("No model trained yet. Run compare_models() first.")
        
        # Use provided X_new or fall back to self.X
        X_to_predict = X_new if X_new is not None else self.X
        
        # Ensure we're working with numpy arrays (not pandas Series)
        if hasattr(X_to_predict, 'values'):
            X_to_predict = X_to_predict.values
        
        # Generate predictions - these methods should handle 2D X input correctly
        try:
            proba = self.best_model.predict_proba(X_to_predict)
            preds = self.best_model.predict(X_to_predict)
        except ValueError as e:
            if "Expected 2D array" in str(e):
                X_to_predict = np.array(X_to_predict).reshape(-1, len(self.feature_names))
                proba = self.best_model.predict_proba(X_to_predict)
                preds = self.best_model.predict(X_to_predict)
            else:
                raise
        
        # Get class names
        if self.label_encoder:
            pred_labels = self.label_encoder.inverse_transform(preds.ravel())  # Ensure 1D
            class_names = self.label_encoder.classes_
        else:
            pred_labels = preds.ravel()  # Ensure 1D
            class_names = self.best_model.classes_
        
        # Create output DataFrame
        proba_cols = [f'probability_{str(cls).lower().replace(" ", "_")}' for cls in class_names]
        output = pd.DataFrame({
            'predicted_class': pred_labels,
            **{col: proba[:, i] for i, col in enumerate(proba_cols)}
        })
        
        # Add relation IDs if provided
        if relation_ids is not None:
            relation_ids = np.array(relation_ids).ravel()  # Ensure 1D
            output.insert(0, 'relation_id', relation_ids)
        
        # Add features if requested
        if include_features:
            if isinstance(X_to_predict, np.ndarray):
                X_to_predict = pd.DataFrame(X_to_predict, columns=self.feature_names)
            output = pd.concat([output, X_to_predict.reset_index(drop=True)], axis=1)
        
        # Save if requested
        if save_as_csv:
            output.to_csv(csv_name, index=False)
            print(f"Predictions saved to {csv_name}")
        
        return output
    
    def analyze_probabilities(self, target_class=None, n_cases=5000, 
                        analysis_type='highest', show_all=False,
                        hover_columns=None, save_plot=True, 
                        plot_filename='probability_analysis.html',
                        X_data=None):
        """
        Analyze class probabilities with flexible selection options.
        
        Parameters:
        - target_class: The class to analyze (None for binary positive class)
        - n_cases: Number of cases to show
        - analysis_type: 'highest', 'lowest', or 'both'
        - show_all: If True, analyzes entire dataset
        - hover_columns: List of columns to show in hover data
        - save_plot: Whether to save the interactive plot
        - plot_filename: Name for saved plot file
        - X_data: Feature matrix to analyze (uses self.X if None)
        
        Returns:
        - DataFrame with probabilities and relation IDs
        - Displays interactive plot
        """
        if self.best_model is None:
            raise ValueError("No model trained yet. Run compare_models() first.")
        
        # Use provided X_data or fall back to self.X
        X_to_analyze = X_data if X_data is not None else self.X
        
        # 1. Generate probabilities and handle column names
        proba = self.best_model.predict_proba(X_to_analyze)
        
        # Determine class names
        if self.label_encoder:
            class_names = [str(cls).lower().replace(" ", "_") for cls in self.label_encoder.classes_]
            proba_df = pd.DataFrame(proba, columns=class_names)
            # Default to first class if not specified
            target_col = str(target_class).lower().replace(" ", "_") if target_class else class_names[0]
        else:
            # For binary classification
            if proba.shape[1] == 2:
                class_names = ['class_0', 'class_1']
                proba_df = pd.DataFrame(proba, columns=class_names)
                target_col = target_class if target_class in class_names else 'class_1'
            else:
                # For multiclass numeric targets
                class_names = [f'class_{i}' for i in range(proba.shape[1])]
                proba_df = pd.DataFrame(proba, columns=class_names)
                target_col = target_class if target_class in class_names else class_names[0]
        
        # 2. Create selection DataFrame
        df_selectie = X_to_analyze.copy()
        for col in proba_df.columns:
            df_selectie[f'probability_{col}'] = proba_df[col]
        
        # 3. Prepare data for visualization
        prob_col = f'probability_{target_col}'
        
        if show_all:
            plot_df = df_selectie
            title_part = "Complete Distribution of"
        else:
            if analysis_type == 'highest':
                plot_df = df_selectie.nlargest(n_cases, prob_col)
                title_part = f"Top {n_cases} Highest"
            elif analysis_type == 'lowest':
                plot_df = df_selectie.nsmallest(n_cases, prob_col)
                title_part = f"Top {n_cases} Lowest"
            elif analysis_type == 'both':
                high_df = df_selectie.nlargest(n_cases, prob_col)
                low_df = df_selectie.nsmallest(n_cases, prob_col)
                plot_df = pd.concat([high_df, low_df])
                title_part = f"Top {n_cases} Highest & Lowest"
            else:
                raise ValueError("analysis_type must be 'highest', 'lowest', or 'both'")
        
        # 4. Create interactive plot
        try:
            import plotly.express as px
            
            fig = px.histogram(
                plot_df,
                x=prob_col,
                title=f"{title_part} '{target_col.replace('_', ' ').title()}' Probabilities",
                marginal="rug",
                hover_data=hover_columns,
                nbins=20,
                color_discrete_sequence=['#636EFA']
            )
            
            fig.update_layout(
                xaxis_title=f"Probability of '{target_col.replace('_', ' ').title()}'",
                yaxis_title="Count",
                hovermode="x unified"
            )
            
            fig.show()
            
            if save_plot:
                fig.write_html(plot_filename)
            
        except ImportError:
            print("Plotly not installed. Install with: pip install plotly")
        
        return df_selectie
