# 推荐架构
class CloudBurstOrchestrator:
    def __init__(self):
        # 使用ECS Task Role或Lambda执行角色
        self.ecs_client = boto3.client('ecs')
        self.lambda_client = boto3.client('lambda')
    
    def process_with_role_based_auth(self, task):
        """使用IAM角色，无需管理密钥"""
        task_definition = {
            "taskRoleArn": "arn:aws:iam::account:role/CloudBurstProcessingRole",
            "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole"
        }