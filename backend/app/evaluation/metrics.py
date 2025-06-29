import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt

class SecurityEvaluator:
    """
    AI模型安全性评估器
    任务书要求：实现攻击成功率（ASR）、扰动幅度、鲁棒精度、对抗精度差距、迁移攻击成功率（TASR）等指标
    """
    
    def __init__(self):
        """初始化评估器"""
        pass
    
    def attack_success_rate(self, pred_clean: torch.Tensor, pred_adv: torch.Tensor, labels: torch.Tensor) -> float:
        """
        攻击成功率（ASR）
        任务书定位：对抗样本导致模型错误输出的比例（任务书"评估引擎"核心指标）
        Args:
            pred_clean: 原始样本预测结果
            pred_adv: 对抗样本预测结果
            labels: 真实标签
        Returns:
            ASR: 攻击成功率
        """
        clean_correct = (pred_clean == labels)
        adv_wrong = (pred_adv != labels)
        
        # 防止除零错误
        clean_correct_count = clean_correct.sum().item()
        if clean_correct_count == 0:
            return 0.0
        
        asr = (clean_correct & adv_wrong).sum().item() / clean_correct_count
        return asr
    
    def perturbation_magnitude(self, x: torch.Tensor, x_adv: torch.Tensor, norm: str = 'l2') -> float:
        """
        扰动幅度（L2/L∞范数）
        任务书定位：原始样本与对抗样本的差异（任务书"量化对抗样本威胁强度"）
        Args:
            x: 原始样本
            x_adv: 对抗样本
            norm: 范数类型 ('l2', 'linf')
        Returns:
            扰动幅度
        """
        if norm == 'l2':
            return torch.norm((x - x_adv).view(x.size(0), -1), p=2, dim=1).mean().item()
        elif norm == 'linf':
            return torch.norm((x - x_adv).view(x.size(0), -1), p=float('inf'), dim=1).mean().item()
        else:
            raise ValueError("不支持的范数类型")
    
    def robust_accuracy(self, pred_adv: torch.Tensor, labels: torch.Tensor) -> float:
        """
        鲁棒精度
        任务书定位：模型在对抗样本输入下的准确率（任务书"评估模型抵御能力"）
        Args:
            pred_adv: 对抗样本预测结果
            labels: 真实标签
        Returns:
            鲁棒精度
        """
        return (pred_adv == labels).float().mean().item()
    
    def adversarial_gap(self, acc_clean: float, acc_adv: float) -> float:
        """
        对抗精度差距
        任务书定位：干净样本精度与对抗样本精度的差值（任务书"模型安全性能对比"）
        Args:
            acc_clean: 干净样本准确率
            acc_adv: 对抗样本准确率
        Returns:
            对抗精度差距
        """
        return acc_clean - acc_adv
    
    def transfer_attack_success_rate(self, 
                                   pred_clean: torch.Tensor, 
                                   pred_adv_source: torch.Tensor,
                                   pred_adv_target: torch.Tensor, 
                                   labels: torch.Tensor) -> float:
        """
        迁移攻击成功率（TASR）
        任务书定位：对抗样本在不同模型间的攻击效果（任务书"跨模型漏洞评估"）
        Args:
            pred_clean: 原始样本预测结果
            pred_adv_source: 源模型对抗样本预测结果
            pred_adv_target: 目标模型对抗样本预测结果
            labels: 真实标签
        Returns:
            TASR: 迁移攻击成功率
        """
        # 源模型攻击成功
        source_success = (pred_clean == labels) & (pred_adv_source != labels)
        # 目标模型也被攻击成功
        target_success = (pred_adv_target != labels)
        # 迁移攻击成功率
        source_success_count = source_success.sum().item()
        if source_success_count == 0:
            return 0.0
        
        tasr = (source_success & target_success).sum().item() / source_success_count
        return tasr
    
    def comprehensive_evaluation(self, 
                               model, 
                               clean_data: torch.Tensor, 
                               adv_data: torch.Tensor, 
                               labels: torch.Tensor,
                               target_model=None) -> Dict[str, float]:
        """
        综合安全性评估
        任务书定位：自动化流程"对抗样本生成→模型推理→指标计算→报告生成"闭环
        Args:
            model: 被评估模型
            clean_data: 干净样本
            adv_data: 对抗样本
            labels: 真实标签
            target_model: 目标模型（用于迁移攻击评估）
        Returns:
            评估结果字典
        """
        model.eval()
        
        with torch.no_grad():
            # 模型推理
            pred_clean = model(clean_data).argmax(dim=1)
            pred_adv = model(adv_data).argmax(dim=1)
            
            # 计算各项指标
            asr = self.attack_success_rate(pred_clean, pred_adv, labels)
            pert_l2 = self.perturbation_magnitude(clean_data, adv_data, 'l2')
            pert_linf = self.perturbation_magnitude(clean_data, adv_data, 'linf')
            robust_acc = self.robust_accuracy(pred_adv, labels)
            clean_acc = (pred_clean == labels).float().mean().item()
            adv_gap = self.adversarial_gap(clean_acc, robust_acc)
            
            results = {
                'attack_success_rate': asr,
                'perturbation_l2': pert_l2,
                'perturbation_linf': pert_linf,
                'robust_accuracy': robust_acc,
                'clean_accuracy': clean_acc,
                'adversarial_gap': adv_gap
            }
            
            # 迁移攻击评估
            if target_model is not None:
                target_model.eval()
                with torch.no_grad():
                    pred_adv_target = target_model(adv_data).argmax(dim=1)
                    tasr = self.transfer_attack_success_rate(pred_clean, pred_adv, pred_adv_target, labels)
                    results['transfer_attack_success_rate'] = tasr
        
        return results
    
    def visualize_results(self, 
                         results: Dict[str, float], 
                         save_path: Optional[str] = None):
        """
        可视化评估结果
        任务书要求：生成评估曲线、原始样本与对抗样本的预测结果对比图
        Args:
            results: 评估结果
            save_path: 保存路径
        """
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 准确率对比
        axes[0, 0].bar(['Clean Accuracy', 'Robust Accuracy'], 
                      [results['clean_accuracy'], results['robust_accuracy']])
        axes[0, 0].set_title('Accuracy Comparison')
        axes[0, 0].set_ylabel('Accuracy')
        
        # 攻击成功率
        axes[0, 1].bar(['Attack Success Rate'], [results['attack_success_rate']])
        axes[0, 1].set_title('Attack Success Rate')
        axes[0, 1].set_ylabel('Success Rate')
        
        # 扰动幅度
        axes[1, 0].bar(['L2 Norm', 'L∞ Norm'], 
                      [results['perturbation_l2'], results['perturbation_linf']])
        axes[1, 0].set_title('Perturbation Magnitude')
        axes[1, 0].set_ylabel('Magnitude')
        
        # 对抗精度差距
        axes[1, 1].bar(['Adversarial Gap'], [results['adversarial_gap']])
        axes[1, 1].set_title('Adversarial Gap')
        axes[1, 1].set_ylabel('Gap')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

# 兼容性函数
def attack_success_rate(pred_clean, pred_adv, labels):
    """兼容性函数"""
    evaluator = SecurityEvaluator()
    return evaluator.attack_success_rate(pred_clean, pred_adv, labels)

def perturbation_magnitude(x, x_adv, norm='l2'):
    """兼容性函数"""
    evaluator = SecurityEvaluator()
    return evaluator.perturbation_magnitude(x, x_adv, norm)

def robust_accuracy(pred_adv, labels):
    """兼容性函数"""
    evaluator = SecurityEvaluator()
    return evaluator.robust_accuracy(pred_adv, labels)

def adversarial_gap(acc_clean, acc_adv):
    """兼容性函数"""
    evaluator = SecurityEvaluator()
    return evaluator.adversarial_gap(acc_clean, acc_adv) 