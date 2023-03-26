from nudenet import NudeClassifier

classifier = NudeClassifier()

def is_unsafe(image_path, threshold=0.9):
    return classifier.classify(image_path)[image_path]['unsafe'] > threshold
