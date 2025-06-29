import torch
import torch.nn as nn
import numpy as np

class CWAttack:
    """
    Carlini & Wagner (C&W) 攻击实现
    任务书定位：针对图像分类模型的经典攻击算法，支持目标导向攻击
    """
    
    def __init__(self, c=1e-4, kappa=0, iters=1000, lr=0.01, targeted=False):
        """
        Args:
            c: 置信度参数
            kappa: 置信度阈值
            iters: 优化迭代次数
            lr: 学习率
            targeted: 是否为目标攻击
        """
        self.c = c
        self.kappa = kappa
        self.iters = iters
        self.lr = lr
        self.targeted = targeted
    
    def attack(self, model, images, labels, target_labels=None):
        """
        执行C&W攻击
        Args:
            model: 被攻击的模型
            images: 输入图片
            labels: 正确标签
            target_labels: 目标标签（目标攻击时使用）
        Returns:
            adv_images: 对抗样本
        """
        device = images.device
        images = images.clone().detach().to(device)
        labels = labels.to(device)
        
        if self.targeted and target_labels is None:
            raise ValueError("目标攻击需要提供target_labels")
        
        batch_size = images.size(0)
        
        # 使用tanh变换确保图像在[0,1]范围内
        w = torch.atanh((images * 1.999999 - 1)).detach()
        w = w.clone().detach().requires_grad_(True)
        
        optimizer = torch.optim.Adam([w], lr=self.lr)
        one_hot_labels = torch.eye(model(images).size(1))[labels].to(device)
        
        if self.targeted:
            target_one_hot = torch.eye(model(images).size(1))[target_labels].to(device)
        
        def f(x):
            outputs = model(x)
            if self.targeted:
                # 目标攻击：最大化目标类别的置信度
                real = (target_one_hot * outputs).sum(1)
                other = ((1 - target_one_hot) * outputs - target_one_hot * 10000).max(1)[0]
                return torch.clamp(other - real + self.kappa, min=0)
            else:
                # 非目标攻击：最小化正确类别的置信度
                real = (one_hot_labels * outputs).sum(1)
                other = ((1 - one_hot_labels) * outputs - one_hot_labels * 10000).max(1)[0]
                return torch.clamp(real - other + self.kappa, min=0)
        
        for step in range(self.iters):
            adv_images = torch.tanh(w) * 0.5 + 0.5
            l2_loss = ((adv_images - images) ** 2).view(batch_size, -1).sum(1)
            f_loss = self.c * f(adv_images)
            loss = l2_loss.sum() + f_loss.sum()
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        adv_images = torch.tanh(w) * 0.5 + 0.5
        return adv_images.detach()
    
    def set_targeted(self, targeted):
        """设置攻击类型"""
        self.targeted = targeted

def cw_attack(model, images, labels, c=1e-4, kappa=0, iters=1000, lr=0.01):
    """
    兼容性函数，保持原有接口
    """
    attacker = CWAttack(c=c, kappa=kappa, iters=iters, lr=lr)
    return attacker.attack(model, images, labels) 