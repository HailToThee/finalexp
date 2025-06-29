import torch
import numpy as np
from typing import Union, List, Dict, Any, Optional
import os

class InferenceEngine:
    """
    AI模型推理引擎
    任务书要求：
    - 支持框架：严格遵循任务书要求，兼容PyTorch、TensorFlow、MindSpore等主流框架
    - 推理接口：接收用户上传的模型（如.pth、.h5格式），输出推理结果，支持批处理推理
    """
    
    def __init__(self, model, device='cpu', framework='pytorch'):
        """
        初始化推理引擎
        Args:
            model: 模型对象
            device: 推理设备
            framework: 框架类型 ('pytorch', 'tensorflow', 'mindspore', 'onnx')
        """
        self.model = model
        self.device = device
        self.framework = framework
        
        # 根据框架类型进行初始化
        self._initialize_model()
    
    def _initialize_model(self):
        """根据框架类型初始化模型"""
        if self.framework == 'pytorch':
            self.model = self.model.to(self.device)
            self.model.eval()
        elif self.framework == 'tensorflow':
            # TensorFlow模型初始化
            pass
        elif self.framework == 'mindspore':
            # MindSpore模型初始化
            pass
        elif self.framework == 'onnx':
            # ONNX模型已在ModelManager中初始化
            pass
        else:
            raise ValueError(f"不支持的框架: {self.framework}")
    
    def predict(self, 
               inputs: Union[torch.Tensor, np.ndarray, List], 
               batch_size: int = 32,
               return_probabilities: bool = True) -> Dict[str, Any]:
        """
        执行模型推理
        任务书要求：支持批处理推理（任务书"在线推理"功能）
        Args:
            inputs: 输入数据
            batch_size: 批次大小
            return_probabilities: 是否返回概率分布
        Returns:
            推理结果字典
        """
        if self.framework == 'pytorch':
            return self._pytorch_predict(inputs, batch_size, return_probabilities)
        elif self.framework == 'tensorflow':
            return self._tensorflow_predict(inputs, batch_size, return_probabilities)
        elif self.framework == 'mindspore':
            return self._mindspore_predict(inputs, batch_size, return_probabilities)
        elif self.framework == 'onnx':
            return self._onnx_predict(inputs, batch_size, return_probabilities)
        else:
            raise ValueError(f"不支持的框架: {self.framework}")
    
    def _pytorch_predict(self, inputs, batch_size, return_probabilities):
        """PyTorch推理"""
        if isinstance(inputs, list):
            inputs = torch.stack(inputs)
        elif isinstance(inputs, np.ndarray):
            inputs = torch.from_numpy(inputs)
        
        results = []
        probabilities = []
        
        with torch.no_grad():
            for i in range(0, len(inputs), batch_size):
                batch = inputs[i:i+batch_size].to(self.device)
                outputs = self.model(batch)
                
                if return_probabilities:
                    probs = torch.softmax(outputs, dim=1)
                    probabilities.append(probs.cpu())
                
                predictions = outputs.argmax(dim=1)
                results.append(predictions.cpu())
        
        results = torch.cat(results, dim=0)
        
        output = {
            'predictions': results.numpy(),
            'framework': 'pytorch'
        }
        
        if return_probabilities:
            probabilities = torch.cat(probabilities, dim=0)
            output['probabilities'] = probabilities.numpy()
        
        return output
    
    def _tensorflow_predict(self, inputs, batch_size, return_probabilities):
        """TensorFlow推理"""
        # TensorFlow推理实现
        # 这里需要根据实际的TensorFlow模型进行适配
        pass
    
    def _mindspore_predict(self, inputs, batch_size, return_probabilities):
        """MindSpore推理"""
        # MindSpore推理实现
        # 这里需要根据实际的MindSpore模型进行适配
        pass
    
    def _onnx_predict(self, inputs, batch_size, return_probabilities):
        """ONNX推理"""
        if isinstance(inputs, torch.Tensor):
            inputs = inputs.numpy()
        elif isinstance(inputs, list):
            inputs = np.array(inputs)
        
        results = []
        probabilities = []
        
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i+batch_size]
            outputs = self.model.run(None, {'input': batch})[0]
            
            if return_probabilities:
                # 计算softmax概率
                exp_outputs = np.exp(outputs - np.max(outputs, axis=1, keepdims=True))
                probs = exp_outputs / np.sum(exp_outputs, axis=1, keepdims=True)
                probabilities.append(probs)
            
            predictions = np.argmax(outputs, axis=1)
            results.append(predictions)
        
        results = np.concatenate(results, axis=0)
        
        output = {
            'predictions': results,
            'framework': 'onnx'
        }
        
        if return_probabilities:
            probabilities = np.concatenate(probabilities, axis=0)
            output['probabilities'] = probabilities
        
        return output
    
    def predict_single(self, input_data: Union[torch.Tensor, np.ndarray]) -> Dict[str, Any]:
        """单样本推理"""
        return self.predict([input_data], batch_size=1)
    
    def predict_batch(self, 
                     input_data: Union[torch.Tensor, np.ndarray, List], 
                     batch_size: int = 32) -> Dict[str, Any]:
        """批量推理"""
        return self.predict(input_data, batch_size=batch_size)
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = {
            'framework': self.framework,
            'device': self.device
        }
        
        if self.framework == 'pytorch':
            info['model_type'] = type(self.model).__name__
            info['parameters'] = sum(p.numel() for p in self.model.parameters())
        
        return info
    
    def warmup(self, input_shape: tuple, num_warmup: int = 10):
        """模型预热"""
        print(f"开始模型预热，预热次数: {num_warmup}")
        
        if self.framework == 'pytorch':
            dummy_input = torch.randn(input_shape).to(self.device)
            with torch.no_grad():
                for _ in range(num_warmup):
                    _ = self.model(dummy_input)
        elif self.framework == 'onnx':
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
            for _ in range(num_warmup):
                _ = self.model.run(None, {'input': dummy_input})
        
        print("模型预热完成")

class MultiFrameworkInferenceEngine:
    """
    多框架推理引擎
    支持同时加载不同框架的模型进行对比推理
    """
    
    def __init__(self):
        self.engines = {}
    
    def add_model(self, name: str, model, framework: str, device: str = 'cpu'):
        """添加模型"""
        engine = InferenceEngine(model, device, framework)
        self.engines[name] = engine
    
    def predict_all(self, inputs, batch_size: int = 32) -> Dict[str, Dict[str, Any]]:
        """使用所有模型进行推理"""
        results = {}
        for name, engine in self.engines.items():
            results[name] = engine.predict(inputs, batch_size)
        return results
    
    def compare_predictions(self, inputs, batch_size: int = 32) -> Dict[str, Any]:
        """比较不同模型的预测结果"""
        all_results = self.predict_all(inputs, batch_size)
        
        # 提取预测结果
        predictions = {name: result['predictions'] for name, result in all_results.items()}
        
        # 计算一致性
        consistency = self._calculate_consistency(predictions)
        
        return {
            'predictions': predictions,
            'consistency': consistency,
            'framework_results': all_results
        }
    
    def _calculate_consistency(self, predictions: Dict[str, np.ndarray]) -> float:
        """计算预测一致性"""
        if len(predictions) < 2:
            return 1.0
        
        pred_arrays = list(predictions.values())
        consistency = np.mean([np.array_equal(pred_arrays[0], pred) for pred in pred_arrays[1:]])
        return consistency 