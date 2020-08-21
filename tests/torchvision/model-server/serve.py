"""
Script for serving.
"""
import torch
from bedrock_client.bedrock.model import BaseModel
from PIL import Image
from torchvision.models import resnet50
from torchvision.transforms import CenterCrop, Compose, Normalize, Resize, ToTensor


class Model(BaseModel):
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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

    def pre_process(self, http_body, files):
        img = Image.open(files["image"])
        features = self.transform(img).unsqueeze_(0).to(self.device)
        return features

    def predict(self, features):
        print(features)
        return self.model(features).max(1)[1].tolist()
