import optuna
import itertools
import random
from typing import Dict, List, Any, Callable
import numpy as np

class HyperparameterOptimizer:
    """
    超参数调优器
    任务书要求：支持用户定义搜索空间，支持网格搜索、随机搜索等算法
    """
    
    def __init__(self, search_method='optuna'):
        """
        Args:
            search_method: 搜索方法 ('optuna', 'grid', 'random')
        """
        self.search_method = search_method
    
    def optimize(self, 
                train_func: Callable, 
                param_space: Dict[str, Any], 
                n_trials: int = 20,
                direction: str = 'minimize'):
        """
        执行超参数优化
        Args:
            train_func: 训练函数
            param_space: 参数搜索空间（任务书示例：BATCH_SIZE=[16,32], WORKERS=[2,4]）
            n_trials: 试验次数
            direction: 优化方向
        Returns:
            best_params: 最佳参数
            best_score: 最佳分数
        """
        if self.search_method == 'optuna':
            return self._optuna_optimize(train_func, param_space, n_trials, direction)
        elif self.search_method == 'grid':
            return self._grid_search(train_func, param_space)
        elif self.search_method == 'random':
            return self._random_search(train_func, param_space, n_trials)
        else:
            raise ValueError(f"不支持的搜索方法: {self.search_method}")
    
    def _optuna_optimize(self, train_func, param_space, n_trials, direction):
        """使用Optuna进行优化"""
        def objective(trial):
            params = {}
            for param_name, param_config in param_space.items():
                if isinstance(param_config, list):
                    # 分类参数
                    params[param_name] = trial.suggest_categorical(param_name, param_config)
                elif isinstance(param_config, tuple) and len(param_config) == 2:
                    # 连续参数
                    if isinstance(param_config[0], int):
                        params[param_name] = trial.suggest_int(param_name, param_config[0], param_config[1])
                    else:
                        params[param_name] = trial.suggest_float(param_name, param_config[0], param_config[1])
                else:
                    raise ValueError(f"不支持的参数配置: {param_config}")
            
            return train_func(**params)
        
        study = optuna.create_study(direction=direction)
        study.optimize(objective, n_trials=n_trials)
        
        print("最佳参数:", study.best_params)
        print("最佳分数:", study.best_value)
        
        return study.best_params, study.best_value
    
    def _grid_search(self, train_func, param_space):
        """网格搜索"""
        # 生成所有参数组合
        param_names = list(param_space.keys())
        param_values = list(param_space.values())
        
        best_params = None
        best_score = float('inf')
        results = []
        
        for param_combination in itertools.product(*param_values):
            params = dict(zip(param_names, param_combination))
            try:
                score = train_func(**params)
                results.append((params, score))
                
                if score < best_score:
                    best_score = score
                    best_params = params
                    
                print(f"参数: {params}, 分数: {score}")
            except Exception as e:
                print(f"参数 {params} 训练失败: {e}")
        
        print("网格搜索完成")
        print("最佳参数:", best_params)
        print("最佳分数:", best_score)
        
        return best_params, best_score
    
    def _random_search(self, train_func, param_space, n_trials):
        """随机搜索"""
        best_params = None
        best_score = float('inf')
        results = []
        
        for trial in range(n_trials):
            params = {}
            for param_name, param_config in param_space.items():
                if isinstance(param_config, list):
                    # 从列表中随机选择
                    params[param_name] = random.choice(param_config)
                elif isinstance(param_config, tuple) and len(param_config) == 2:
                    # 在范围内随机选择
                    if isinstance(param_config[0], int):
                        params[param_name] = random.randint(param_config[0], param_config[1])
                    else:
                        params[param_name] = random.uniform(param_config[0], param_config[1])
                else:
                    raise ValueError(f"不支持的参数配置: {param_config}")
            
            try:
                score = train_func(**params)
                results.append((params, score))
                
                if score < best_score:
                    best_score = score
                    best_params = params
                    
                print(f"试验 {trial+1}/{n_trials}: 参数 {params}, 分数 {score}")
            except Exception as e:
                print(f"试验 {trial+1} 失败: {e}")
        
        print("随机搜索完成")
        print("最佳参数:", best_params)
        print("最佳分数:", best_score)
        
        return best_params, best_score

def objective(trial, train_func, param_space):
    """
    兼容性函数，保持原有接口
    """
    params = {k: trial.suggest_float(k, *v) if isinstance(v, tuple) else trial.suggest_categorical(k, v)
              for k, v in param_space.items()}
    return train_func(**params)

def run_optuna(train_func, param_space, n_trials=20):
    """
    兼容性函数，保持原有接口
    """
    optimizer = HyperparameterOptimizer(search_method='optuna')
    best_params, _ = optimizer.optimize(train_func, param_space, n_trials)
    return best_params 