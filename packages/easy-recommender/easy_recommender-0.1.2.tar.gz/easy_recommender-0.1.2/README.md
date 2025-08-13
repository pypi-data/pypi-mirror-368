# Easy Recommender

⚠️ **This package is currently broken and under repair. Please do not use.** ⚠️

**This project only works with Python 3.11.11 because LightFM requires this specific version. Other versions are not supported.**

A simple and efficient recommendation system library using implicit collaborative filtering and LightFM.

## Features

- Simple API for building recommendation systems
- Support for both implicit and explicit feedback
- Built on top of proven libraries (implicit, LightFM)
- Easy data preprocessing utilities

## Installation

```bash
pip install easy-recommender
```

## Quick Start

```python
from easy_recommender import recommend, process_df, build_feature_data
import pandas as pd

# Load your data
df = pd.read_csv('your_ratings.csv')

# Process the data
processed_df = process_df(df)

# Build features
user_features, item_features = build_feature_data(df)

# Get recommendations
recommendations = recommend(
    processed_df, 
    user_features, 
    item_features, 
    user_id=123, 
    num_recommendations=10
)

print(recommendations)
```

## Requirements

- Python >=3.12
- pandas >=2.0.0
- scikit-learn >=1.3.0
- numpy >=1.24.0
- implicit >=0.7.0
- lightfm >=1.17

## License

MIT License

## References

This implementation is based on the approach described in:
https://zenn.dev/genda_jp/articles/2c2a1b5d185741