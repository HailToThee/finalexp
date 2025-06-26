import torch
import os
import json
import onnx
import onnxruntime
from typing import Dict, Any, Optional, List
from datetime import datetime

class ModelManager:
    """
    AI模型管理器
    任务书要求：
    - 模型格式：支持ONNX标准格式导入导出（任务书"模型导入"功能）
    - 版本控制：记录模型训练参数、评估结果，支持版本追溯（任务书"模型库模块"）
    """
    
    def __init__(self, model_dir: str):
        """
        初始化模型管理器
        Args:
            model_dir: 模型存储目录
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # 创建版本控制文件
        self.version_file = os.path.join(model_dir, 'model_versions.json')
        self._load_versions()
    
    def _load_versions(self):
        """加载版本信息"""
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r', encoding='utf-8') as f:
                self.versions = json.load(f)
        else:
            self.versions = {}
    
    def _save_versions(self):
        """保存版本信息"""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(self.versions, f, indent=2, ensure_ascii=False)
    
    def save_model(self, 
                  model: torch.nn.Module, 
                  name: str, 
                  training_config: Optional[Dict[str, Any]] = None,
                  evaluation_results: Optional[Dict[str, float]] = None,
                  export_onnx: bool = True) -> str:
        """
        保存模型
        任务书要求：记录模型训练参数（如BATCH_SIZE、MAX_EPOCHS）、评估结果（如ASR、鲁棒精度）
        Args:
            model: PyTorch模型
            name: 模型名称
            training_config: 训练配置参数
            evaluation_results: 评估结果
            export_onnx: 是否同时导出ONNX格式
        Returns:
            模型保存路径
        """
        # 生成版本号
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"{name}_v{timestamp}"
        
        # 创建版本目录
        version_dir = os.path.join(self.model_dir, version)
        os.makedirs(version_dir, exist_ok=True)
        
        # 保存PyTorch模型
        torch_path = os.path.join(version_dir, f"{name}.pth")
        torch.save({
            'model_state_dict': model.state_dict(),
            'model_config': {
                'name': name,
                'version': version,
                'timestamp': timestamp
            }
        }, torch_path)
        
        # 导出ONNX格式（任务书要求）
        onnx_path = None
        if export_onnx:
            try:
                onnx_path = os.path.join(version_dir, f"{name}.onnx")
                self._export_to_onnx(model, onnx_path)
            except Exception as e:
                print(f"ONNX导出失败: {e}")
                onnx_path = None
        
        # 记录版本信息
        version_info = {
            'name': name,
            'version': version,
            'timestamp': timestamp,
            'torch_path': torch_path,
            'onnx_path': onnx_path,
            'training_config': training_config or {},
            'evaluation_results': evaluation_results or {}
        }
        
        self.versions[version] = version_info
        self._save_versions()
        
        print(f"模型已保存: {version}")
        print(f"  PyTorch路径: {torch_path}")
        if onnx_path:
            print(f"  ONNX路径: {onnx_path}")
        
        return torch_path
    
    def _export_to_onnx(self, model: torch.nn.Module, onnx_path: str):
        """导出ONNX格式"""
        model.eval()
        
        # 创建示例输入（需要根据实际模型调整）
        dummy_input = torch.randn(1, 3, 224, 224)  # 假设是图像分类模型
        
        # 导出ONNX
        torch.onnx.export(
            model,
            dummy_input,
            onnx_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        # 验证ONNX模型
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
    
    def load_model(self, 
                  model_class: torch.nn.Module, 
                  name: str, 
                  version: Optional[str] = None,
                  device: str = 'cpu',
                  use_onnx: bool = False) -> torch.nn.Module:
        """
        加载模型
        Args:
            model_class: 模型类
            name: 模型名称
            version: 版本号（如果为None，加载最新版本）
            device: 设备
            use_onnx: 是否使用ONNX格式
        Returns:
            加载的模型
        """
        if version is None:
            # 加载最新版本
            versions = [v for v in self.versions.keys() if v.startswith(name)]
            if not versions:
                raise ValueError(f"未找到模型: {name}")
            version = sorted(versions)[-1]
        
        if version not in self.versions:
            raise ValueError(f"未找到版本: {version}")
        
        version_info = self.versions[version]
        
        if use_onnx and version_info.get('onnx_path') and os.path.exists(version_info['onnx_path']):
            # 使用ONNX模型
            return self._load_onnx_model(version_info['onnx_path'])
        else:
            # 使用PyTorch模型
            if not os.path.exists(version_info['torch_path']):
                raise FileNotFoundError(f"模型文件不存在: {version_info['torch_path']}")
            
            model = model_class().to(device)
            checkpoint = torch.load(version_info['torch_path'], map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            return model
    
    def _load_onnx_model(self, onnx_path: str):
        """加载ONNX模型"""
        if not os.path.exists(onnx_path):
            raise FileNotFoundError(f"ONNX文件不存在: {onnx_path}")
        
        session = onnxruntime.InferenceSession(onnx_path)
        return session
    
    def list_models(self) -> List[str]:
        """列出所有模型"""
        return list(set([self.versions[v]['name'] for v in self.versions.keys()]))
    
    def list_versions(self, name: str) -> List[Dict[str, Any]]:
        """列出指定模型的所有版本"""
        versions = []
        for version, info in self.versions.items():
            if info['name'] == name:
                versions.append({
                    'version': version,
                    'timestamp': info['timestamp'],
                    'training_config': info['training_config'],
                    'evaluation_results': info['evaluation_results']
                })
        return sorted(versions, key=lambda x: x['timestamp'], reverse=True)
    
    def get_model_info(self, version: str) -> Dict[str, Any]:
        """获取模型详细信息"""
        if version not in self.versions:
            raise ValueError(f"未找到版本: {version}")
        return self.versions[version]
    
    def delete_model(self, version: str):
        """删除模型版本"""
        if version not in self.versions:
            raise ValueError(f"未找到版本: {version}")
        
        version_info = self.versions[version]
        
        # 删除文件
        if os.path.exists(version_info['torch_path']):
            os.remove(version_info['torch_path'])
        
        if version_info.get('onnx_path') and os.path.exists(version_info['onnx_path']):
            os.remove(version_info['onnx_path'])
        
        # 删除版本目录
        version_dir = os.path.dirname(version_info['torch_path'])
        if os.path.exists(version_dir) and not os.listdir(version_dir):
            os.rmdir(version_dir)
        
        # 从版本记录中删除
        del self.versions[version]
        self._save_versions()
        
        print(f"已删除模型版本: {version}")
    
    def compare_models(self, versions: List[str]) -> Dict[str, Any]:
        """比较多个模型版本"""
        if len(versions) < 2:
            raise ValueError("至少需要两个版本进行比较")
        
        comparison = {
            'versions': versions,
            'training_configs': {},
            'evaluation_results': {}
        }
        
        for version in versions:
            if version not in self.versions:
                raise ValueError(f"未找到版本: {version}")
            
            info = self.versions[version]
            comparison['training_configs'][version] = info['training_config']
            comparison['evaluation_results'][version] = info['evaluation_results']
        
        return comparison 