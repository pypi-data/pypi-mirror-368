import json
import logging
import torch
import optuna
from torch.utils.data import DataLoader
from diffusers import StableDiffusionPipeline
from transformers import CLIPTokenizer
from accelerate import Accelerator
from .dataset import FeedbackDataset

logger = logging.getLogger(__name__)

def load_feedback_data(path):
    """Load feedback data from JSON and filter positive examples."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return [d for d in data if isinstance(d.get("feedback"), (int, float)) and d["feedback"] > 0]
    except FileNotFoundError:
        logger.error(f"Feedback file not found: {path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in file: {path}")
        raise

def objective(trial, data, model_path, tokenizer, accelerator):
    """Optuna objective function for hyperparameter tuning."""
    lr = trial.suggest_float("lr", 1e-6, 1e-4, log=True)
    batch_size = trial.suggest_categorical("batch_size", [1, 2, 4])

    pipe = StableDiffusionPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.float32
    )
    
    pipe.unet.train()
    pipe.vae.eval()
    pipe.text_encoder.eval()

    dataset = FeedbackDataset(data, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.AdamW(pipe.unet.parameters(), lr=lr)
    
    unet, optimizer, dataloader = accelerator.prepare(pipe.unet, optimizer, dataloader)

    total_loss = 0
    for batch in dataloader:
        imgs = batch["pixel_values"].to(accelerator.device)
        ids = batch["input_ids"].to(accelerator.device)

        with torch.no_grad():
            latents = pipe.vae.encode(imgs).latent_dist.sample() * 0.18215
            noise = torch.randn_like(latents)
            t = torch.randint(0, 1000, (latents.shape[0],), device=latents.device)
            enc = pipe.text_encoder(ids)[0]
            noisy_latents = pipe.scheduler.add_noise(latents, noise, t)

        pred = unet(noisy_latents, t, enc).sample
        loss = torch.nn.functional.mse_loss(pred, noise)
        optimizer.zero_grad()
        accelerator.backward(loss)
        optimizer.step()
        total_loss += loss.item()

    return total_loss / len(dataloader)

def train_with_optuna(feedback_json_path, model_path, output_dir="fine_tuned_model", n_trials=5):
    """
    Train a Stable Diffusion model with feedback data using Optuna.

    Args:
        feedback_json_path (str): Path to feedback JSON file.
        model_path (str): Path to pre-trained or fine-tuned model.
        output_dir (str): Directory to save the final model.
        n_trials (int): Number of Optuna trials.
    """
    # Initialize logging and accelerator
    logging.basicConfig(level=logging.INFO)
    accelerator = Accelerator()

    # Load data
    data = load_feedback_data(feedback_json_path)
    logger.info(f"Loaded {len(data)} positive feedback examples")

    # Load tokenizer
    tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")

    # Run Optuna study
    study = optuna.create_study(direction="minimize")
    study.optimize(lambda trial: objective(trial, data, model_path, tokenizer, accelerator), n_trials=n_trials)

    logger.info("✅ Best Hyperparameters: %s", study.best_params)

    # Retrain with best hyperparameters
    best_lr = study.best_params["lr"]
    best_batch_size = study.best_params["batch_size"]

    pipe = StableDiffusionPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.float32
    )
    pipe.unet.train()
    pipe.vae.eval()
    pipe.text_encoder.eval()

    dataset = FeedbackDataset(data, tokenizer)
    dataloader = DataLoader(dataset, batch_size=best_batch_size, shuffle=True)
    optimizer = torch.optim.AdamW(pipe.unet.parameters(), lr=best_lr)
    
    unet, optimizer, dataloader = accelerator.prepare(pipe.unet, optimizer, dataloader)

    for batch in dataloader:
        imgs = batch["pixel_values"].to(accelerator.device)
        ids = batch["input_ids"].to(accelerator.device)

        with torch.no_grad():
            latents = pipe.vae.encode(imgs).latent_dist.sample() * 0.18215
            noise = torch.randn_like(latents)
            t = torch.randint(0, 1000, (latents.shape[0],), device=latents.device)
            enc = pipe.text_encoder(ids)[0]
            noisy_latents = pipe.scheduler.add_noise(latents, noise, t)

        pred = unet(noisy_latents, t, enc).sample
        loss = torch.nn.functional.mse_loss(pred, noise)
        optimizer.zero_grad()
        accelerator.backward(loss)
        optimizer.step()

    # Save the fine-tuned model
    pipe.save_pretrained(output_dir)
    logger.info(f"🎉 Model training completed and saved to '{output_dir}'")

    return study.best_params