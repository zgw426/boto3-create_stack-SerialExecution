import boto3
import json
import argparse

parser = argparse.ArgumentParser(description='-fオプションでjsonファイルを指定')
parser.add_argument('-f', '--file')
parser.add_argument('-s3', '--s3bucket')
parser.add_argument('-p', '--prefix')

args = parser.parse_args()
jsonfile = args.file
bucketName = args.s3bucket
prefix = args.prefix
createStackCode = ""
templateUrlVal = ""
stackVal = ""
paramVal = []
paramFlg = 0
stack_name = ""
template_url = ""

s3 = boto3.resource("s3")
bucket = s3.Bucket( bucketName )
cf = boto3.client("cloudformation")

json_open = open(jsonfile, 'r')
json_load = json.load(json_open)

def info_stack(argStackName):
    client = boto3.client('cloudformation')
    res = client.describe_stacks(StackName= argStackName )

    print( "スタック名 : {0}".format(res["Stacks"][0]["StackName"]) )
    print( "スタックID : {0}".format(res["Stacks"][0]["StackId"]) )

    print( "パラメータ" )
    for info in res["Stacks"][0]["Parameters"]:
        print("\t{0} = {1}".format( info["ParameterKey"], info["ParameterValue"] ) )

    print( "[CloudFormation] Outputs" )
    for info in res["Stacks"][0]["Outputs"]:
        print("\t{0} : {1} : {2}".format( info["OutputKey"], info["OutputValue"], info["ExportName"] ) )


for stack in json_load:
    params = {}
    paramVal = []
    for param in stack:
        if param == "StackName":
            stack_name = stack[param]
        elif param == "Code":
            template_url = "https://"+ bucketName +".s3-ap-northeast-1.amazonaws.com/" + prefix + "/" + stack[param]
        else:
            paramVal.append({"ParameterKey": param ,"ParameterValue": stack[param]})

    params = {
        'StackName': stack_name,
        'TemplateURL': template_url,
        'Parameters': paramVal,
    }

    print(params)
    res = cf.create_stack( **params )

    print("[LOG] CFn Stack [{0}] start.".format(stack_name) )
    waiter = cf.get_waiter('stack_create_complete')
    waiter.wait(StackName=stack["StackName"]) # スタック完了まで待つ
    print("[LOG] CFn Stack [{0}] end.".format(stack_name)) # スタック完了後に実行される処理
    info_stack(stack_name)



