"""
Easy Recommender - A simple recommendation system using implicit library
"""

__version__ = "0.1.1"

from .recommender import recommend, process_df, build_feature_data

__all__ = ["recommend", "process_df", "build_feature_data"]
