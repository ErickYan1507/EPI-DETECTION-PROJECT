import torch
import glob
import argparse
from collections import OrderedDict

def unify_models(model_paths_glob, output_path):
    """
    This function loads multiple YOLOv5 models, averages their weights,
    and saves the result to a new model file.

    Args:
        model_paths_glob (str): Glob pattern to find the models to merge.
        output_path (str): Path to save the unified model.
    """
    print(f"Searching for models with pattern: {model_paths_glob}")
    model_paths = glob.glob(model_paths_glob)
    if not model_paths:
        print("No models found. Please check the path/pattern.")
        return

    print(f"Found {len(model_paths)} models to unify:")
    for path in model_paths:
        print(f" - {path}")

    # Load all models and accumulate their state dicts
    models = [torch.load(path, map_location=torch.device('cpu')) for path in model_paths]
    
    # Use the state_dict from the first model as the base
    unified_statedict = OrderedDict()

    # Get all keys from the first model's state_dict
    keys = models[0]['model'].state_dict().keys()

    for key in keys:
        # Sum the weights for the current key from all models
        tensors = [m['model'].state_dict()[key].float() for m in models]
        summed_tensor = torch.stack(tensors).sum(0)
        
        # Average the weights
        averaged_tensor = summed_tensor / len(models)
        
        # Add the averaged tensor to the unified state_dict
        unified_statedict[key] = averaged_tensor

    # Create the final model structure
    final_model = models[0] # Use the first model as a template
    final_model['model'].load_state_dict(unified_statedict)
    final_model['names'] = models[0]['names'] # Ensure class names are preserved

    # Save the unified model
    torch.save(final_model, output_path)
    print(f"\nSuccessfully unified {len(models)} models.")
    print(f"Unified model saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Unify YOLOv5 models by averaging their weights.")
    parser.add_argument(
        '--input-glob', 
        type=str, 
        required=True, 
        help="Glob pattern to find models to unify (e.g., 'models/exp*.pt'). Quote the pattern to avoid shell expansion."
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='models/best.pt',
        help="Path to save the unified model file."
    )
    args = parser.parse_args()

    unify_models(args.input_glob, args.output)

if __name__ == "__main__":
    main()
