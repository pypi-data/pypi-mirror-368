from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer,AutoModelForCausalLM, AutoTokenizer
import re 
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def coder(prompt, model_name="bigcode/santacoder"):
    """Generates Python code from a given prompt using an open-source model."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        **inputs,
        max_length=300,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
        top_p=0.95
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)




def summarize(text, model_name="t5-small", max_length=50, min_length=25):
    """Summarize long texts."""
    summarizer = pipeline("summarization", model=model_name)
    summary = summarizer(text, max_length=max_length, min_length=min_length, truncation=True)
    return summary[0]["summary_text"]

def labels(text, model_name="dbmdz/bert-large-cased-finetuned-conll03-english"):
    """Perform NER on a given text."""
    ner_pipeline = pipeline("ner", model=model_name, grouped_entities=True)
    return ner_pipeline(text)

def  textify(prompt, model_name="distilgpt2", max_length=50):
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(**inputs, max_length=max_length, num_return_sequences=1, do_sample=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)




def moodscan(text, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
    """Perform sentiment analysis on a given text."""
    sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)
    return sentiment_pipeline(text)

def scrub(text, stopwords=None):
    """Remove stopwords from text."""
    if stopwords is None:
        stopwords = {"and", "or", "but", "so", "the", "a", "an", "of", "in", "on"}
    return " ".join([word for word in text.split() if word.lower() not in stopwords])

def wordcount(text):
    """Calculate word frequency in a text."""
    words = re.findall(r'\b\w+\b', text.lower())
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
    return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))
