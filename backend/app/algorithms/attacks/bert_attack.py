import torch
import numpy as np
from typing import List, Optional

class BERTAttack:
    """
    BERT-Attack实现
    任务书定位：针对BERT等预训练模型的上下文感知攻击算法，用于命名实体识别（NER）等任务
    """
    
    def __init__(self, tokenizer=None, max_perturbations=3, mask_prob=0.15):
        """
        Args:
            tokenizer: BERT分词器
            max_perturbations: 最大扰动数量
            mask_prob: 掩码概率
        """
        self.tokenizer = tokenizer
        self.max_perturbations = max_perturbations
        self.mask_prob = mask_prob
    
    def attack(self, model, texts, labels=None):
        """
        执行BERT-Attack
        Args:
            model: BERT模型
            texts: 输入文本列表
            labels: 标签列表
        Returns:
            adv_texts: 对抗文本列表
        """
        adv_texts = []
        
        for i, text in enumerate(texts):
            label = labels[i] if labels is not None else None
            
            # 分词
            if self.tokenizer:
                tokens = self.tokenizer.tokenize(text)
            else:
                tokens = text.split()
            
            # 生成对抗文本
            adv_text = self._generate_adversarial_text(model, tokens, label)
            adv_texts.append(adv_text)
        
        return adv_texts
    
    def _generate_adversarial_text(self, model, tokens, label):
        """生成对抗文本"""
        adv_tokens = tokens.copy()
        perturbations = 0
        
        for i, token in enumerate(tokens):
            if perturbations >= self.max_perturbations:
                break
            
            # 计算token重要性
            importance = self._calculate_token_importance(model, tokens, i, label)
            
            if importance > 0.5:  # 重要性阈值
                # 尝试替换或删除
                if torch.rand(1).item() < self.mask_prob:
                    adv_tokens[i] = '[MASK]'
                    perturbations += 1
        
        return ' '.join(adv_tokens)
    
    def _calculate_token_importance(self, model, tokens, token_idx, label):
        """计算token重要性（简化实现）"""
        # 简化实现：返回随机重要性分数
        return torch.rand(1).item()

def bert_attack(model, texts, labels=None, **kwargs):
    """
    兼容性函数，保持原有接口
    """
    attacker = BERTAttack(**kwargs)
    return attacker.attack(model, texts, labels) 