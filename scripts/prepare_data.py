import json
import os
from sentence_transformers import SentenceTransformer

# Load embedding model
# This will download the model to the local cache if not already present
print("Loading sentence-transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def prepare_movie_data(input_path, output_path):
    """Prepare and enrich movie data with embeddings"""
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    # Load raw data
    print(f"Loading raw data from {input_path}...")
    with open(input_path, 'r') as f:
        movies = json.load(f)
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate embeddings for movie overviews
    print("Generating embeddings...")
    for movie in movies:
        text = f"{movie['title']} {movie['overview']}"
        embedding = model.encode(text).tolist()
        movie['embedding'] = embedding
    
    # Save processed data
    print(f"Saving processed data to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(movies, f, indent=2)
    
    print(f"Successfully processed {len(movies)} movies")

if __name__ == "__main__":
    prepare_movie_data(
        'data/raw/movies.json',
        'data/processed/movies_with_embeddings.json'
    )
