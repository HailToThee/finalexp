import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import os
from typing import Dict, Any, Optional

class Trainer:
    """
    AI模型训练器
    任务书要求：支持用户自定义学习率、批次大小、最大迭代次数、工作进程数等参数
    """
    
    def __init__(self, 
                 model: nn.Module,
                 train_dataset,
                 val_dataset=None,
                 learning_rate: float = 0.001,
                 batch_size: int = 32,
                 max_epochs: int = 600,
                 workers: int = 4,
                 device = torch.device ('cuda' if torch.cuda.is_available () else 'cpu'),
                 log_dir: str = './logs'):
        """
        初始化训练器
        Args:
            model: 待训练的模型
            train_dataset: 训练数据集
            val_dataset: 验证数据集
            learning_rate: 学习率（任务书示例：0.001~0.1）
            batch_size: 批次大小（任务书示例：16、32、64）
            max_epochs: 最大迭代次数（任务书示例：600）
            workers: 工作进程数（任务书示例：4）
            device: 训练设备
            log_dir: 日志目录
        """
        self.model = model.to(device)
        self.device = device
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.workers = workers
        self.log_dir = log_dir
        
        # 数据加载器
        self.train_loader = DataLoader(
            train_dataset, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=workers
        )
        
        if val_dataset:
            self.val_loader = DataLoader(
                val_dataset, 
                batch_size=batch_size, 
                shuffle=False, 
                num_workers=workers
            )
        else:
            self.val_loader = None
        
        # 优化器和损失函数
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        
        # TensorBoard日志
        os.makedirs(log_dir, exist_ok=True)
        self.writer = SummaryWriter(log_dir)
        
        # 训练历史
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
    
    def train(self):
        """
        执行训练
        任务书要求：集成TensorBoard/MindInsight，实时可视化损失函数、准确率等指标
        """
        print(f"开始训练，参数配置：")
        print(f"  学习率: {self.learning_rate}")
        print(f"  批次大小: {self.batch_size}")
        print(f"  最大轮次: {self.max_epochs}")
        print(f"  工作进程: {self.workers}")
        
        for epoch in range(self.max_epochs):
            # 训练阶段
            train_loss, train_acc = self._train_epoch()
            
            # 验证阶段
            if self.val_loader:
                val_loss, val_acc = self._validate_epoch()
            else:
                val_loss, val_acc = 0.0, 0.0
            
            # 记录历史
            self.train_losses.append(train_loss)
            self.train_accuracies.append(train_acc)
            if self.val_loader:
                self.val_losses.append(val_loss)
                self.val_accuracies.append(val_acc)
            
            # TensorBoard记录
            self.writer.add_scalar('Loss/Train', train_loss, epoch)
            self.writer.add_scalar('Accuracy/Train', train_acc, epoch)
            if self.val_loader:
                self.writer.add_scalar('Loss/Validation', val_loss, epoch)
                self.writer.add_scalar('Accuracy/Validation', val_acc, epoch)
            
            # 打印进度
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{self.max_epochs}")
                print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
                if self.val_loader:
                    print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        
        self.writer.close()
        print("训练完成！")
    
    def _train_epoch(self):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = correct / total
        return avg_loss, accuracy
    
    def _validate_epoch(self):
        """验证一个epoch"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in self.val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.criterion(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = correct / total
        return avg_loss, accuracy
    
    def save_model(self, path: str):
        """保存模型"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epoch': self.max_epochs,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies,
            'config': {
                'learning_rate': self.learning_rate,
                'batch_size': self.batch_size,
                'max_epochs': self.max_epochs,
                'workers': self.workers
            }
        }, path)
    
    def load_model(self, path: str):
        """加载模型"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        return checkpoint

def train(model, dataloader, optimizer, loss_fn, device='cpu', epochs=10):
    """
    兼容性函数，保持原有接口
    """
    trainer = Trainer(
        model=model,
        train_dataset=dataloader.dataset,
        learning_rate=optimizer.param_groups[0]['lr'],
        batch_size=dataloader.batch_size,
        max_epochs=epochs,
        device=device
    )
    trainer.train() 