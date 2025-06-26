import torch

def deepfool_attack(model, images, labels=None, max_iter=50, overshoot=0.02, num_classes=10):
    """
    DeepFool攻击实现
    """
    device = images.device
    images = images.clone().detach().to(device)
    adv_images = images.clone().detach()
    adv_images.requires_grad = True
    batch_size = images.size(0)
    for b in range(batch_size):
        image = images[b:b+1].clone().detach()
        image.requires_grad = True
        output = model(image)
        _, label = torch.max(output.data, 1)
        if labels is not None:
            label = labels[b:b+1]
        pert_image = image.clone().detach()
        r_tot = torch.zeros_like(image)
        loop_i = 0
        x = pert_image.clone().detach().requires_grad_(True)
        while loop_i < max_iter:
            outputs = model(x)
            fs = outputs.data.cpu().numpy().flatten()
            k_i = label.item()
            grad_orig = torch.autograd.grad(outputs[0, k_i], x, retain_graph=True)[0]
            min_val = float('inf')
            ri = None
            for k in range(num_classes):
                if k == k_i:
                    continue
                grad_curr = torch.autograd.grad(outputs[0, k], x, retain_graph=True)[0]
                w_k = grad_curr - grad_orig
                f_k = (outputs[0, k] - outputs[0, k_i]).data.cpu().numpy()
                pert_k = abs(f_k) / (w_k.norm() + 1e-8)
                if pert_k < min_val:
                    min_val = pert_k
                    ri = w_k * pert_k / (w_k.norm() + 1e-8)
            r_tot = r_tot + ri
            x = (image + (1 + overshoot) * r_tot).clone().detach().requires_grad_(True)
            output = model(x)
            k_i_new = output.data.max(1)[1].item()
            if k_i_new != k_i:
                break
            loop_i += 1
        adv_images[b:b+1] = x.detach()
    return torch.clamp(adv_images, 0, 1) 