# [boto3] [create_stack] CloudFormationスタックをシリアルに実行するサンプルスクリプト

## 概要

- CloudFormationスタックを順次するboto3スクリプト
- スタック実行はシリアル（順次）実行される
- 実行中のスタックが完了するまで次のスタックは実行しない

## 環境

Windows 10 の以下バージョンの環境にて動作を確認

```
PS C:\> python3 --version
Python 3.8.10
PS C:\> aws --version
aws-cli/2.2.3 Python/3.8.8 Windows/10 exe/AMD64 prompt/off
PS C:\> python3
Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import boto3
>>> import botocore
>>> print(f'boto3 version: {boto3.__version__}')
boto3 version: 1.14.43
>>> print(f'botocore version: {botocore.__version__}')
botocore version: 1.17.43
>>>
PS C:\> aws configure
AWS Access Key ID [****************XXXX]:
AWS Secret Access Key [****************XXXX]:
Default region name [ap-northeast-1]:
Default output format [json]:
```

## 実行前の準備

- S3バケットを作成し、さらにprefix(フォルダ)を作成し以下のようにymlファイルを格納します。

```
PS C:\> aws s3 ls s3://{{S3バケット名}} --recursive
2021-05-07 18:32:58       1940 test/ec2-linux.yml
2021-05-07 17:36:00       1112 test/sg.yml
2021-05-07 17:46:45       1821 test/subnet-public.yml
2021-05-07 17:36:00       1062 test/vpc.yml
```

## 実行方法

コマンド例

```
C:\Users\usr001\tmp> python3 .\test.py -f sample.json -s3 {{S3バケット名}} -p test
```

-f に sample.json を、-s3 に実行前の準備でymlファイルを格納したS3バケット名を、-p prefix(フォルダ)名を指定します。


## 制御について

CloudFormaionスタック実行時に使用するymlファイルと指定するパラメータは、sample.json で指定します。

例１）sample.jsonが以下の場合、ymlファイルは vpc.yml でPJPrefixとVPCCIDRがパラメータになります。StackNameはスタック名です。

```
[
    {"StackName": "test001-vpc","Code": "vpc.yml", "PJPrefix": "Project1","VPCCIDR": "10.11.0.0/16"}
]
```

例２）sample.jsonが以下の場合、2つのスタックを実行します。vpc.ymlを使用したスタックの実行が完了した後で、subnet-public.ymlを使用したスタックが実行を開始します。

```
[
    {"StackName": "test001-vpc","Code": "vpc.yml", "PJPrefix": "Project1","VPCCIDR": "10.11.0.0/16"},
    {"StackName": "test001-subnet1","Code": "subnet-public.yml", "PJPrefix": "Project1","NetworkName": "Net001","PublicSubnetCIDR": "10.11.1.0/24", "AZName": "ap-northeast-1a"},
]
```

本リポジトリに格納したsample.jsonは以下であり、VPC→サブネットワーク→セキュリティグループ→EC2インスタンスの順にシリアルにスタックを実行します。※EC2起動は課金の可能性があるので注意※

```
[
    {"StackName": "test001-vpc","Code": "vpc.yml", "PJPrefix": "Project1","VPCCIDR": "10.11.0.0/16"},
    {"StackName": "test001-subnet1","Code": "subnet-public.yml", "PJPrefix": "Project1","NetworkName": "Net001","PublicSubnetCIDR": "10.11.1.0/24", "AZName": "ap-northeast-1a"},
    {"StackName": "test001-sg","Code": "sg.yml", "PJPrefix": "Project1","ServiceName": "ServiceA","SGNo": "001"},
    {"StackName": "test001-ec2","Code": "ec2-linux.yml", "PJPrefix": "Project1","ServiceName": "ServiceA","SGNo": "001",
        "NetworkName":             "Net001",
        "KeyPairName":             "keypair_ap-northeast-1_01",
        "EC2InstanceName":         "ec2-001",
        "EC2InstanceAMI":          "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2",
        "EC2InstanceInstanceType": "t2.micro",
        "EC2InstanceVolumeType":   "gp2",
        "EC2InstanceVolumeSize":   "8"
    }
]
```


## 実行例

スクリプトを実行したときに出力される

```
PS C:\Users\usr001\tmp> python3 .\test.py -f sample.json -s3 {{S3バケット名}} -p test
{'StackName': 'test001-vpc', 'TemplateURL': 'https://{{S3バケット名}}.s3-ap-northeast-1.amazonaws.com/test/vpc.yml', 'Parameters': [{'ParameterKey': 'PJPrefix', 'ParameterValue': 'Project1'}, {'ParameterKey': 'VPCCIDR', 'ParameterValue': '10.11.0.0/16'}]}
[LOG] CFn Stack [test001-vpc] start.
[LOG] CFn Stack [test001-vpc] end.
スタック名 : test001-vpc
スタックID : arn:aws:cloudformation:ap-northeast-1:121212121212:stack/test001-vpc/00000000-0000-0000-0000-000000000000
パラメータ
        VPCCIDR = 10.11.0.0/16
        PJPrefix = Project1
[CloudFormation] Outputs
        VPCCIDR : 10.11.0.0/16 : Project1-vpc-cidr
        InternetGateway : igw-00000000000000000 : Project1-igw
        VPC : vpc-00000000000000000 : Project1-vpc
{'StackName': 'test001-subnet1', 'TemplateURL': 'https://{{S3バケット名}}.s3-ap-northeast-1.amazonaws.com/test/subnet-public.yml', 'Parameters': [{'ParameterKey': 'PJPrefix', 'ParameterValue': 'Project1'}, {'ParameterKey': 'NetworkName', 'ParameterValue': 'Net001'}, {'ParameterKey': 'PublicSubnetCIDR', 'ParameterValue': '10.11.1.0/24'}, {'ParameterKey': 'AZName', 'ParameterValue': 'ap-northeast-1a'}]}        
[LOG] CFn Stack [test001-subnet1] start.
[LOG] CFn Stack [test001-subnet1] end.
スタック名 : test001-subnet1
スタックID : arn:aws:cloudformation:ap-northeast-1:121212121212:stack/test001-subnet1/0000000-0000-0000-0000-000000000000
パラメータ
        AZName = ap-northeast-1a
        PublicSubnetCIDR = 10.11.1.0/24
        NetworkName = Net001
        PJPrefix = Project1
[CloudFormation] Outputs
        PublicSubnet01 : subnet-0000000000000000 : Net001-ap-northeast-1a
        PublicSubnetCIDR : 10.11.1.0/24 : Net001-ap-northeast-1a-cidr
        PublicRouteTable01 : rtb-0000000000000000 : Net001-ap-northeast-1a-routetbl
{'StackName': 'test001-sg', 'TemplateURL': 'https://{{S3バケット名}}.s3-ap-northeast-1.amazonaws.com/test/sg.yml', 'Parameters': [{'ParameterKey': 'PJPrefix', 'ParameterValue': 'Project1'}, {'ParameterKey': 'ServiceName', 'ParameterValue': 'ServiceA'}, {'ParameterKey': 'AWSResource', 'ParameterValue': 'EC2'}, {'ParameterKey': 'SGNo', 'ParameterValue': '001'}]}
[LOG] CFn Stack [test001-sg] start.
[LOG] CFn Stack [test001-sg] end.
スタック名 : test001-sg
b7a1f
パラメータ
        SGNo = 001
        ServiceName = ServiceA
        AWSResource = EC2
        PJPrefix = Project1
[CloudFormation] Outputs
        SecurityGroupEC2 : sg-00000000000000000 : sg-Project1-EC2-001
PS C:\Users\usr001\tmp>
```


