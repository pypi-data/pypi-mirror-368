# Dataset with Logits

A PyTorch package for loading computer vision datasets paired with pre-computed model logits. Perfect for knowledge distillation, model analysis, and efficient research workflows.

## 🚀 Quick Start

```bash
pip install dataset-with-logits
```

```python
import torchvision.transforms as transforms
from dataset_with_logits import ImageNet

# Define transforms
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# Create dataset (auto-downloads predictions)
dataset = ImageNet(
    root='/path/to/imagenet/val',
    model='resnet18',
    transform=transform,
    auto_download=True
)

# Use with DataLoader
from torch.utils.data import DataLoader
loader = DataLoader(dataset, batch_size=32, shuffle=True)

for images, labels, logits in loader:
    # images: [batch_size, 3, 224, 224] 
    # labels: [batch_size] - ground truth
    # logits: [batch_size, 1000] - model predictions
    break
```

## 📊 Available Models

### ImageNet-1K
- `resnet18` - ResNet-18 (11.7M parameters)
- `resnet50` - ResNet-50 (25.6M parameters)  
- `resnet152` - ResNet-152 (60.2M parameters)
- `vit_l_16` - Vision Transformer Large (304M parameters)
- `mobilenet_v3_small` - MobileNet V3 Small (2.5M parameters)
- `mobilenet_v3_large` - MobileNet V3 Large (5.5M parameters)

More models and datasets coming soon!

## 🎯 Use Cases

### Knowledge Distillation
```python
import torch.nn.functional as F

def knowledge_distillation_loss(student_logits, teacher_logits, labels, temperature=3.0):
    student_soft = F.log_softmax(student_logits / temperature, dim=1)
    teacher_soft = F.softmax(teacher_logits / temperature, dim=1)
    return F.kl_div(student_soft, teacher_soft, reduction='batchmean')

# In your training loop
for images, labels, teacher_logits in dataloader:
    student_logits = student_model(images)
    loss = knowledge_distillation_loss(student_logits, teacher_logits, labels)
```

### Model Analysis
```python
from dataset_with_logits import ImageNet

# Compare different models
models = ['resnet18', 'resnet152', 'vit_l_16']
datasets = {}

for model in models:
    datasets[model] = ImageNet(root=imagenet_path, model=model)

# Analyze prediction differences, calibration, etc.
```

## 🔧 Advanced Usage

### List Available Models
```python
from dataset_with_logits import list_available_models

models = list_available_models()
print(models)
# {'imagenet1k': {'resnet18': 'ResNet-18 (11.7M parameters)', ...}}
```

### Custom Cache Directory
```python
dataset = ImageNet(
    root='/path/to/imagenet',
    model='resnet18',
    cache_dir='/custom/cache/dir',
    auto_download=True
)
```

### Version Control
```python
dataset = ImageNet(
    root='/path/to/imagenet',
    model='resnet18',
    version='v0.1.0',  # Specific version
    auto_download=True
)
```

## 📁 File Format

Prediction files are CSV format with:
- `id`: Image filename (no extension)
- `label`: Ground truth class index  
- `logits`: Semicolon-separated model outputs

Example:
```csv
id,label,logits
ILSVRC2012_val_00000001,65,-2.3;1.7;0.2;...;0.8
ILSVRC2012_val_00000002,970,0.1;-1.2;3.4;...;-0.5
```

## 🌐 Data Source

Prediction files are automatically downloaded from **Hugging Face Hub** (primary) with GitHub fallback. Files are cached locally after first download.

**Hosting Infrastructure:**
- 🤗 **Primary**: [Hugging Face Datasets](https://huggingface.co/datasets/ViGeng/prediction-datasets) - Fast, reliable, academic-friendly
- 🐙 **Fallback**: GitHub Releases & LFS - For redundancy
- 📦 **Multi-backend**: Automatic fallback ensures high availability

## 🔍 Examples

See the `examples/` directory for:
- Basic usage
- Knowledge distillation
- Model comparison
- Advanced workflows

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install dataset-with-logits
```

### From Source
```bash
git clone https://github.com/ViGeng/predictions-on-datasets.git
cd predictions-on-datasets/dataset_with_logits
pip install -e .
```

## 🤝 Contributing

Contributions are welcome! See the main repository for contribution guidelines.

## 📄 License

MIT License - see LICENSE file for details.
