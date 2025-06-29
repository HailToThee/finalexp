import torch
import torch.nn as nn

def bim_attack(model, images, labels, epsilon, alpha, iters, loss_fn=None):
    """
    Basic Iterative Method (BIM) 攻击实现
    Args:
        model: 被攻击的模型
        images: 输入图片
        labels: 正确标签
        epsilon: 扰动上限
        alpha: 每步步长
        iters: 迭代次数
        loss_fn: 损失函数
    Returns:
        adv_images: 对抗样本
    """
    ori_images = images.clone().detach()
    adv_images = ori_images.clone().detach()
    if loss_fn is None:
        loss_fn = nn.CrossEntropyLoss()
    for i in range(iters):
        adv_images.requires_grad = True
        outputs = model(adv_images)
        loss = loss_fn(outputs, labels)
        model.zero_grad()
        loss.backward()
        grad = adv_images.grad.data
        adv_images = adv_images + alpha * grad.sign()
        eta = torch.clamp(adv_images - ori_images, min=-epsilon, max=epsilon)
        adv_images = torch.clamp(ori_images + eta, 0, 1).detach()
    return adv_images 