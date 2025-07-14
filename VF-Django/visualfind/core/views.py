import os
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from django.shortcuts import render, redirect
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from torchvision import transforms
from .forms import UploadForm
from opensearchpy import OpenSearch
model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitg14')
model.eval()
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=0.5, std=0.5)
])
_vectors = None
_metadata = None
def load_vectors():
    global _vectors, _metadata
    if _vectors is None or _metadata is None:
        base_dir = settings.BASE_DIR
        _vectors = np.load(os.path.join(base_dir, 'embeddings.npy'))
        with open(os.path.join(base_dir, 'metadata.json')) as f:
            _metadata = json.load(f)
    return _vectors, _metadata
def get_embedding(image: Image.Image):
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        return model(img_tensor).squeeze().numpy().reshape(1, -1)
client = OpenSearch(
    hosts=[{'host': 'superbotics-search-8731633774.eu-central-1.bonsaisearch.net', 'port': 443}],
    http_auth=('JC8YvqRN74', 'T8JEbusxGFN5VXZ'),
    use_ssl=True,
    verify_certs=True
)
INDEX_NAME = "products_new"
PAGE_SIZE = 20
def index_view(request):
    form = UploadForm()
    return render(request, 'core/index.html', {'form': form})
def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                img = Image.open(request.FILES['image']).convert('RGB')
            except Exception:
                return render(request, 'core/index.html', {
                    'form': form,
                    'error': 'Invalid image file.'
                })
            query_vec = get_embedding(img)
            vectors, metadata = load_vectors()
            similarities = cosine_similarity(query_vec, vectors)[0]
            top_indices = np.argsort(similarities)[::-1][:5]
            results = [{
                "image": metadata[i].get("image", ""),
                "title": metadata[i].get("title", "No Title"),
                "category": metadata[i].get("type", "Unknown"),
                "distance": round(float(similarities[i]), 4)
            } for i in top_indices]

            return render(request, 'core/results.html', {
                'results': results,
                'category': 'Auto'
            })
    return redirect('index')
def all_products_view(request):
    page = int(request.GET.get('page', 1))
    start = (page - 1) * PAGE_SIZE
    query = {
        "from": start,
        "size": PAGE_SIZE,
        "_source": ["image", "title", "price", "type"],
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "image"}},
                    {
                        "script": {
                            "script": {
                                "source": "doc['image'].size() > 0 && doc['image'].value != ''",
                                "lang": "painless"
                            }
                        }
                    }
                ]
            }
        }
    }
    response = client.search(index=INDEX_NAME, body=query)
    docs = [hit["_source"] for hit in response["hits"]["hits"]]
    total = response["hits"]["total"]["value"]
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    return render(request, "core/all_products.html", {
        "products": docs,
        "page": page,
        "total_pages": total_pages
    })