import torch
import torch.nn as nn
import numpy as np

class FGSMAttack:
    """
    Fast Gradient Sign Method (FGSM) 攻击实现
    任务书定位：基础白盒攻击算法，基于单步梯度优化
    核心参数：扰动强度（对应任务书中"微小输入扰动"）
    适用模型：针对CNN类图像分类模型（如ResNet50、VGG16）
    """
    
    def __init__(self, epsilon=0.03, loss_fn=None):
        """
        Args:
            epsilon: 扰动强度，确保扰动"微小"（符合人类视觉不可察觉性）
            loss_fn: 损失函数（可选，默认交叉熵）
        """
        self.epsilon = epsilon
        self.loss_fn = loss_fn if loss_fn is not None else nn.CrossEntropyLoss()
    
    def attack(self, model, images, labels):
        """
        执行FGSM攻击
        Args:
            model: 被攻击的CNN模型（如ResNet50、VGG16）
            images: 输入图片 (batch, C, H, W)
            labels: 正确标签
        Returns:
            adv_images: 对抗样本
        """
        images = images.clone().detach().requires_grad_(True)
        
        # 前向传播
        outputs = model(images)
        loss = self.loss_fn(outputs, labels)
        
        # 反向传播
        model.zero_grad()
        loss.backward()
        grad = images.grad.data
        
        # 生成对抗样本
        adv_images = images + self.epsilon * grad.sign()
        adv_images = torch.clamp(adv_images, 0, 1)
        
        return adv_images.detach()
    
    def set_epsilon(self, epsilon):
        """设置扰动强度"""
        self.epsilon = epsilon

def fgsm_attack(model, images, labels, epsilon=0.03, loss_fn=None):
    """
    兼容性函数，保持原有接口
    """
    attacker = FGSMAttack(epsilon=epsilon, loss_fn=loss_fn)
    return attacker.attack(model, images, labels) 