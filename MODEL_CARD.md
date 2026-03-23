# Model Card: SpamShield ML

## Model Details

### Model Information
- **Model Type**: Text Classification (Binary: Spam/Ham)
- **Architecture**: Logistic Regression + TF-IDF Vectorizer / Multinomial Naive Bayes
- **Version**: 1.0.0
- **Date**: March 2026
- **License**: MIT License

### Model Authors
- Your Name / Organization

### Contact
- Email: [INSERT EMAIL]

### Model Repository
- GitHub: https://github.com/yourusername/spam-detection

---

## Intended Use

### Primary Use Cases
- Filtering spam SMS messages
- Email spam detection
- User-generated content moderation
- Educational purposes for ML/NLP learning

### Out-of-Scope Use Cases
- **Critical decision-making** (legal, financial, medical)
- **High-stakes content moderation** without human review
- **Surveillance or monitoring** without user consent
- **Discriminatory profiling** of individuals or groups
- **Automated account suspension** without appeal process

---

## Training Data

### Dataset Description
- **Primary Dataset**: UCI SMS Spam Collection
- **Size**: 5,572 messages
- **Class Distribution**: ~86.6% ham, ~13.4% spam
- **Language**: English
- **Time Period**: 2012

### Data Limitations
- **Language Bias**: Trained only on English text; performance degrades on other languages
- **Cultural Bias**: SMS spam patterns vary by region and culture
- **Temporal Bias**: Spam tactics evolve; model may not detect modern spam techniques
- **Domain Bias**: Trained on SMS; performance on email/social media may differ
- **Demographic Gaps**: No demographic information available; potential bias across user groups

### Data Preprocessing
- Lowercase normalization
- URL, email, phone number tokenization
- Stop word removal (optional)
- Lemmatization (default)
- Custom spam feature extraction (15+ indicators)

---

## Evaluation Metrics

### Performance on Test Set (UCI SMS)

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression + TF-IDF | 98.5% | 97.9% | 97.8% | 97.8% | 99.2% |
| Naive Bayes + Count Vectorizer | 97.8% | 96.5% | 96.2% | 96.3% | 98.7% |

### Cross-Validation
- **Method**: Stratified 5-fold cross-validation
- **Standard Deviation**: ±0.3% accuracy

### Known Performance Gaps
- **Short messages** (< 10 characters): Lower confidence
- **Mixed languages**: Significant performance degradation
- **Sarcasm/irony**: Often misclassified
- **Legitimate marketing messages**: May be flagged as spam
- **Sophisticated phishing**: May evade detection

---

## Ethical Considerations

### Bias and Fairness

#### Potential Biases
1. **Language Bias**: Model performs poorly on non-English text, potentially disadvantaging non-English speakers
2. **Cultural Bias**: What constitutes "spam" varies across cultures and contexts
3. **Socioeconomic Bias**: Spam patterns may differ across demographic groups
4. **False Positive Impact**: Legitimate messages incorrectly flagged may cause users to miss important communications

#### Mitigation Strategies
- ✅ Clear documentation of limitations
- ✅ Confidence scores provided with predictions
- ✅ Configurable threshold for different use cases
- ✅ Feature attribution for explainability
- ⚠️ **Recommended**: Regular bias audits with diverse test sets
- ⚠️ **Recommended**: Human review for high-stakes decisions

### Privacy Considerations
- Model processes message text; ensure compliance with privacy regulations (GDPR, CCPA)
- Do not log or store message content without user consent
- Consider on-device inference for sensitive applications

### Dual-Use Concerns
- **Misuse Risk**: Could be adapted for surveillance or censorship
- **Mitigation**: Clear license restrictions and terms of use

---

## Limitations

### Technical Limitations
1. **Language Support**: English only
2. **Context Understanding**: No long-term context or conversation history
3. **Adaptability**: Requires retraining for new spam patterns
4. **Adversarial Robustness**: Vulnerable to carefully crafted adversarial examples
5. **Cold Start**: No personalization without fine-tuning

### Operational Limitations
1. **Latency**: ~100ms per message (may not suit real-time applications)
2. **Throughput**: Batch processing limited to 1,000 messages per request
3. **Resource Requirements**: ~150MB memory footprint
4. **Dependency on NLTK**: Requires external data downloads

### Ethical Limitations
1. **Not suitable for high-stakes decisions** without human oversight
2. **May perpetuate existing biases** in training data
3. **Should not be sole criterion** for content moderation
4. **Requires transparency** with end users about automated filtering

---

## Recommendations

### Best Practices for Deployment

#### Do ✅
- Use as **one signal** in a broader moderation system
- Provide **user controls** to override classifications
- Implement **appeal mechanisms** for false positives
- **Monitor performance** across different user groups
- **Update regularly** with new spam patterns
- Be **transparent** about automated filtering
- Set **conservative thresholds** for sensitive applications

#### Don't ❌
- Use for **automated account suspension** without review
- Deploy in **high-stakes contexts** (legal, medical, financial)
- Apply to **languages other than English** without validation
- **Hide the use** of automated filtering from users
- Assume **perfect accuracy**; always expect errors
- Use **without monitoring** for performance degradation

### Monitoring Recommendations
- Track **false positive rate** by user segment
- Monitor **confidence score distribution** over time
- Log **prediction drift** to detect spam evolution
- Implement **human review queue** for low-confidence predictions
- Regular **bias audits** with diverse test datasets

---

## Reproducibility

### Training Instructions
```bash
# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download(['punkt_tab', 'stopwords', 'wordnet'])"

# Train models
python backend/main.py train

# Evaluate
pytest tests/ -v
```

### Model Artifacts
- Location: `models/` directory
- Format: `.joblib` (scikit-learn pipeline)
- Version: Included in model filename

### Environment
- Python: 3.9+
- scikit-learn: 1.3+
- NLTK: 3.8+
- See `requirements.txt` for full dependency list

---

## Citation

If you use this model in your research:

```bibtex
@software{spamshield_ml2026,
  author = {Your Name},
  title = {SpamShield ML: Production-Grade Spam Detection System},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/yourusername/spam-detection},
  license = {MIT}
}
```

---

## Changelog

### Version 1.0.0 (March 2026)
- Initial release
- Logistic Regression + TF-IDF pipeline
- Naive Bayes + Count Vectorizer pipeline
- 15+ custom spam features
- Full API and web interface

---

## Acknowledgments

- **Dataset**: UCI SMS Spam Collection (Almeida & Gómez Hidalgo, 2012)
- **Framework**: scikit-learn, FastAPI, Next.js
- **Contributors**: See GitHub contributors page

---

## Contact & Feedback

For questions, concerns, or feedback about this model:
- **GitHub Issues**: https://github.com/yourusername/spam-detection/issues
- **Email**: [INSERT EMAIL]

**Report Bias or Harm**: If you encounter biased or harmful outputs, please report them responsibly via our [Security Policy](SECURITY.md).

---

*This model card is a living document and will be updated as the model evolves.*
