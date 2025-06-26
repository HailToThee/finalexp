def deepwordbug_attack(model, texts, labels=None, **kwargs):
    """
    DeepWordBug攻击（需安装textattack库）
    """
    from textattack.attack_recipes import DeepWordBugGao2018
    from textattack.models.wrappers import PyTorchModelWrapper
    from textattack.datasets import Dataset

    model_wrapper = PyTorchModelWrapper(model, tokenizer=lambda x: x.split())
    attack = DeepWordBugGao2018.build(model_wrapper)
    dataset = [(text, label) for text, label in zip(texts, labels)]
    adv_texts = []
    for result in attack.attack_dataset(Dataset(dataset)):
        adv_texts.append(result.perturbed_text())
    return adv_texts 