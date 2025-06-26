import torch

def dag_attack(model, images, targets, iters=10, alpha=0.01, device='cpu'):
    """
    DAG攻击实现（适用于Faster R-CNN等目标检测模型）
    Args:
        model: 目标检测模型（如torchvision.models.detection.fasterrcnn_resnet50_fpn）
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
    adv_images.requires_grad = True

    for i in range(iters):
        adv_images.requires_grad = True
        # 目标检测模型的损失计算
        loss_dict = model(adv_images, targets)
        loss = sum(loss for loss in loss_dict.values())
        model.zero_grad()
        loss.backward()
        grad = adv_images.grad.data
        adv_images = adv_images + alpha * grad.sign()
        adv_images = torch.clamp(adv_images, 0, 1).detach()
        adv_images.requires_grad = True
    return adv_images.detach() 