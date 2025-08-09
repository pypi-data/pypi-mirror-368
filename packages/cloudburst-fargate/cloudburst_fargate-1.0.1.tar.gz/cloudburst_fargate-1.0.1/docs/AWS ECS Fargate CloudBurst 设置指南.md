# AWS ECS Fargate CloudBurst 设置指南

## 🎯 为什么选择 ECS Fargate？

从AWS提供的三个选项来看：

| 服务 | 复杂度 | GPU支持 | 成本 | 适合CloudBurst? |
|------|--------|---------|------|----------------|
| **EKS** | 很高 ❌ | ✅ | 高 | ❌ 过于复杂 |
| **Batch** | 中等 🟡 | ✅ | 中等 | 🤔 如果需要GPU |
| **ECS** | 低 ✅ | ❌ (CPU only) | 低 | ✅ **最佳选择** |

## 🚀 ECS Fargate 实际操作步骤

### 第一步：通过AWS控制台创建基础设施

#### 1. 创建ECS集群
```bash
# 在AWS控制台中：
1. 进入 ECS 服务页面
2. 点击 "Clusters" → "Create Cluster"
3. 选择 "Networking only (Fargate)" 
4. 集群名称输入: cloudburst-cluster
5. 点击 "Create"
```

#### 2. 准备你的Docker镜像
```dockerfile
# 修改你现有的Dockerfile
FROM python:3.11-slim

# 安装CloudBurst依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 安装AWS CLI (用于上传结果)
RUN pip install boto3 awscli

# 复制你的CloudBurst代码
COPY . /app
WORKDIR /app

# 创建入口脚本
COPY fargate_processor.py /app/
RUN chmod +x /app/fargate_processor.py

# 设置入口点
CMD ["python", "/app/fargate_processor.py"]
```

#### 3. 创建ECR仓库并推送镜像
```bash
# 在终端中执行：

# 1. 创建ECR仓库
aws ecr create-repository --repository-name cloudburst-processor

# 2. 获取推送命令
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# 3. 构建镜像
docker build -t cloudburst-processor .

# 4. 标记镜像
docker tag cloudburst-processor:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/cloudburst-processor:latest

# 5. 推送镜像
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/cloudburst-processor:latest
```

### 第二步：创建任务定义

#### 通过AWS控制台创建：
```
1. 在ECS控制台中，点击 "Task Definitions" → "Create new Task Definition"
2. 选择 "Fargate" 启动类型
3. 填写以下信息：
   - 任务定义名称: cloudburst-task-def
   - 任务角色: 创建新角色或使用现有角色
   - 任务执行角色: ecsTaskExecutionRole
   - 任务内存: 2048 (2GB)
   - 任务CPU: 1024 (1 vCPU)

4. 添加容器：
   - 容器名称: cloudburst-processor
   - 镜像URI: YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/cloudburst-processor:latest
   - 内存限制: 2048
   - 端口映射: (不需要，因为是批处理任务)

5. 环境变量:
   - AWS_DEFAULT_REGION: us-east-1
   - S3_BUCKET: your-cloudburst-bucket
   
6. 日志配置：
   - 选择 "awslogs"
   - 日志组: /ecs/cloudburst-task-def
```

### 第三步：创建Fargate处理器Python类

#### 简化版的Fargate处理器：
```python
import boto3
import json
import time
from datetime import datetime

class SimpleFargateProcessor:
    def __init__(self):
        self.ecs = boto3.client('ecs')
        self.cluster_name = 'cloudburst-cluster'
        self.task_definition = 'cloudburst-task-def'
        
        # 你需要设置这些网络参数
        self.subnet_ids = ['subnet-xxxxxxxxx']  # 你的子网ID
        self.security_groups = ['sg-xxxxxxxxx']  # 你的安全组ID
    
    def process_video(self, input_video_url, output_s3_path):
        """
        处理单个视频的主要方法
        """
        print(f"🎬 开始处理视频: {input_video_url}")
        
        # 启动Fargate任务
        task_arn = self._start_task(input_video_url, output_s3_path)
        
        if task_arn:
            # 等待任务完成
            result = self._wait_for_completion(task_arn)
            return result
        else:
            return {"success": False, "error": "Failed to start task"}
    
    def _start_task(self, input_url, output_path):
        """启动Fargate任务"""
        try:
            response = self.ecs.run_task(
                cluster=self.cluster_name,
                taskDefinition=self.task_definition,
                launchType='FARGATE',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': self.subnet_ids,
                        'securityGroups': self.security_groups,
                        'assignPublicIp': 'ENABLED'
                    }
                },
                overrides={
                    'containerOverrides': [
                        {
                            'name': 'cloudburst-processor',
                            'environment': [
                                {'name': 'INPUT_VIDEO_URL', 'value': input_url},
                                {'name': 'OUTPUT_S3_PATH', 'value': output_path}
                            ]
                        }
                    ]
                }
            )
            
            if response['tasks']:
                task_arn = response['tasks'][0]['taskArn']
                print(f"✅ 任务已启动: {task_arn.split('/')[-1]}")
                return task_arn
                
        except Exception as e:
            print(f"❌ 启动任务失败: {e}")
            return None
    
    def _wait_for_completion(self, task_arn):
        """等待任务完成"""
        print("⏱️ 等待任务完成...")
        
        while True:
            response = self.ecs.describe_tasks(
                cluster=self.cluster_name,
                tasks=[task_arn]
            )
            
            if response['tasks']:
                task = response['tasks'][0]
                status = task['lastStatus']
                
                if status == 'STOPPED':
                    # 检查退出码
                    containers = task.get('containers', [])
                    if containers and containers[0].get('exitCode') == 0:
                        print("✅ 任务成功完成")
                        return {"success": True, "task_arn": task_arn}
                    else:
                        print("❌ 任务失败")
                        return {"success": False, "error": "Task failed"}
                        
                print(f"📊 任务状态: {status}")
                time.sleep(10)  # 等待10秒再检查
            else:
                return {"success": False, "error": "Task not found"}

# 使用示例
processor = SimpleFargateProcessor()
result = processor.process_video(
    input_video_url="https://example.com/video.mp4",
    output_s3_path="s3://your-bucket/output/processed.mp4"
)
print(result)
```

### 第四步：容器内的处理脚本

#### 创建 `fargate_processor.py`:
```python
#!/usr/bin/env python3
"""
在Fargate容器内运行的CloudBurst处理脚本
"""
import os
import sys
import boto3
from your_existing_cloudburst_code import process_video_function

def main():
    """主处理函数"""
    # 从环境变量获取参数
    input_video_url = os.environ.get('INPUT_VIDEO_URL')
    output_s3_path = os.environ.get('OUTPUT_S3_PATH')
    
    if not input_video_url or not output_s3_path:
        print("❌ 缺少必要的环境变量")
        sys.exit(1)
    
    print(f"🎬 CloudBurst Fargate 处理器启动")
    print(f"   输入: {input_video_url}")
    print(f"   输出: {output_s3_path}")
    
    try:
        # 调用你现有的CloudBurst处理函数
        result = process_video_function(
            input_url=input_video_url,
            output_path=output_s3_path
        )
        
        if result.get('success'):
            print(f"✅ 处理完成")
            sys.exit(0)  # 成功退出
        else:
            print(f"❌ 处理失败: {result.get('error')}")
            sys.exit(1)  # 失败退出
            
    except Exception as e:
        print(f"❌ 处理出现异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 🎯 快速开始检查清单

### ✅ 准备工作：
- [ ] 有AWS账户和适当的IAM权限
- [ ] 安装了AWS CLI并配置了凭据
- [ ] Docker已安装
- [ ] 有一个可用的VPC和子网

### ✅ 实施步骤：
1. [ ] 创建ECR仓库
2. [ ] 修改Dockerfile添加Fargate入口脚本
3. [ ] 构建并推送Docker镜像到ECR
4. [ ] 在AWS控制台创建ECS集群
5. [ ] 创建任务定义
6. [ ] 测试Fargate处理器

## 💡 与你现有代码的集成

```python
# 替换你现有的RunPod实例创建逻辑
class CloudBurst:
    def __init__(self):
        # 之前：使用RunPod
        # self.runpod = RunPodManager()
        
        # 现在：使用Fargate
        self.processor = SimpleFargateProcessor()
    
    def process_videos(self, video_urls):
        """批量处理视频"""
        results = []
        
        for video_url in video_urls:
            # 之前：等待RunPod实例启动2分钟
            # instance = self.runpod.create_instance() 
            # result = self.runpod.process(instance, video_url)
            # self.runpod.terminate_instance(instance)
            
            # 现在：Fargate自动管理，30秒启动
            result = self.processor.process_video(
                input_video_url=video_url,
                output_s3_path=f"s3://your-bucket/output/{video_url.split('/')[-1]}"
            )
            
            results.append(result)
        
        return results
```

## 📊 预期改进效果

| 指标 | RunPod | ECS Fargate | 改进 |
|------|---------|-------------|------|
| **启动时间** | ~2分钟 | ~30秒 | 🚀 75%更快 |
| **待机成本** | 需要保持实例 | $0 | 💰 100%节省 |
| **可用性** | 经常无资源 | 几乎100% | ✅ 高可靠 |
| **扩展性** | GPU限制 | 无限制 | 📈 更好 |
| **运维复杂度** | 需要管理实例 | 全托管 | 🎯 更简单 |

这个方案看起来如何？需要我帮你详细设计任何特定的步骤吗？