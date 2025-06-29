import torch
import torch.nn as nn
import numpy as np

class PGDAttack:
    """
    Projected Gradient Descent (PGD) 攻击实现
    任务书定位：迭代式强对抗样本生成算法，支持L∞约束（任务书提及"扰动约束"相关概念）
    核心参数：
        - 迭代次数：任务书要求"多次迭代生成对抗样本"，需支持用户配置（如5~100次）
        - 投影约束：严格遵循L∞范数约束，确保扰动在预设范围内
    """
    
    def __init__(self, epsilon=0.3, alpha=0.01, iters=40, loss_fn=None):
        """
        Args:
            epsilon: 扰动上限（L∞约束）
            alpha: 每步步长
            iters: 迭代次数（任务书要求支持5~100次配置）
            loss_fn: 损失函数
        """
        self.epsilon = epsilon
        self.alpha = alpha
        self.iters = iters
        self.loss_fn = loss_fn if loss_fn is not None else nn.CrossEntropyLoss()
    
    def attack(self, model, images, labels):
        """
        执行PGD攻击
        Args:
            model: 被攻击的模型
            images: 输入图片
            labels: 正确标签
        Returns:
            adv_images: 对抗样本
        """
        ori_images = images.clone().detach()
        adv_images = ori_images.clone().detach()
        
        # 随机初始化扰动
        adv_images = adv_images + torch.rand_like(adv_images) * 2 * self.epsilon - self.epsilon
        adv_images = torch.clamp(adv_images, 0, 1)
        
        for i in range(self.iters):
            adv_images.requires_grad = True
            outputs = model(adv_images)
            loss = self.loss_fn(outputs, labels)
            
            model.zero_grad()
            loss.backward()
            grad = adv_images.grad.data
            
            # 梯度更新
            adv_images = adv_images + self.alpha * grad.sign()
            
            # L∞投影约束
            eta = torch.clamp(adv_images - ori_images, min=-self.epsilon, max=self.epsilon)
            adv_images = torch.clamp(ori_images + eta, 0, 1).detach()
        
        return adv_images
    
    def set_iters(self, iters):
        """设置迭代次数"""
        self.iters = iters
    
    def set_epsilon(self, epsilon):
        """设置扰动上限"""
        self.epsilon = epsilon

def pgd_attack(model, images, labels, epsilon=0.3, alpha=0.01, iters=40, loss_fn=None):
    """
    兼容性函数，保持原有接口
    """
    attacker = PGDAttack(epsilon=epsilon, alpha=alpha, iters=iters, loss_fn=loss_fn)
    return attacker.attack(model, images, labels) 