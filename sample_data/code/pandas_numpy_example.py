#!/usr/bin/env python3
"""Data Science with Pandas and NumPy"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# Create sample dataset
def create_sales_data():
    """Create sample sales dataset."""
    np.random.seed(42)
    
    dates = pd.date_range(start='2024-01-01', periods=365, freq='D')
    products = ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard']
    
    data = {
        'date': np.random.choice(dates, 1000),
        'product': np.random.choice(products, 1000),
        'quantity': np.random.randint(1, 10, 1000),
        'price': np.random.uniform(50, 2000, 1000).round(2),
    }
    
    df = pd.DataFrame(data)
    df['total'] = df['quantity'] * df['price']
    return df


# Data Analysis Functions
def analyze_sales(df):
    """Perform comprehensive sales analysis."""
    analysis = {}
    
    # Total revenue
    analysis['total_revenue'] = df['total'].sum()
    
    # Average order value
    analysis['avg_order_value'] = df['total'].mean()
    
    # Sales by product
    analysis['by_product'] = df.groupby('product')['total'].agg(['sum', 'mean', 'count'])
    
    # Monthly trends
    df['month'] = df['date'].dt.to_period('M')
    analysis['monthly'] = df.groupby('month')['total'].sum()
    
    # Top 10 transactions
    analysis['top_10'] = df.nlargest(10, 'total')[['date', 'product', 'total']]
    
    return analysis


# Machine Learning Preparation
def prepare_ml_data(df):
    """Prepare data for machine learning."""
    # Feature engineering
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Encode categorical variables
    df_encoded = pd.get_dummies(df, columns=['product'], prefix='product')
    
    # Split features and target
    X = df_encoded.drop(['date', 'total'], axis=1)
    y = df_encoded['total']
    
    return X, y


# Data Cleaning
def clean_data(df):
    """Clean and validate data."""
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.fillna(df.mean(numeric_only=True))
    
    # Remove outliers (IQR method)
    Q1 = df['total'].quantile(0.25)
    Q3 = df['total'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[(df['total'] >= Q1 - 1.5 * IQR) & (df['total'] <= Q3 + 1.5 * IQR)]
    
    return df


# Visualization Helper
def create_visualizations(df):
    """Create visualization data structures."""
    viz_data = {
        'revenue_by_product': df.groupby('product')['total'].sum().to_dict(),
        'daily_sales': df.groupby('date')['total'].sum().reset_index().to_dict('records'),
        'quantity_distribution': df['quantity'].value_counts().sort_index().to_dict(),
    }
    return viz_data


if __name__ == "__main__":
    # Generate and analyze data
    df = create_sales_data()
    df = clean_data(df)
    analysis = analyze_sales(df)
    
    print("=" * 60)
    print("Sales Analysis Report")
    print("=" * 60)
    print(f"\nTotal Revenue: ${analysis['total_revenue']:,.2f}")
    print(f"Average Order Value: ${analysis['avg_order_value']:,.2f}")
    print(f"\nSales by Product:")
    print(analysis['by_product'])
    print(f"\nTop 10 Transactions:")
    print(analysis['top_10'].to_string(index=False))
