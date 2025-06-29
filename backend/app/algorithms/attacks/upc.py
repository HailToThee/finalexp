import torch

def upc_attack(model, images, targets, iters=10, alpha=0.01, device='cpu'):
    """
    UPC攻击实现（适用于Faster R-CNN等目标检测模型）
    Args:
        model: 目标检测模型
        images: 输入图片 (batch, C, H, W)
        targets: 目标检测标签（list[dict]，与torchvision格式一致）
        iters: 迭代次数
        alpha: 步长
        device: 设备
    Returns:
        adv_images: 对抗样本
    """
    model.eval()
    adv_images = images.clone().detach().to(device)
    perturbation = torch.zeros_like(adv_images).to(device)

    for i in range(iters):
        adv_images = (images + perturbation).clone().detach().to(device)
        adv_images.requires_grad = True
        loss_dict = model(adv_images, targets)
        loss = sum(loss for loss in loss_dict.values())
        model.zero_grad()
        loss.backward()
        grad = adv_images.grad.data
        perturbation = perturbation + alpha * grad.sign()
        perturbation = torch.clamp(perturbation, -0.3, 0.3)  # 限制扰动幅度
    adv_images = torch.clamp(images + perturbation, 0, 1).detach()
    return adv_images 