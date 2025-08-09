#!/usr/bin/env python3
"""
AWS ECS Fargate CloudBurst 实施方案
真正的Serverless视频处理 - 零待机成本，按需扩展

核心思路：
1. 使用ECS Fargate替代RunPod实例
2. 任务来时自动启动容器（10-30秒）
3. 处理完成自动销毁
4. 支持并行处理多个任务
5. CPU密集型处理（如果需要GPU可以用AWS Batch）
"""

import boto3
import json
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class FargateCloudBurst:
    """
    基于AWS ECS Fargate的CloudBurst处理器
    """
    
    def __init__(self, cluster_name: str = "cloudburst-cluster", 
                 region: str = "us-east-1"):
        """
        初始化Fargate处理器
        
        Args:
            cluster_name: ECS集群名称
            region: AWS区域
        """
        self.cluster_name = cluster_name
        self.region = region
        
        # 初始化AWS客户端
        self.ecs = boto3.client('ecs', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        
        # 配置
        self.task_definition_name = "cloudburst-processor"
        self.subnet_ids = []  # 需要配置
        self.security_group_ids = []  # 需要配置
        
        # 任务跟踪
        self.running_tasks = {}
        self.completed_tasks = {}
        
        print(f"🚀 Fargate CloudBurst 初始化完成")
        print(f"   集群: {cluster_name}")
        print(f"   区域: {region}")
    
    def setup_infrastructure(self):
        """
        一次性设置AWS基础设施
        这个函数只需要运行一次来创建所有必要的AWS资源
        """
        print("🏗️ 设置AWS基础设施...")
        
        # 1. 创建ECS集群
        self._create_ecs_cluster()
        
        # 2. 创建任务定义
        self._create_task_definition()
        
        # 3. 设置网络（VPC、子网、安全组）
        self._setup_networking()
        
        # 4. 设置日志组
        self._create_log_group()
        
        print("✅ 基础设施设置完成！")
    
    def _create_ecs_cluster(self):
        """创建ECS集群"""
        try:
            response = self.ecs.create_cluster(
                clusterName=self.cluster_name,
                capacityProviders=['FARGATE', 'FARGATE_SPOT'],  # 支持Spot实例节省成本
                defaultCapacityProviderStrategy=[
                    {
                        'capacityProvider': 'FARGATE_SPOT',  # 优先使用Spot（便宜60-70%）
                        'weight': 2,
                        'base': 0
                    },
                    {
                        'capacityProvider': 'FARGATE',  # 备用标准Fargate
                        'weight': 1,
                        'base': 1
                    }
                ]
            )
            print(f"✅ ECS集群已创建: {self.cluster_name}")
            
        except self.ecs.exceptions.InvalidParameterException:
            print(f"ℹ️ ECS集群 {self.cluster_name} 已存在")
    
    def _create_task_definition(self):
        """
        创建任务定义（相当于Docker容器的运行配置）
        """
        task_definition = {
            "family": self.task_definition_name,
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": "2048",  # 2 vCPU
            "memory": "4096",  # 4GB内存
            "executionRoleArn": self._get_or_create_execution_role(),
            "taskRoleArn": self._get_or_create_task_role(),
            "containerDefinitions": [
                {
                    "name": "cloudburst-processor",
                    "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/cloudburst:latest",  # 你的Docker镜像
                    "essential": True,
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": f"/ecs/{self.task_definition_name}",
                            "awslogs-region": self.region,
                            "awslogs-stream-prefix": "ecs"
                        }
                    },
                    "environment": [
                        {"name": "AWS_DEFAULT_REGION", "value": self.region},
                        {"name": "PYTHONUNBUFFERED", "value": "1"}
                    ],
                    "mountPoints": [],
                    "volumesFrom": []
                }
            ]
        }
        
        try:
            response = self.ecs.register_task_definition(**task_definition)
            print(f"✅ 任务定义已创建: {self.task_definition_name}")
            
        except Exception as e:
            print(f"❌ 创建任务定义失败: {e}")
    
    def _setup_networking(self):
        """
        设置网络配置
        这里需要你的VPC和子网信息
        """
        # TODO: 替换为你的实际网络配置
        self.subnet_ids = [
            "subnet-xxxxxxxx",  # 你的公共子网ID
            "subnet-yyyyyyyy"   # 另一个可用区的子网ID
        ]
        
        self.security_group_ids = [
            "sg-xxxxxxxx"  # 你的安全组ID，允许出站互联网访问
        ]
        
        print("ℹ️ 网络配置需要手动设置subnet_ids和security_group_ids")
    
    def _get_or_create_execution_role(self) -> str:
        """
        获取或创建ECS执行角色
        """
        # 返回执行角色ARN
        # TODO: 创建或获取实际的IAM角色
        return "arn:aws:iam::your-account:role/ecsTaskExecutionRole"
    
    def _get_or_create_task_role(self) -> str:
        """
        获取或创建ECS任务角色（用于访问S3等服务）
        """
        # 返回任务角色ARN
        # TODO: 创建或获取实际的IAM角色
        return "arn:aws:iam::your-account:role/CloudBurstTaskRole"
    
    def _create_log_group(self):
        """创建CloudWatch日志组"""
        try:
            self.logs.create_log_group(
                logGroupName=f"/ecs/{self.task_definition_name}",
                retentionInDays=7  # 日志保留7天
            )
            print("✅ 日志组已创建")
            
        except self.logs.exceptions.ResourceAlreadyExistsException:
            print("ℹ️ 日志组已存在")
    
    async def process_video_async(self, video_path: str, 
                                  output_path: str = None,
                                  task_cpu: str = "1024",
                                  task_memory: str = "2048") -> Dict:
        """
        异步处理视频（主要API）
        
        Args:
            video_path: 输入视频路径（S3或HTTP URL）
            output_path: 输出路径（S3）
            task_cpu: CPU分配（256, 512, 1024, 2048, 4096）
            task_memory: 内存分配（512-30720MB）
            
        Returns:
            Dict: 处理结果
        """
        task_id = f"cloudburst_{uuid.uuid4().hex[:8]}"
        
        print(f"🎬 开始处理视频: {task_id}")
        print(f"   输入: {video_path}")
        print(f"   输出: {output_path or 'auto-generated'}")
        
        try:
            # 1. 启动Fargate任务
            task_arn = await self._start_fargate_task(
                task_id, video_path, output_path, task_cpu, task_memory
            )
            
            if not task_arn:
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": "Failed to start Fargate task"
                }
            
            # 2. 等待任务完成
            result = await self._wait_for_task_completion(task_id, task_arn)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }
    
    async def _start_fargate_task(self, task_id: str, video_path: str,
                                  output_path: str, task_cpu: str, 
                                  task_memory: str) -> Optional[str]:
        """
        启动Fargate任务
        """
        print(f"🚀 启动Fargate任务: {task_id}")
        
        # 构建环境变量
        environment_vars = [
            {"name": "TASK_ID", "value": task_id},
            {"name": "INPUT_VIDEO", "value": video_path},
            {"name": "OUTPUT_PATH", "value": output_path or f"s3://your-bucket/output/{task_id}.mp4"},
            {"name": "AWS_DEFAULT_REGION", "value": self.region}
        ]
        
        try:
            response = self.ecs.run_task(
                cluster=self.cluster_name,
                taskDefinition=self.task_definition_name,
                launchType="FARGATE",  # 也可以用FARGATE_SPOT节省成本
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': self.subnet_ids,
                        'securityGroups': self.security_group_ids,
                        'assignPublicIp': 'ENABLED'  # 需要访问互联网
                    }
                },
                overrides={
                    'cpu': task_cpu,
                    'memory': task_memory,
                    'containerOverrides': [
                        {
                            'name': 'cloudburst-processor',
                            'environment': environment_vars
                        }
                    ]
                },
                tags=[
                    {'key': 'Project', 'value': 'CloudBurst'},
                    {'key': 'TaskID', 'value': task_id}
                ]
            )
            
            if response['tasks']:
                task_arn = response['tasks'][0]['taskArn']
                self.running_tasks[task_id] = {
                    'task_arn': task_arn,
                    'started_at': datetime.now(),
                    'status': 'RUNNING'
                }
                
                print(f"✅ Fargate任务已启动: {task_arn.split('/')[-1]}")
                return task_arn
            else:
                print("❌ 无法启动Fargate任务")
                return None
                
        except Exception as e:
            print(f"❌ 启动任务失败: {e}")
            return None
    
    async def _wait_for_task_completion(self, task_id: str, task_arn: str) -> Dict:
        """
        等待任务完成并获取结果
        """
        print(f"⏱️ 等待任务完成: {task_id}")
        
        start_time = datetime.now()
        timeout_minutes = 30  # 30分钟超时
        
        while True:
            try:
                # 检查任务状态
                response = self.ecs.describe_tasks(
                    cluster=self.cluster_name,
                    tasks=[task_arn]
                )
                
                if not response['tasks']:
                    return {
                        "success": False,
                        "task_id": task_id,
                        "error": "Task not found"
                    }
                
                task = response['tasks'][0]
                last_status = task['lastStatus']
                
                # 更新任务状态
                if task_id in self.running_tasks:
                    self.running_tasks[task_id]['status'] = last_status
                
                if last_status == 'STOPPED':
                    # 任务完成，检查退出代码
                    containers = task.get('containers', [])
                    if containers:
                        exit_code = containers[0].get('exitCode', 1)
                        
                        if exit_code == 0:
                            # 成功
                            duration = (datetime.now() - start_time).total_seconds()
                            
                            result = {
                                "success": True,
                                "task_id": task_id,
                                "task_arn": task_arn,
                                "duration": duration,
                                "exit_code": exit_code,
                                "logs_url": self._get_logs_url(task_id)
                            }
                            
                            # 移动到完成列表
                            self.completed_tasks[task_id] = result
                            if task_id in self.running_tasks:
                                del self.running_tasks[task_id]
                            
                            print(f"✅ 任务完成: {task_id} (耗时: {duration:.1f}秒)")
                            return result
                        else:
                            # 失败
                            error_reason = containers[0].get('reason', 'Unknown error')
                            
                            result = {
                                "success": False,
                                "task_id": task_id,
                                "error": f"Task failed with exit code {exit_code}: {error_reason}",
                                "exit_code": exit_code,
                                "logs_url": self._get_logs_url(task_id)
                            }
                            
                            print(f"❌ 任务失败: {task_id} - {error_reason}")
                            return result
                
                # 检查超时
                if (datetime.now() - start_time).total_seconds() > timeout_minutes * 60:
                    # 超时，停止任务
                    await self._stop_task(task_arn)
                    
                    return {
                        "success": False,
                        "task_id": task_id,
                        "error": f"Task timeout after {timeout_minutes} minutes"
                    }
                
                # 等待5秒再检查
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"❌ 检查任务状态出错: {e}")
                await asyncio.sleep(10)
    
    async def _stop_task(self, task_arn: str):
        """
        停止任务
        """
        try:
            self.ecs.stop_task(
                cluster=self.cluster_name,
                task=task_arn,
                reason='Timeout'
            )
            print(f"🛑 任务已停止: {task_arn.split('/')[-1]}")
            
        except Exception as e:
            print(f"❌ 停止任务失败: {e}")
    
    def _get_logs_url(self, task_id: str) -> str:
        """
        获取任务日志URL
        """
        log_group = f"/ecs/{self.task_definition_name}"
        log_stream = f"ecs/cloudburst-processor/{task_id}"
        
        return f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#logsV2:log-groups/log-group/{log_group.replace('/', '$252F')}/log-events/{log_stream.replace('/', '$252F')}"
    
    async def process_multiple_videos(self, video_list: List[str],
                                      max_concurrent: int = 10) -> List[Dict]:
        """
        并行处理多个视频
        
        Args:
            video_list: 视频路径列表
            max_concurrent: 最大并发数
            
        Returns:
            List[Dict]: 处理结果列表
        """
        print(f"📦 开始批量处理: {len(video_list)} 个视频")
        print(f"   最大并发: {max_concurrent}")
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(video_path: str):
            async with semaphore:
                return await self.process_video_async(video_path)
        
        # 并发处理所有视频
        results = await asyncio.gather(*[
            process_with_semaphore(video_path)
            for video_path in video_list
        ])
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - success_count
        
        print(f"📊 批量处理完成:")
        print(f"   成功: {success_count}")
        print(f"   失败: {failed_count}")
        
        return results
    
    def get_status(self) -> Dict:
        """
        获取当前状态
        """
        return {
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "cluster_name": self.cluster_name,
            "region": self.region,
            "task_definition": self.task_definition_name
        }
    
    def print_status(self):
        """
        打印当前状态
        """
        status = self.get_status()
        print(f"\n📊 Fargate CloudBurst 状态:")
        print(f"   运行中任务: {status['running_tasks']}")
        print(f"   已完成任务: {status['completed_tasks']}")
        print(f"   集群: {status['cluster_name']}")
        print(f"   区域: {status['region']}")


# Docker容器内的处理脚本示例
CONTAINER_SCRIPT = '''#!/usr/bin/env python3
"""
CloudBurst Fargate容器内的处理脚本
这个脚本会在Fargate容器内运行
"""

import os
import sys
import boto3
from your_cloudburst_module import process_video

def main():
    # 从环境变量获取参数
    task_id = os.environ.get('TASK_ID')
    input_video = os.environ.get('INPUT_VIDEO')
    output_path = os.environ.get('OUTPUT_PATH')
    
    print(f"🎬 CloudBurst Fargate处理器启动")
    print(f"   任务ID: {task_id}")
    print(f"   输入: {input_video}")
    print(f"   输出: {output_path}")
    
    try:
        # 处理视频
        result = process_video(
            input_path=input_video,
            output_path=output_path,
            task_id=task_id
        )
        
        if result['success']:
            print(f"✅ 处理完成: {result['output_file']}")
            sys.exit(0)
        else:
            print(f"❌ 处理失败: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 容器处理出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

# 使用示例
async def example_usage():
    """
    使用示例
    """
    # 创建Fargate处理器
    processor = FargateCloudBurst(
        cluster_name="cloudburst-prod",
        region="us-east-1"
    )
    
    # 一次性设置基础设施（只需要运行一次）
    # processor.setup_infrastructure()
    
    # 处理单个视频
    print("🎬 测试单个视频处理...")
    result = await processor.process_video_async(
        video_path="s3://your-bucket/input/test.mp4",
        output_path="s3://your-bucket/output/test_processed.mp4"
    )
    
    print(f"结果: {result}")
    
    # 批量处理视频
    print("\n📦 测试批量处理...")
    video_list = [
        "s3://your-bucket/input/video1.mp4",
        "s3://your-bucket/input/video2.mp4", 
        "s3://your-bucket/input/video3.mp4"
    ]
    
    results = await processor.process_multiple_videos(
        video_list=video_list,
        max_concurrent=5
    )
    
    # 显示状态
    processor.print_status()

if __name__ == "__main__":
    asyncio.run(example_usage())