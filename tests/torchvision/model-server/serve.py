"""
Script for serving.
"""
import torch
from PIL import Image
from torchvision.models import resnet50
from torchvision.transforms import CenterCrop, Compose, Normalize, Resize, ToTensor


def pre_process(http_body, files):
    return [Image.open(files["image"])]


class Model:
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = resnet50(pretrained=True)
        self.model.to(self.device)
        self.model.eval()
        self.transform = Compose(
            [
                Resize(256),
                CenterCrop(224),
                ToTensor(),
                Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def predict(self, features):
        features_t = self.transform(features[0]).unsqueeze_(0)
        return self.model(features_t).max(1)[1].item()
