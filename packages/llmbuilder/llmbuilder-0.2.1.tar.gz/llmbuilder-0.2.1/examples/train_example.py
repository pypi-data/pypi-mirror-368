"""
Example script to train a language model using llmbuilder package.
This script demonstrates how to:
1. Load and prepare data
2. Train a language model
3. Generate text using the trained model
"""
import os
from pathlib import Path
from llmbuilder import train, generate_text

def main():
    # Configuration
    data_path = Path("data/sample_data.txt")  # Path to your training data
    output_dir = Path("output")  # Directory to save the model and outputs
    
    # Clean output directory if it exists
    if output_dir.exists():
        print(f"Cleaning up existing output directory: {output_dir}")
        import shutil
        shutil.rmtree(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting training with data from: {data_path.absolute()}")
    print(f"Output will be saved to: {output_dir.absolute()}")
    
    try:
        # Train the model
        print("\n=== Starting Training ===")
        pipeline = train(
            data_path=str(data_path),
            output_dir=str(output_dir),
            clean=True
        )
        
        print("\nTraining completed successfully!")
        
        # Example: Generate some text
        print("\n=== Example Generation ===")
        prompts = [
            "Artificial intelligence is",
            "Machine learning can be used to",
            "The future of AI will"
        ]
        
        for prompt in prompts:
            print(f"\nPrompt: {prompt}")
            generated = pipeline.generate(
                prompt,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True
            )
            print(f"Generated: {generated}")
            
    except Exception as e:
        print(f"\nAn error occurred during training: {str(e)}")
        raise

if __name__ == "__main__":
    main()
