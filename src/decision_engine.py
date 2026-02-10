
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class WinRateDriverEngine:
    def __init__(self):
        self.model = None
        self.preprocessor = None

    def prepare_data(self, df):
        """
        Cleans data matching your CSV screenshot.
        """
        # 1. Standardize 'outcome' to handle 'Won'/'won'/'WON'
        df['outcome_clean'] = df['outcome'].astype(str).str.strip().str.lower()
        
        # 2. Filter for Closed Deals only
        data = df[df['outcome_clean'].isin(['won', 'lost'])].copy()
        
        # 3. Create Target (1 = Won, 0 = Lost)
        data['target'] = (data['outcome_clean'] == 'won').astype(int)
        
        # 4. Handle Missing Values in Numeric Columns
        # Use existing 'sales_cycle_days' from your CSV
        if 'sales_cycle_days' in data.columns:
            data['sales_cycle_days'] = data['sales_cycle_days'].fillna(data['sales_cycle_days'].median())
        else:
             # Fallback if column is missing (though your screenshot shows it exists)
             data['sales_cycle_days'] = (pd.to_datetime(data['closed_date']) - pd.to_datetime(data['created_date'])).dt.days

        data['deal_amount'] = data['deal_amount'].fillna(data['deal_amount'].median())

        # 5. Select Features (Based on your Screenshot)
        # Note: We exclude 'deal_id', 'rep_id', dates, and 'outcome'
        feature_cols = ['deal_amount', 'industry', 'region', 'product_type', 'lead_source', 'sales_cycle_days']
        
        # Fill categorical text nulls with "Unknown"
        cat_cols = ['industry', 'region', 'product_type', 'lead_source']
        for col in cat_cols:
            data[col] = data[col].fillna('Unknown')
            
        return data[feature_cols], data['target']

    def train(self, X, y):
        """
        Trains the Decision Tree.
        """
        cat_features = ['industry', 'region', 'product_type', 'lead_source']
        num_features = ['deal_amount', 'sales_cycle_days']

        # Preprocessing Pipeline
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', 'passthrough', num_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
            ])

        # Model Pipeline
        self.model = Pipeline(steps=[
            ('preprocessor', self.preprocessor),
            ('classifier', DecisionTreeClassifier(max_depth=3, random_state=42))
        ])

        self.model.fit(X, y)
        print(f"✅ Model Trained on {len(X)} deals.")

    def get_key_drivers(self):
        """
        Returns top 5 drivers of Win/Loss.
        """
        # Get feature names from the pipeline
        ohe = self.model.named_steps['preprocessor'].named_transformers_['cat']
        cat_names = ohe.get_feature_names_out(['industry', 'region', 'product_type', 'lead_source'])
        all_names = ['deal_amount', 'sales_cycle_days'] + list(cat_names)
        
        # Get Importance
        importances = self.model.named_steps['classifier'].feature_importances_
        
        drivers = pd.DataFrame({
            'Driver': all_names,
            'Impact': importances
        }).sort_values(by='Impact', ascending=False)
        
        return drivers.head(5)