class AttackBase:
    def __init__(self, model):
        self.model = model

    def generate(self, inputs, labels, **kwargs):
        raise NotImplementedError("子类需实现 generate 方法") 