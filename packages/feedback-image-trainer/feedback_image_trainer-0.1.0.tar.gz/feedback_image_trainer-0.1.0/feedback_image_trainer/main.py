from .trainer import train_with_optuna

def run_study(feedback_file="image_feedback.json", model_path="runwayml/stable-diffusion-v1-5", output_dir="fine_tuned_model", trials=5):
    """
    Run a hyperparameter tuning study and train a Stable Diffusion model.

    Args:
        feedback_file (str): Path to feedback JSON file.
        model_path (str): Path to pre-trained or fine-tuned model.
        output_dir (str): Directory to save the final model.
        trials (int): Number of Optuna trials.
    """
    best_params = train_with_optuna(feedback_file, model_path, output_dir, trials)
    print("Best hyperparameters:", best_params)