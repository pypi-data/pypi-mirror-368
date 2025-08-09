# AWS IAM角色设置指南 - 告别Access Key

## 🎯 **为什么要用IAM角色替代Access Key？**

### **问题：Access Key的安全隐患**
```python
# ❌ 不安全的做法 (你现在的方式)
aws_access_key_id = "AKIAIOSFODNN7EXAMPLE" 
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# 问题：
# 1. 密钥可能被意外暴露到代码、日志、GitHub
# 2. 密钥长期有效，难以轮换
# 3. 一旦泄露，攻击者可以随意使用
# 4. 难以审计和控制权限
```

### **解决方案：IAM角色**
```python
# ✅ 安全的做法 (使用IAM角色)
import boto3

# 无需硬编码任何密钥！
ec2 = boto3.client('ecs')  # 自动获取临时凭据
s3 = boto3.client('s3')    # 权限由角色控制

# 优势：
# 1. 临时凭据，自动轮换
# 2. 精确的权限控制
# 3. 完整的审计追踪
# 4. 不会意外泄露
```

## 🏗️ **IAM角色设置步骤**

### **步骤1：创建IAM角色**

#### **通过AWS控制台：**
```
1. 进入 IAM 控制台
2. 点击 "角色" → "创建角色"
3. 选择可信实体类型：
   - ECS任务：选择 "AWS服务" → "Elastic Container Service" → "Elastic Container Service Task"
   - EC2实例：选择 "AWS服务" → "EC2"
   - Lambda函数：选择 "AWS服务" → "Lambda"
4. 输入角色名称：CloudBurstExecutionRole
```

#### **通过AWS CLI：**
```bash
# 创建信任策略文件
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 创建角色
aws iam create-role \
    --role-name CloudBurstExecutionRole \
    --assume-role-policy-document file://trust-policy.json
```

### **步骤2：创建权限策略**

#### **CloudBurst所需的权限：**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-cloudburst-bucket",
        "arn:aws:s3:::your-cloudburst-bucket/*"
      ]
    },
    {
      "Effect": "Allow", 
      "Action": [
        "ecs:RunTask",
        "ecs:StopTask",
        "ecs:DescribeTasks"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ecs:cluster": "arn:aws:ecs:us-east-1:ACCOUNT:cluster/cloudburst-cluster"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream", 
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:ACCOUNT:log-group:/ecs/cloudburst*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    }
  ]
}
```

#### **创建并附加策略：**
```bash
# 创建权限策略
aws iam create-policy \
    --policy-name CloudBurstExecutionPolicy \
    --policy-document file://cloudburst-policy.json

# 附加策略到角色
aws iam attach-role-policy \
    --role-name CloudBurstExecutionRole \
    --policy-arn arn:aws:iam::ACCOUNT:policy/CloudBurstExecutionPolicy
```

### **步骤3：在不同场景中使用IAM角色**

#### **场景A：ECS Fargate任务中使用**
```python
# 在ECS任务定义中指定角色
task_definition = {
    "family": "cloudburst-processor",
    "networkMode": "awsvpc", 
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "4096",
    "memory": "16384",
    
    # 🔑 关键：指定执行角色和任务角色
    "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",  # 拉取镜像等
    "taskRoleArn": "arn:aws:iam::ACCOUNT:role/CloudBurstExecutionRole",    # 你的应用权限
    
    "containerDefinitions": [{
        "name": "cloudburst-processor",
        "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/cloudburst:latest",
        # 不需要环境变量中的AWS凭据！
        "environment": [
            {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"}
            # 注意：不需要 AWS_ACCESS_KEY_ID 和 AWS_SECRET_ACCESS_KEY
        ]
    }]
}

# 在容器内的代码
import boto3

# 🎯 无需提供任何凭据，自动从角色获取
s3_client = boto3.client('s3')
ecs_client = boto3.client('ecs')

# 正常使用，权限由附加到任务的角色控制
s3_client.upload_file('local_file.mp4', 'bucket', 'output.mp4')
```

#### **场景B：EC2实例中使用**
```python
# 1. 为EC2实例创建实例配置文件
aws iam create-instance-profile --instance-profile-name CloudBurstInstanceProfile

# 2. 将角色添加到实例配置文件
aws iam add-role-to-instance-profile \
    --instance-profile-name CloudBurstInstanceProfile \
    --role-name CloudBurstExecutionRole

# 3. 在创建EC2实例时指定实例配置文件
response = ec2.run_instances(
    ImageId='ami-xxxxxxxx',
    MinCount=1,
    MaxCount=1,
    InstanceType='c5.2xlarge',
    IamInstanceProfile={
        'Name': 'CloudBurstInstanceProfile'  # 🔑 关键设置
    }
)

# 4. 在EC2实例内的代码
import boto3

# 🎯 无需任何凭据配置！
client = boto3.client('s3')  # 自动从实例元数据获取临时凭据
```

#### **场景C：Lambda函数中使用**
```python
# 在Lambda函数配置中指定执行角色
lambda_client.create_function(
    FunctionName='cloudburst-processor',
    Runtime='python3.11',
    Role='arn:aws:iam::ACCOUNT:role/CloudBurstExecutionRole',  # 🔑 指定角色
    Handler='lambda_function.lambda_handler',
    Code={'ZipFile': zip_content}
)

# Lambda函数内的代码
import boto3

def lambda_handler(event, context):
    # 🎯 自动获取临时凭据
    s3 = boto3.client('s3')
    ecs = boto3.client('ecs')
    
    # 处理视频任务...
    return {'statusCode': 200}
```

### **步骤4：本地开发环境的处理**

#### **问题：本地开发怎么办？**
本地开发时无法直接使用ECS/EC2的角色，但有几种解决方案：

#### **方案A：AssumeRole（推荐）**
```python
import boto3

class LocalDevelopment:
    def __init__(self):
        # 本地开发时，使用临时的AssumeRole
        sts = boto3.client('sts')
        
        # 假设你的开发用户有AssumeRole权限
        assumed_role = sts.assume_role(
            RoleArn='arn:aws:iam::ACCOUNT:role/CloudBurstExecutionRole',
            RoleSessionName='local-development'
        )
        
        credentials = assumed_role['Credentials']
        
        # 使用临时凭据创建客户端
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
    
    def test_cloudburst(self):
        # 使用相同的权限测试
        self.s3.list_objects_v2(Bucket='your-bucket')
```

#### **方案B：AWS配置文件**
```bash
# ~/.aws/config
[profile cloudburst-dev]
role_arn = arn:aws:iam::ACCOUNT:role/CloudBurstExecutionRole
source_profile = default
region = us-east-1

# 在代码中使用
import boto3

session = boto3.Session(profile_name='cloudburst-dev')
s3 = session.client('s3')
```

## 🔄 **迁移步骤总结**

### **从Access Key到IAM角色的完整迁移：**

#### **第1步：创建IAM角色和权限**
```bash
# 执行上面的角色创建命令
aws iam create-role --role-name CloudBurstExecutionRole ...
aws iam create-policy --policy-name CloudBurstExecutionPolicy ...
aws iam attach-role-policy ...
```

#### **第2步：修改CloudBurst代码**
```python
# 老代码（使用Access Key）
# import boto3
# s3 = boto3.client(
#     's3',
#     aws_access_key_id='AKIA...',
#     aws_secret_access_key='xxxx'
# )

# 新代码（使用IAM角色）
import boto3
s3 = boto3.client('s3')  # 自动从角色获取凭据！
```

#### **第3步：更新基础设施**
- ECS任务定义：添加taskRoleArn
- EC2实例：添加IAM实例配置文件
- Lambda函数：指定执行角色

#### **第4步：删除Access Key**
```bash
# 确认一切工作正常后，删除旧的Access Key
aws iam delete-access-key --user-name your-user --access-key-id AKIA...
```

## ✅ **验证设置是否正确**

### **测试脚本：**
```python
import boto3
import json

def test_iam_role_permissions():
    """测试IAM角色权限是否正确设置"""
    
    try:
        # 测试S3权限
        s3 = boto3.client('s3')
        s3.list_objects_v2(Bucket='your-cloudburst-bucket')
        print("✅ S3权限正常")
        
        # 测试ECS权限
        ecs = boto3.client('ecs')
        ecs.list_clusters()
        print("✅ ECS权限正常")
        
        # 测试当前身份
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ 当前身份: {identity['Arn']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 权限测试失败: {e}")
        return False

if __name__ == "__main__":
    test_iam_role_permissions()
```

## 🎯 **安全最佳实践总结**

### **✅ 使用IAM角色后的优势：**
1. **零密钥管理** - 不需要存储任何长期凭据
2. **自动轮换** - 临时凭据自动失效和更新
3. **精确权限** - 只给应用需要的最小权限
4. **完整审计** - 所有API调用都有详细日志
5. **防止泄露** - 即使代码泄露也不会暴露凭据

### **🚫 再也不用担心：**
- ❌ Access Key泄露到GitHub
- ❌ 日志中意外记录密钥
- ❌ 密钥轮换的复杂性
- ❌ 权限过大的安全风险

这就是AWS推荐的"零信任"安全架构的核心部分！

需要我帮你设计具体的迁移计划吗？