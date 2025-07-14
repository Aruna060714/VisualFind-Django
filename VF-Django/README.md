VisualFind — Image Similarity Search

VisualFind is an web application built with Django that allows users to upload a product image and find visually similar items. It uses DINOv2 model for feature extraction and OpenSearch for scalable product retrieval.

##  Features

- Upload any product image
- Extract high-quality embeddings using **DINOv2 ViT-G**
- Compare images using **cosine similarity**
- Fast retrieval from **OpenSearch index**
- View all indexed products with pagination
- Stylish frontend with TailwindCSS
- Clean and responsive UI

## Project Workflow

1. **User Uploads Image**  
   → Image is converted to tensor and passed through DINOv2
2. **Embedding Generation**  
   → DINOv2 generates a 1536-dimensional vector
3. **Similarity Search**  
   → Cosine similarity is computed between input and all stored embeddings
4. **Metadata Display**  
   → Top 5 similar images shown with title and category
5. **All Products Page**  
   → Images loaded from OpenSearch index (with pagination)

##  Tech Stack

| Layer       | Tech Used                              |
|-------------|-----------------------------------------|
| Backend     | Django 5.2, Python 3.12                 |
| Frontend    | HTML, TailwindCSS                      |
| ML Model    | DINOv2 (`dinov2_vitg14` via Torch Hub) |
| Search      | OpenSearch (Bonsai Elasticsearch)      |
| Data Format | `.npy` for embeddings, `.json` for metadata |

##  Project Structure

    visualfind/
    │
    ├── core/
    │ ├── views.py # Core logic: index, upload, all-products
    │ ├── forms.py # Upload form
    │ ├── templates/
    │ │ └── core/
    │ │ ├── index.html
    │ │ ├── results.html
    │ │ └── all_products.html
    │ └── static/
    │ └── core/
    │ └── bg.jpg
    │
    ├── embeddings.npy # Numpy array of DINOv2 image vectors
    ├── metadata.json # Image metadata (title, URL, type)
    ├── manage.py
    └── requirements.txt

## OpenSearch Index
1. Index name: products_new
2. Must contain fields: image, title, type
3. Pagination and filtering done using OpenSearch queries