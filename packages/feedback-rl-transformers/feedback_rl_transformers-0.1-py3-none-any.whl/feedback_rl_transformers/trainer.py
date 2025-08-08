import os
import json
import logging
import optuna

from simpletransformers.question_answering import QuestionAnsweringModel, QuestionAnsweringArgs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_feedback_data(path):
    """Load feedback data from a JSON file and filter positive examples."""
    try:
        with open(path, "r") as f:
            raw_data = json.load(f)
        return [ex for ex in raw_data if isinstance(ex.get("feedback"), (int, float)) and ex["feedback"] > 0]
    except FileNotFoundError:
        logger.error(f"Feedback file not found: {path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in file: {path}")
        raise

def convert_to_squad_format(data):
    """Convert feedback data to SQuAD format."""
    squad_data = []
    for i, entry in enumerate(data):
        if not all(key in entry for key in ["answer", "question"]):
            logger.warning(f"Skipping entry {i}: Missing 'answer' or 'question' key")
            continue
        context = entry["answer"]
        question = entry["question"]
        answer_text = entry["answer"]
        answer_start = context.find(answer_text)
        if answer_start == -1:
            logger.warning(f"Skipping entry {i}: Answer text not found in context")
            continue
        squad_data.append({
            "context": context,
            "qas": [{
                "id": str(i),
                "question": question,
                "is_impossible": False,
                "answers": [{
                    "text": answer_text,
                    "answer_start": answer_start
                }]
            }]
        })
    if not squad_data:
        logger.error("No valid data converted to SQuAD format")
        raise ValueError("No valid data available for training")
    return squad_data

def build_model_args(trial=None, output_dir="outputs/optuna_trial", overwrite=True):
    """Build QuestionAnsweringArgs with optional Optuna trial parameters."""
    args = QuestionAnsweringArgs()
    args.reprocess_input_data = True
    args.overwrite_output_dir = overwrite
    args.output_dir = output_dir
    args.no_cache = True
    args.use_multiprocessing = False

    if trial:
        args.num_train_epochs = trial.suggest_int("num_train_epochs", 1, 4)
        args.learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)
        args.train_batch_size = trial.suggest_categorical("train_batch_size", [4, 8, 16])
        args.eval_batch_size = args.train_batch_size
    return args

def train_with_feedback(feedback_data_path, model_type, model_path, output_dir="fine_tuned_model", n_trials=5, use_cuda=False):
    """
    Train a QA model with feedback data using Optuna for hyperparameter tuning.

    Args:
        feedback_data_path (str): Path to feedback JSON file.
        model_type (str): Model type (e.g., 'bert').
        model_path (str): Path to pre-trained or fine-tuned model.
        output_dir (str): Directory to save the final model.
        n_trials (int): Number of Optuna trials for hyperparameter tuning.
        use_cuda (bool): Whether to use CUDA for training.
    """
    # Step 1: Load and preprocess data
    feedback_data = load_feedback_data(feedback_data_path)
    train_data = convert_to_squad_format(feedback_data)
    logger.info(f"Loaded {len(train_data)} training examples")

    # Step 2: Optimize with Optuna
    def objective(trial):
        model_args = build_model_args(trial, output_dir=f"{output_dir}/optuna_trial_{trial.number}")
        model = QuestionAnsweringModel(
            model_type=model_type,
            model_name=model_path,
            args=model_args,
            use_cuda=use_cuda
        )
        model.train_model(train_data)
        result, *_ = model.eval_model(train_data)
        return result["f1"]

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    logger.info("✅ Best Hyperparameters: %s", study.best_trial.params)

    # Step 3: Retrain final model
    best_args = build_model_args(output_dir=output_dir, overwrite=False)
    best_args.num_train_epochs = study.best_trial.params["num_train_epochs"]
    best_args.learning_rate = study.best_trial.params["learning_rate"]
    best_args.train_batch_size = study.best_trial.params["train_batch_size"]
    best_args.eval_batch_size = best_args.train_batch_size
    best_args.save_model_every_epoch = False

    final_model = QuestionAnsweringModel(
        model_type=model_type,
        model_name=model_path,
        args=best_args,
        use_cuda=use_cuda
    )
    final_model.train_model(train_data)

    # Step 4: Save final model
    final_model.save_model(output_dir)
    logger.info(f"🎉 Model training completed and saved to '{output_dir}'")