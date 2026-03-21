"""
Data loading and validation module.

Supports multiple data sources:
- SMS Spam Collection Dataset (UCI)
- CSV files with text/label columns
- Direct text input for inference
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Union, List

from sklearn.model_selection import train_test_split

from ..config.settings import DATA_DIR, LABEL_MAP
from ..utils.logging import get_logger

logger = get_logger(__name__)


class DataLoader:
    """
    Handles loading and validation of spam/ham datasets.

    Attributes:
        data_path: Path to the dataset file
        text_column: Name of the column containing text messages
        label_column: Name of the column containing labels
    """

    def __init__(
        self,
        data_path: Optional[Union[str, Path]] = None,
        text_column: str = "text",
        label_column: str = "label",
    ):
        """
        Initialize the DataLoader.

        Args:
            data_path: Path to dataset file (CSV, TSV, or TXT)
            text_column: Column name for text messages
            label_column: Column name for labels
        """
        self.data_path = Path(data_path) if data_path else None
        self.text_column = text_column
        self.label_column = label_column
        self._data: Optional[pd.DataFrame] = None

    def load_sms_spam_collection(
        self,
        url: str = None,
        sep: str = ",",
    ) -> pd.DataFrame:
        """
        Load the SMS Spam Collection Dataset.

        The dataset contains SMS messages labeled as 'ham' or 'spam'.

        Args:
            url: URL or local path to the dataset
            sep: Separator character (default: tab)

        Returns:
            DataFrame with 'text' and 'label' columns
        """
        logger.info(f"Loading SMS Spam Collection from: {url}")

        try:
            if url and url.startswith("http"):
                self._data = pd.read_csv(url, sep=sep, header=None, names=["label", "text"])
            elif url:
                self._data = pd.read_csv(url, sep=sep)
            else:
                return self._load_local_fallback()

            self._data["label"] = self._data["label"].str.lower().str.strip()

            logger.info(f"Loaded {len(self._data)} samples")
            logger.info(f"Label distribution:\n{self._data['label'].value_counts()}")

            return self._data

        except Exception as e:
            logger.error(f"Failed to load from URL: {e}")
            return self._load_local_fallback()

    def _load_local_fallback(self) -> pd.DataFrame:
        """Load dataset from local data directory as fallback."""
        local_paths = [
            DATA_DIR / "sms_spam.csv",
            DATA_DIR / "sms_spam.tsv",
            DATA_DIR / "SMSSpamCollection",
        ]

        for path in local_paths:
            if path.exists():
                logger.info(f"Loading from local file: {path}")
                if path.suffix == ".tsv" or "SMSSpamCollection" in path.name:
                    self._data = pd.read_csv(path, sep="\t", names=["label", "text"])
                else:
                    # CSV file with header
                    self._data = pd.read_csv(path, engine="python")
                self._data["label"] = self._data["label"].str.lower().str.strip()
                return self._data

        raise FileNotFoundError(
            "No local dataset found. Please download SMS Spam Collection to data/ folder."
        )

    def load_csv(
        self,
        file_path: Union[str, Path],
        text_column: str = "text",
        label_column: str = "label",
    ) -> pd.DataFrame:
        """
        Load a custom CSV dataset.

        Args:
            file_path: Path to CSV file
            text_column: Column name for text messages
            label_column: Column name for labels

        Returns:
            DataFrame with text and label columns
        """
        file_path = Path(file_path)
        logger.info(f"Loading custom CSV from: {file_path}")

        self._data = pd.read_csv(file_path)

        if text_column not in self._data.columns:
            raise ValueError(f"Text column '{text_column}' not found in CSV")
        if label_column not in self._data.columns:
            raise ValueError(f"Label column '{label_column}' not found in CSV")

        self._data = self._data.rename(
            columns={text_column: "text", label_column: "label"}
        )
        self._data["label"] = self._data["label"].str.lower().str.strip()
        self.text_column = "text"
        self.label_column = "label"

        logger.info(f"Loaded {len(self._data)} samples")
        return self._data

    def validate_data(self, data: Optional[pd.DataFrame] = None) -> bool:
        """
        Validate the dataset for training readiness.

        Checks:
        - No null values in text or label
        - Labels are binary (ham/spam)
        - No duplicate messages

        Args:
            data: DataFrame to validate (uses internal _data if None)

        Returns:
            True if validation passes

        Raises:
            ValueError: If validation fails
        """
        df = data if data is not None else self._data

        if df is None:
            raise ValueError("No data loaded for validation")

        null_text = df["text"].isnull().sum()
        null_label = df["label"].isnull().sum()
        if null_text > 0 or null_label > 0:
            raise ValueError(f"Null values found: text={null_text}, label={null_label}")

        unique_labels = set(df["label"].unique())
        valid_labels = {"ham", "spam"}
        if not unique_labels.issubset(valid_labels):
            invalid = unique_labels - valid_labels
            raise ValueError(f"Invalid labels found: {invalid}")

        duplicates = df.duplicated(subset=["text"]).sum()
        if duplicates > 0:
            logger.warning(f"Found {duplicates} duplicate messages")

        logger.info("Data validation passed")
        return True

    def get_train_test_split(
        self,
        data: Optional[pd.DataFrame] = None,
        test_size: float = 0.2,
        random_state: int = 42,
        stratify: bool = True,
    ) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        Split data into training and testing sets.

        Args:
            data: DataFrame to split
            test_size: Fraction of data for testing
            random_state: Random seed for reproducibility
            stratify: Whether to stratify by label

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        df = data if data is not None else self._data

        if df is None:
            raise ValueError("No data loaded for splitting")

        X = df["text"]
        y = df["label"].map(LABEL_MAP)

        stratify_param = y if stratify else None

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=stratify_param
        )

        logger.info(f"Train/test split: {len(X_train)} train, {len(X_test)} test")

        return X_train, X_test, y_train, y_test

    def load_messages_for_inference(self, messages: Union[str, List[str]]) -> pd.Series:
        """
        Load messages for inference.

        Args:
            messages: Single message string or list of messages

        Returns:
            pandas Series of messages
        """
        if isinstance(messages, str):
            messages = [messages]

        logger.info(f"Loaded {len(messages)} message(s) for inference")
        return pd.Series(messages, name="text")


def load_dataset(
    source: Union[str, Path] = "sms_spam_collection",
    **kwargs,
) -> pd.DataFrame:
    """
    Convenience function to load a dataset.

    Args:
        source: Dataset source ('sms_spam_collection' or file path)
        **kwargs: Additional arguments passed to DataLoader

    Returns:
        DataFrame with text and label columns
    """
    loader = DataLoader(**kwargs)

    if source == "sms_spam_collection":
        return loader.load_sms_spam_collection()
    else:
        return loader.load_csv(source)
