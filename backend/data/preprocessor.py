"""
Advanced Text preprocessing module.

Provides reusable text cleaning and normalization functions
for both training and inference pipelines.

Features:
- Standard text cleaning (lowercase, punctuation, etc.)
- URL, email, phone number detection and handling
- Emoji and emoticon processing
- Social media pattern handling (mentions, hashtags)
- Spam-specific pattern detection
- Custom spam feature extraction
"""

import re
import string
from typing import List, Optional, Dict, Any
from functools import lru_cache
from dataclasses import dataclass, field

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

from ..utils.logging import get_logger

logger = get_logger(__name__)


def _download_nltk_data():
    """Download required NLTK data packages."""
    resources = [
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
    ]

    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(name, quiet=True)
            except Exception:
                pass


_download_nltk_data()


@dataclass
class SpamFeatures:
    """Container for extracted spam-indicative features."""

    has_urls: bool = False
    url_count: int = 0
    has_emails: bool = False
    has_phone: bool = False
    has_money_symbols: bool = False
    money_count: int = 0
    has_excessive_punctuation: bool = False
    has_all_caps: bool = False
    emoji_count: int = 0
    has_suspicious_words: bool = False
    suspicious_word_count: int = 0
    exclamation_count: int = 0
    question_count: int = 0
    avg_word_length: float = 0.0
    char_to_word_ratio: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "has_urls": self.has_urls,
            "url_count": self.url_count,
            "has_emails": self.has_emails,
            "has_phone": self.has_phone,
            "has_money_symbols": self.has_money_symbols,
            "money_count": self.money_count,
            "has_excessive_punctuation": self.has_excessive_punctuation,
            "has_all_caps": self.has_all_caps,
            "emoji_count": self.emoji_count,
            "has_suspicious_words": self.has_suspicious_words,
            "suspicious_word_count": self.suspicious_word_count,
            "exclamation_count": self.exclamation_count,
            "question_count": self.question_count,
            "avg_word_length": round(self.avg_word_length, 2),
            "char_to_word_ratio": round(self.char_to_word_ratio, 2),
        }


class TextPreprocessor:
    """
    Advanced reusable text preprocessor for spam detection.

    Applies a pipeline of transformations:
    1. Lowercase conversion
    2. URL/email/phone removal or marking
    3. Emoji and emoticon processing
    4. Punctuation removal
    5. Stopword removal
    6. Tokenization
    7. Stemming/Lemmatization (optional)
    8. Spam feature extraction
    """

    # Common spam indicator words
    SPAM_WORDS = {
        'free', 'winner', 'won', 'prize', 'cash', 'money', 'claim',
        'urgent', 'act now', 'limited', 'offer', 'discount', 'buy',
        'click', 'subscribe', 'apply now', 'call now', 'order',
        'credit', 'loan', 'mortgage', 'investment', 'income',
        'guarantee', 'risk-free', 'no obligation', 'cancel anytime',
        'congratulations', 'selected', 'exclusive', 'secret',
        'password', 'account', 'verify', 'suspended', 'update',
        'lottery', 'million', 'dollars', 'pounds', 'euros',
        'viagra', 'cialis', 'medication', 'prescription', 'pharmacy',
        'weight loss', 'diet', 'miracle', 'amazing', 'incredible',
    }

    def __init__(
        self,
        remove_stopwords: bool = True,
        use_stemming: bool = False,
        use_lemmatization: bool = False,
        min_length: int = 2,
        custom_stopwords: Optional[List[str]] = None,
        extract_spam_features: bool = True,
        mark_special_tokens: bool = False,
    ):
        """
        Initialize the text preprocessor.

        Args:
            remove_stopwords: Remove common English stopwords
            use_stemming: Apply Porter stemming
            use_lemmatization: Apply WordNet lemmatization
            min_length: Minimum character length for tokens
            custom_stopwords: Additional stopwords to remove
            extract_spam_features: Extract spam-indicative features
            mark_special_tokens: Mark URLs/emails instead of removing
        """
        self.remove_stopwords = remove_stopwords
        self.use_stemming = use_stemming
        self.use_lemmatization = use_lemmatization
        self.min_length = min_length
        self.extract_spam_features = extract_spam_features
        self.mark_special_tokens = mark_special_tokens

        try:
            self.stopwords_set = set(stopwords.words("english"))
        except Exception:
            self.stopwords_set = set()
            logger.warning("NLTK stopwords not available")

        if custom_stopwords:
            self.stopwords_set.update(custom_stopwords)

        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        # Compile regex patterns
        self.url_pattern = re.compile(
            r"http\S+|www\.\S+|https?\S+|bit\.ly\S+|t\.co\S+|goo\.gl\S+",
            re.IGNORECASE
        )
        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )
        self.phone_pattern = re.compile(
            r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
        )
        self.money_pattern = re.compile(
            r"[$£€¥]\s*\d+(?:[.,]\d+)*|\d+(?:[.,]\d+)\s*(?:dollars?|pounds?|euros?|usd|gbp|eur)"
            r"|cash|money|prize|reward|payment",
            re.IGNORECASE
        )
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        self.hashtag_pattern = re.compile(r"#\w+")
        self.mention_pattern = re.compile(r"@\w+")
        self.exclamation_pattern = re.compile(r"!+")
        self.question_pattern = re.compile(r"\?+")

        logger.info(
            f"Preprocessor initialized: stopwords={remove_stopwords}, "
            f"stemming={use_stemming}, lemmatization={use_lemmatization}, "
            f"spam_features={extract_spam_features}"
        )

    def _remove_urls(self, text: str) -> str:
        if self.mark_special_tokens:
            return self.url_pattern.sub(" URL ", text)
        return self.url_pattern.sub(" ", text)

    def _remove_emails(self, text: str) -> str:
        if self.mark_special_tokens:
            return self.email_pattern.sub(" EMAIL ", text)
        return self.email_pattern.sub(" ", text)

    def _remove_phones(self, text: str) -> str:
        if self.mark_special_tokens:
            return self.phone_pattern.sub(" PHONE ", text)
        return self.phone_pattern.sub(" ", text)

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis but count them for features."""
        return self.emoji_pattern.sub(" ", text)

    def _remove_hashtags(self, text: str) -> str:
        """Remove hashtags but keep the word."""
        return self.hashtag_pattern.sub(lambda m: " " + m.group()[1:] + " ", text)

    def _remove_mentions(self, text: str) -> str:
        """Remove @mentions."""
        return self.mention_pattern.sub(" ", text)

    def _to_lowercase(self, text: str) -> str:
        return text.lower()

    def _remove_punctuation(self, text: str) -> str:
        return text.translate(str.maketrans("", "", string.punctuation))

    def _remove_digits(self, text: str) -> str:
        return re.sub(r"\b\d+\b", " ", text)

    def _remove_extra_whitespace(self, text: str) -> str:
        return " ".join(text.split())

    def _tokenize(self, text: str) -> List[str]:
        try:
            return word_tokenize(text)
        except Exception:
            return text.split()

    def _remove_stopwords(self, tokens: List[str]) -> List[str]:
        if not self.remove_stopwords:
            return tokens
        return [t for t in tokens if t not in self.stopwords_set]

    def _apply_stemming(self, tokens: List[str]) -> List[str]:
        if not self.use_stemming:
            return tokens
        return [self.stemmer.stem(t) for t in tokens]

    def _apply_lemmatization(self, tokens: List[str]) -> List[str]:
        if not self.use_lemmatization:
            return tokens
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def _filter_by_length(self, tokens: List[str]) -> List[str]:
        return [t for t in tokens if len(t) >= self.min_length]

    def extract_features(self, text: str) -> SpamFeatures:
        """
        Extract spam-indicative features from text.

        Args:
            text: Raw input text

        Returns:
            SpamFeatures dataclass with extracted features
        """
        features = SpamFeatures()

        if not isinstance(text, str) or not text.strip():
            return features

        # URL detection
        urls = self.url_pattern.findall(text)
        features.url_count = len(urls)
        features.has_urls = features.url_count > 0

        # Email detection
        features.has_emails = bool(self.email_pattern.search(text))

        # Phone detection
        features.has_phone = bool(self.phone_pattern.search(text))

        # Money symbols detection
        money_matches = self.money_pattern.findall(text)
        features.money_count = len(money_matches)
        features.has_money_symbols = features.money_count > 0

        # Emoji detection
        emojis = self.emoji_pattern.findall(text)
        features.emoji_count = len(emojis)

        # Excessive punctuation
        exclamations = self.exclamation_pattern.findall(text)
        questions = self.question_pattern.findall(text)
        features.exclamation_count = sum(len(m) for m in exclamations)
        features.question_count = sum(len(m) for m in questions)
        features.has_excessive_punctuation = (
            features.exclamation_count > 2 or features.question_count > 2
        )

        # All caps words (shouting)
        words = text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        features.has_all_caps = len(caps_words) > 2

        # Suspicious/spam words
        text_lower = text.lower()
        suspicious = [w for w in self.SPAM_WORDS if w in text_lower]
        features.suspicious_word_count = len(suspicious)
        features.has_suspicious_words = features.suspicious_word_count > 0

        # Text statistics
        clean_words = [w for w in words if w.isalpha()]
        if clean_words:
            features.avg_word_length = sum(len(w) for w in clean_words) / len(clean_words)
            features.char_to_word_ratio = len(text) / len(clean_words) if clean_words else 0

        return features

    def preprocess(self, text: str, return_features: bool = False):
        """
        Apply full preprocessing pipeline to a single text.

        Args:
            text: Raw input text
            return_features: If True, return (processed_text, features) tuple

        Returns:
            Preprocessed text string, or (text, features) tuple
        """
        if not isinstance(text, str):
            if return_features:
                return "", SpamFeatures()
            return ""

        # Extract features before cleaning if requested
        features = None
        if self.extract_spam_features and return_features:
            features = self.extract_features(text)

        # Apply preprocessing pipeline
        text = self._to_lowercase(text)
        text = self._remove_urls(text)
        text = self._remove_emails(text)
        text = self._remove_phones(text)
        text = self._remove_emojis(text)
        text = self._remove_hashtags(text)
        text = self._remove_mentions(text)
        text = self._remove_punctuation(text)
        text = self._remove_digits(text)
        text = self._remove_extra_whitespace(text)

        tokens = self._tokenize(text)
        tokens = self._remove_stopwords(tokens)
        tokens = self._apply_stemming(tokens)
        tokens = self._apply_lemmatization(tokens)
        tokens = self._filter_by_length(tokens)

        processed_text = " ".join(tokens)

        if return_features and features:
            return processed_text, features
        return processed_text

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
        """Create a sklearn-compatible transformer."""
        return PreprocessingTransformer(self)


class PreprocessingTransformer:
    """
    Sklearn-compatible transformer wrapper for TextPreprocessor.

    Enables integration with sklearn Pipeline objects.
    """

    def __init__(self, preprocessor: TextPreprocessor):
        self.preprocessor = preprocessor

    def fit(self, X, y=None):
        """Fit method (no-op, preprocessing is stateless)."""
        return self

    def transform(self, X):
        """Transform texts using the preprocessor."""
        if hasattr(X, "tolist"):
            X = X.tolist()
        return self.preprocessor.preprocess_batch(X)

    def fit_transform(self, X, y=None):
        """Fit and transform."""
        return self.fit(X, y).transform(X)


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
    """Quick preprocessing function using default settings."""
    return get_default_preprocessor().preprocess(text)
