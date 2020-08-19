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
        return Image.open(files["image"])

    def predict(self, features):
        features_t = self.transform(features).unsqueeze_(0).to(self.device)
        return self.model(features_t).max(1)[1].item()


if __name__ == "__main__":
    m = Model()
    with open("./tests/208.jpg", "rb") as f:
        m.validate(http_body=None, files={"image": f})
