# taizun

`taizun` is a Python library that simplifies machine learning tasks by providing utility functions for **Natural Language Processing (NLP)** and **Computer Vision**. It leverages free pre-trained models from Hugging Face, making advanced AI tasks accessible and easy to use.


## Installation

Install the library using pip:

```bash
pip install taizun
```


---

## Features

### **Natural Language Processing (NLP)**

1. **Summarize Text**

   - Summarize long texts into concise, readable summaries.
   - **Usage**:
     ```python
     from taizun import summarize_text
     summary = summarize_text("Your long text here...")
     print(summary)
     ```
2. **Named Entity Recognition (NER)**

   - Identify entities like people, locations, and organizations in text.
   - **Usage**:
     ```python
     from taizun import named_entity_recognition
     entities = named_entity_recognition("Barack Obama was the 44th President of the United States.")
     print(entities)
     ```
3. **Text Generation**

   - Generate text from a prompt using GPT-2.
   - **Usage**:
     ```python
     from taizun import text_generation
     generated_text = text_generation("Once upon a time,")
     print(generated_text)
     ```
4. **Sentiment Analysis**

   - Analyze the sentiment of text (positive, negative, neutral).
   - **Usage**:
     ```python
     from taizun import sentiment_analysis
     sentiment = sentiment_analysis("I love this library!")
     print(sentiment)
     ```
5. **Remove Stopwords**

   - Remove common stopwords from text.
   - **Usage**:
     ```python
     from taizun import remove_stopwords
     cleaned_text = remove_stopwords("This is a sample text with stopwords.")
     print(cleaned_text)
     ```
6. **Word Frequency Analysis**

   - Analyze the frequency of words in a text.
   - **Usage**:
     ```python
     from taizun import word_frequency_analysis
     frequency = word_frequency_analysis("This is a test. This test is only a test.")
     print(frequency)
     ```

---

### **Computer Vision**

1. **Generate Image Caption**

   - Generate a natural language caption for an image.
   - **Usage**:
     ```python
     from taizun import generate_image_caption
     caption = generate_image_caption("path/to/image.jpg")
     print(caption)
     ```
2. **Classify Image**

   - Classify an image using a Vision Transformer (ViT) model.
   - **Usage**:
     ```python
     from taizun import classify_image
     label = classify_image("path/to/image.jpg")
     print(label)
     ```
3. **Detect Objects**

   - Detect objects in an image with bounding boxes and labels.
   - **Usage**:
     ```python
     from taizun import detect_objects
     objects = detect_objects("path/to/image.jpg")
     print(objects)
     ```
4. **Resize Image**

   - Resize an image to specified dimensions.
   - **Usage**:
     ```python
     from taizun import resize_image
     resized = resize_image("path/to/image.jpg", "path/to/output.jpg", size=(300, 300))
     print(resized)
     ```
5. **Convert to Grayscale**

   - Convert an image to grayscale.
   - **Usage**:
     ```python
     from taizun import convert_to_grayscale
     grayscale = convert_to_grayscale("path/to/image.jpg", "path/to/output_grayscale.jpg")
     print(grayscale)
     ```

---
