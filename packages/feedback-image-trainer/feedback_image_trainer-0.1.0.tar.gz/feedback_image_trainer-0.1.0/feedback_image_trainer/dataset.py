import torch
import logging
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

logger = logging.getLogger(__name__)

class FeedbackDataset(Dataset):
    """Dataset for loading feedback-driven image-prompt pairs."""
    def __init__(self, data, tokenizer, image_size=(512, 512)):
        self.data = data
        self.tokenizer = tokenizer
        self.image_size = image_size
        self.transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.ToTensor(),  # Converts to [C, H, W] and normalizes to [0, 1]
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        try:
            if not all(key in item for key in ["image_path", "prompt"]):
                logger.warning(f"Skipping item {idx}: Missing 'image_path' or 'prompt'")
                raise KeyError("Missing required keys")
            
            image = Image.open(item["image_path"]).convert("RGB")
            image = self.transform(image)
            
            tokens = self.tokenizer(
                item["prompt"],
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=77
            ).input_ids[0]
            
            return {"pixel_values": image, "input_ids": tokens}
        except (FileNotFoundError, KeyError, Exception) as e:
            logger.error(f"Error processing item {idx}: {str(e)}")
            raise