# quick_sentiments/__init__.py
from .pipeline import run_pipeline       # Expose pipeline function
from .predict import make_predictions # Expose prediction function
from .preprocess import pre_process
from .preprocess import pre_process_spacy  # Expose preprocessing function

__all__ = ['run_pipeline', 'make_predictions', 'pre_process', 'pre_process_spacy']  # Controls what's available in *

