from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

def imagecaption(image_path, model_name="Salesforce/blip-image-captioning-base"):
    """Generate a caption for an image."""
    processor = BlipProcessor.from_pretrained(model_name)
    model = BlipForConditionalGeneration.from_pretrained(model_name)
    image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    outputs = model.generate(**inputs)
    return processor.decode(outputs[0], skip_special_tokens=True)

def classify_image(image_path, model_name="google/vit-base-patch16-224"):
    """Classify an image using a vision transformer model."""
    from transformers import ViTImageProcessor, ViTForImageClassification

    processor = ViTImageProcessor.from_pretrained(model_name)
    model = ViTForImageClassification.from_pretrained(model_name)
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    return model.config.id2label[torch.argmax(outputs.logits).item()]

def spot(image_path, model_name="facebook/detr-resnet-50"):
    """Detect objects in an image using DETR."""
    from transformers import DetrImageProcessor, DetrForObjectDetection

    processor = DetrImageProcessor.from_pretrained(model_name)
    model = DetrForObjectDetection.from_pretrained(model_name)
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    # Extracting the objects detected
    prob_threshold = 0.9  # Only include objects with a probability > 90%
    results = []
    for logit, box in zip(outputs.logits[0], outputs.pred_boxes[0]):
        prob = torch.softmax(logit, -1)[:-1].max()
        if prob > prob_threshold:
            label = model.config.id2label[torch.argmax(logit).item()]
            box = box.tolist()
            results.append({"label": label, "box": box, "probability": float(prob)})
    return results

def resize_image(image_path, output_path, size=(224, 224)):
    """Resize an image to the specified size."""
    image = Image.open(image_path)
    resized_image = image.resize(size)
    resized_image.save(output_path)
    return f"Image resized and saved to {output_path}"

def grayscale(image_path, output_path):
    """Convert an image to grayscale."""
    image = Image.open(image_path)
    grayscale_image = image.convert("L")
    grayscale_image.save(output_path)
    return f"Image converted to grayscale and saved to {output_path}"
