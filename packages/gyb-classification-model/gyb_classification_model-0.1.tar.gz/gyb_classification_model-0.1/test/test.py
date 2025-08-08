from ml_models import preprocess_text, predict_text

text = "AOB"

processed_text = preprocess_text(text)
category = predict_text(processed_text)

print(category['category'])

