with open('backend/inference/predictor.py', 'r') as f:
    text = f.read()

old_logic = '''        if spam_prob > 0.8:
            confidence_level = "very high"
        elif spam_prob > 0.6:
            confidence_level = "high"
        elif spam_prob > 0.4:
            confidence_level = "moderate"
        else:
            confidence_level = "low"'''

new_logic = '''        confidence = max(spam_prob, 1.0 - spam_prob)
        if confidence > 0.9:
            confidence_level = "very high"
        elif confidence > 0.8:
            confidence_level = "high"
        elif confidence > 0.6:
            confidence_level = "moderate"
        else:
            confidence_level = "low"'''

if old_logic in text:
    text = text.replace(old_logic, new_logic)
    with open('backend/inference/predictor.py', 'w') as f:
        f.write(text)
    print("Fixed confidence metric message!")
else:
    print("Could not find the segment to replace")
