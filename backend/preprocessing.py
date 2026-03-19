"""
Text preprocessing module for spam detection.

Provides reusable text cleaning and normalization functions
for both training and inference pipelines.
"""

import re
import string
from typing import List, Optional, Callable
from functools import lru_cache

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

from .utils import setup_logger

logger = setup_logger(__name__)

# =============================================================================
# NLTK Data Download (one-time setup)
# =============================================================================


def _download_nltk_data():
    """Download required NLTK data packages."""
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("stemmer/porter", "porter"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw"),
    ]

    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(name, quiet=True)
            except Exception:
                pass  # Silently continue if download fails


_download_nltk_data()

# =============================================================================
# Preprocessing Components
# =============================================================================


class TextPreprocessor:
    """
    Reusable text preprocessor for spam detection.

    Applies a pipeline of transformations:
    1. Lowercase conversion
    2. URL removal
    3. Punctuation removal
    4. Stopword removal
    5. Tokenization
    6. Stemming/Lemmatization (optional)

    Attributes:
        remove_stopwords: Whether to remove stopwords
        use_stemming: Whether to apply stemming
        use_lemmatization: Whether to apply lemmatization
        min_length: Minimum word length to keep
    """

    def __init__(
        self,
        remove_stopwords: bool = True,
        use_stemming: bool = False,
        use_lemmatization: bool = False,
        min_length: int = 2,
        custom_stopwords: Optional[List[str]] = None,
    ):
        """
        Initialize the text preprocessor.

        Args:
            remove_stopwords: Remove common English stopwords
            use_stemming: Apply Porter stemming
            use_lemmatization: Apply WordNet lemmatization
            min_length: Minimum character length for tokens
            custom_stopwords: Additional stopwords to remove
        """
        self.remove_stopwords = remove_stopwords
        self.use_stemming = use_stemming
        self.use_lemmatization = use_lemmatization
        self.min_length = min_length

        # Load stopwords
        try:
            self.stopwords_set = set(stopwords.words("english"))
        except Exception:
            self.stopwords_set = set()
            logger.warning("NLTK stopwords not available")

        if custom_stopwords:
            self.stopwords_set.update(custom_stopwords)

        # Initialize stemmer and lemmatizer
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        # Compile regex patterns
        self.url_pattern = re.compile(
            r"http\S+|www\.\S+|https?\S+|bit\.ly\S+|t\.co\S+", re.IGNORECASE
        )
        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )
        self.phone_pattern = re.compile(
            r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
        )
        self.money_pattern = re.compile(r"£\d+|\$\d+|\d+\.(?:\d{2})\b")

        logger.info(
            f"Preprocessor initialized: stopwords={remove_stopwords}, "
            f"stemming={use_stemming}, lemmatization={use_lemmatization}"
        )

    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        return self.url_pattern.sub(" ", text)

    def _remove_emails(self, text: str) -> str:
        """Remove email addresses from text."""
        return self.email_pattern.sub(" ", text)

    def _remove_phone_numbers(self, text: str) -> str:
        """Remove phone numbers from text."""
        return self.phone_pattern.sub(" ", text)

    def _remove_money(self, text: str) -> str:
        """Remove monetary values from text."""
        return self.money_pattern.sub(" ", text)

    def _to_lowercase(self, text: str) -> str:
        """Convert text to lowercase."""
        return text.lower()

    def _remove_punctuation(self, text: str) -> str:
        """Remove punctuation marks."""
        return text.translate(str.maketrans("", "", string.punctuation))

    def _remove_digits(self, text: str) -> str:
        """Remove standalone digits."""
        return re.sub(r"\b\d+\b", " ", text)

    def _remove_extra_whitespace(self, text: str) -> str:
        """Remove extra whitespace."""
        return " ".join(text.split())

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        try:
            return word_tokenize(text)
        except Exception:
            # Fallback to simple split
            return text.split()

    def _remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list."""
        if not self.remove_stopwords:
            return tokens
        return [t for t in tokens if t not in self.stopwords_set]

    def _apply_stemming(self, tokens: List[str]) -> List[str]:
        """Apply Porter stemming to tokens."""
        if not self.use_stemming:
            return tokens
        return [self.stemmer.stem(t) for t in tokens]

    def _apply_lemmatization(self, tokens: List[str]) -> List[str]:
        """Apply WordNet lemmatization to tokens."""
        if not self.use_lemmatization:
            return tokens
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def _filter_by_length(self, tokens: List[str]) -> List[str]:
        """Filter tokens by minimum length."""
        return [t for t in tokens if len(t) >= self.min_length]

    def preprocess(self, text: str) -> str:
        """
        Apply full preprocessing pipeline to a single text.

        Args:
            text: Raw input text

        Returns:
            Preprocessed text (tokenized and cleaned)
        """
        if not isinstance(text, str):
            return ""

        # Text normalization
        text = self._to_lowercase(text)
        text = self._remove_urls(text)
        text = self._remove_emails(text)
        text = self._remove_phone_numbers(text)
        text = self._remove_money(text)
        text = self._remove_punctuation(text)
        text = self._remove_digits(text)
        text = self._remove_extra_whitespace(text)

        # Tokenization
        tokens = self._tokenize(text)

        # Token filtering and transformation
        tokens = self._remove_stopwords(tokens)
        tokens = self._apply_stemming(tokens)
        tokens = self._apply_lemmatization(tokens)
        tokens = self._filter_by_length(tokens)

        # Return as space-separated string for vectorizer
        return " ".join(tokens)

    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Apply preprocessing to a batch of texts.

        Args:
            texts: List of raw input texts

        Returns:
            List of preprocessed texts
        """
        return [self.preprocess(text) for text in texts]

    def create_sklearn_transformer(self):
        """
        Create a sklearn-compatible transformer for pipeline integration.

        Returns:
            PreprocessingTransformer instance
        """
        return PreprocessingTransformer(self)


class PreprocessingTransformer:
    """
    Sklearn-compatible transformer wrapper for TextPreprocessor.

    Enables integration with sklearn Pipeline objects.
    """

    def __init__(self, preprocessor: TextPreprocessor):
        """
        Initialize the transformer.

        Args:
            preprocessor: TextPreprocessor instance to wrap
        """
        self.preprocessor = preprocessor

    def fit(self, X, y=None):
        """Fit method (no-op, preprocessing is stateless)."""
        return self

    def transform(self, X):
        """
        Transform texts using the preprocessor.

        Args:
            X: List or array of texts

        Returns:
            List of preprocessed texts
        """
        if hasattr(X, "tolist"):
            X = X.tolist()
        return self.preprocessor.preprocess_batch(X)

    def fit_transform(self, X, y=None):
        """Fit and transform (convenience method)."""
        return self.fit(X, y).transform(X)


# =============================================================================
# Convenience Functions (for simple use cases)
# =============================================================================


@lru_cache(maxsize=1)
def get_default_preprocessor() -> TextPreprocessor:
    """Get a preprocessor with default settings (cached)."""
    return TextPreprocessor(
        remove_stopwords=True,
        use_stemming=False,
        use_lemmatization=False,
        min_length=2,
    )


def preprocess_text(text: str) -> str:
    """
    Quick preprocessing function using default settings.

    Args:
        text: Raw input text

    Returns:
        Preprocessed text
    """
    return get_default_preprocessor().preprocess(text)
