import torch
from torch.utils.data import DataLoader, Dataset
import numpy as np
from typing import List, Dict, Any, Optional, Callable
import os
import json
from PIL import Image
import torchvision.transforms as transforms
import time

class CustomDataset(Dataset):
    """
    自定义数据集
    任务书要求：支持图像、文本等类型，支持数据增强
    """
    
    def __init__(self, data, labels, transform=None, data_type='image'):
        """
        Args:
            data: 数据
            labels: 标签
            transform: 数据变换
            data_type: 数据类型 ('image', 'text')
        """
        self.data = data
        self.labels = labels
        self.transform = transform
        self.data_type = data_type

    def __getitem__(self, idx):
        x = self.data[idx]
        y = self.labels[idx]
        
        if self.transform:
            if self.data_type == 'image':
                x = self.transform(x)
            elif self.data_type == 'text':
                x = self.transform(x)
        
        return x, y

    def __len__(self):
        return len(self.data)

class DataAugmentation:
    """
    数据增强模块
    任务书要求：支持样本库中的数据增强方法（如水平翻转、高斯模糊，任务书"样本管理"提及的7种方法）
    """
    
    def __init__(self, augmentation_type='image'):
        """
        Args:
            augmentation_type: 增强类型 ('image', 'text')
        """
        self.augmentation_type = augmentation_type
        self.augmentations = self._get_augmentations()
    
    def _get_augmentations(self) -> Dict[str, Callable]:
        """获取数据增强方法"""
        if self.augmentation_type == 'image':
            return {
                'horizontal_flip': transforms.RandomHorizontalFlip(p=0.5),
                'vertical_flip': transforms.RandomVerticalFlip(p=0.5),
                'rotation': transforms.RandomRotation(degrees=15),
                'gaussian_blur': transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
                'color_jitter': transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
                'random_crop': transforms.RandomCrop(size=(224, 224), padding=10),
                'random_erasing': transforms.RandomErasing(p=0.2, scale=(0.02, 0.33))
            }
        elif self.augmentation_type == 'text':
            return {
                'synonym_replacement': self._synonym_replacement,
                'random_insertion': self._random_insertion,
                'random_deletion': self._random_deletion,
                'random_swap': self._random_swap,
                'back_translation': self._back_translation
            }
        else:
            return {}
    
    def _synonym_replacement(self, text: str) -> str:
        """同义词替换"""
        # 简化实现
        return text
    
    def _random_insertion(self, text: str) -> str:
        """随机插入"""
        # 简化实现
        return text
    
    def _random_deletion(self, text: str) -> str:
        """随机删除"""
        # 简化实现
        return text
    
    def _random_swap(self, text: str) -> str:
        """随机交换"""
        # 简化实现
        return text
    
    def _back_translation(self, text: str) -> str:
        """回译"""
        # 简化实现
        return text
    
    def apply_augmentation(self, data, method: str) -> Any:
        """应用数据增强"""
        if method not in self.augmentations:
            raise ValueError(f"不支持的数据增强方法: {method}")
        
        augmentor = self.augmentations[method]
        return augmentor(data)
    
    def apply_multiple_augmentations(self, data, methods: List[str]) -> List[Any]:
        """应用多种数据增强"""
        results = []
        for method in methods:
            if method in self.augmentations:
                augmented_data = self.apply_augmentation(data, method)
                results.append(augmented_data)
        return results

class SampleLibrary:
    """
    样本库管理
    任务书要求：支持版本管理和筛选，支持图像、文本等类型
    """
    
    def __init__(self, library_path: str):
        """
        Args:
            library_path: 样本库路径
        """
        self.library_path = library_path
        os.makedirs(library_path, exist_ok=True)
        
        # 样本库元数据文件
        self.metadata_file = os.path.join(library_path, 'metadata.json')
        self._load_metadata()
    
    def _load_metadata(self):
        """加载元数据"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                'samples': {},
                'versions': {},
                'categories': {}
            }
    
    def _save_metadata(self):
        """保存元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def add_sample(self, 
                  sample_id: str, 
                  data: Any, 
                  labels: List[int], 
                  category: str = 'clean',
                  version: str = 'v1.0',
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        添加样本到样本库
        Args:
            sample_id: 样本ID
            data: 样本数据
            labels: 标签
            category: 类别（clean, adversarial, augmented）
            version: 版本
            metadata: 额外元数据
        Returns:
            样本路径
        """
        # 创建版本目录
        version_dir = os.path.join(self.library_path, version)
        os.makedirs(version_dir, exist_ok=True)
        
        # 保存样本数据
        sample_path = os.path.join(version_dir, f"{sample_id}.pth")
        torch.save({
            'data': data,
            'labels': labels,
            'category': category,
            'metadata': metadata or {}
        }, sample_path)
        
        # 更新元数据
        sample_info = {
            'id': sample_id,
            'path': sample_path,
            'category': category,
            'version': version,
            'labels': labels,
            'metadata': metadata or {},
            'created_at': str(time.time())
        }
        
        self.metadata['samples'][sample_id] = sample_info
        
        if category not in self.metadata['categories']:
            self.metadata['categories'][category] = []
        self.metadata['categories'][category].append(sample_id)
        
        if version not in self.metadata['versions']:
            self.metadata['versions'][version] = []
        self.metadata['versions'][version].append(sample_id)
        
        self._save_metadata()
        
        print(f"样本已添加到库: {sample_id} (版本: {version}, 类别: {category})")
        return sample_path
    
    def get_sample(self, sample_id: str, version: str = None) -> Dict[str, Any]:
        """获取样本"""
        if sample_id not in self.metadata['samples']:
            raise ValueError(f"样本不存在: {sample_id}")
        
        sample_info = self.metadata['samples'][sample_id]
        
        if version and sample_info['version'] != version:
            raise ValueError(f"版本不匹配: 请求 {version}, 实际 {sample_info['version']}")
        
        # 加载样本数据
        sample_data = torch.load(sample_info['path'])
        sample_data['info'] = sample_info
        
        return sample_data
    
    def list_samples(self, 
                    category: Optional[str] = None, 
                    version: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出样本"""
        samples = []
        
        for sample_id, sample_info in self.metadata['samples'].items():
            if category and sample_info['category'] != category:
                continue
            if version and sample_info['version'] != version:
                continue
            samples.append(sample_info)
        
        return samples
    
    def delete_sample(self, sample_id: str):
        """删除样本"""
        if sample_id not in self.metadata['samples']:
            raise ValueError(f"样本不存在: {sample_id}")
        
        sample_info = self.metadata['samples'][sample_id]
        
        # 删除文件
        if os.path.exists(sample_info['path']):
            os.remove(sample_info['path'])
        
        # 更新元数据
        del self.metadata['samples'][sample_id]
        
        # 从分类中移除
        category = sample_info['category']
        if category in self.metadata['categories']:
            self.metadata['categories'][category] = [
                sid for sid in self.metadata['categories'][category] if sid != sample_id
            ]
        
        # 从版本中移除
        version = sample_info['version']
        if version in self.metadata['versions']:
            self.metadata['versions'][version] = [
                sid for sid in self.metadata['versions'][version] if sid != sample_id
            ]
        
        self._save_metadata()
        print(f"样本已删除: {sample_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取样本库统计信息"""
        stats = {
            'total_samples': len(self.metadata['samples']),
            'categories': {},
            'versions': {}
        }
        
        for category, samples in self.metadata['categories'].items():
            stats['categories'][category] = len(samples)
        
        for version, samples in self.metadata['versions'].items():
            stats['versions'][version] = len(samples)
        
        return stats

class DataLoaderFactory:
    """
    数据加载器工厂
    支持创建不同类型的数据加载器
    """
    
    @staticmethod
    def create_image_loader(data, labels, batch_size=32, shuffle=True, num_workers=4, 
                           augmentations: Optional[List[str]] = None):
        """创建图像数据加载器"""
        transforms_list = []
        
        if augmentations:
            augmentor = DataAugmentation('image')
            for aug in augmentations:
                if aug in augmentor.augmentations:
                    transforms_list.append(augmentor.augmentations[aug])
        
        transform = transforms.Compose(transforms_list) if transforms_list else None
        
        dataset = CustomDataset(data, labels, transform, 'image')
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
    
    @staticmethod
    def create_text_loader(data, labels, batch_size=32, shuffle=True, num_workers=4,
                          augmentations: Optional[List[str]] = None):
        """创建文本数据加载器"""
        transforms_list = []
        
        if augmentations:
            augmentor = DataAugmentation('text')
            for aug in augmentations:
                if aug in augmentor.augmentations:
                    transforms_list.append(augmentor.augmentations[aug])
        
        transform = transforms.Compose(transforms_list) if transforms_list else None
        
        dataset = CustomDataset(data, labels, transform, 'text')
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers) 