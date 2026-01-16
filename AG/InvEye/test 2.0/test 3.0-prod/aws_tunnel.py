import json
import subprocess
import boto3
ASSUME_ROLE_ARN = "arn:aws:iam::257394494848:role/io-port-forwarding-session-assume-iam-role"
ROLE_SESSION_NAME = "sai-io-port-forwarding-session"
PROFILE="default"
AWS_REGION="ap-south-1"
INSTANCE="i-00078712b543691e3"
DOCUMENT_NAME="AWS-StartPortForwardingSessionToRemoteHost"
RDS_HOST="172.17.65.163"
RDS_PORT="8123"
LOCAL_PORT="5000"
def get_boto3_client(profile, service, region):
    session = boto3.session.Session(profile_name=profile)
    client = session.client(service, region)
    return client
def get_rds_session(profile, service, region, instance, document, reason, host, host_port, local_port):
    try:
        client = get_boto3_client(profile, service, region)
        credentials = client.assume_role(RoleArn=ASSUME_ROLE_ARN, RoleSessionName=ROLE_SESSION_NAME)
        ssm = boto3.client( "ssm",
                            aws_access_key_id=credentials.get('Credentials').get('AccessKeyId'),
                            aws_secret_access_key=credentials.get('Credentials').get('SecretAccessKey'),
                            aws_session_token=credentials.get('Credentials').get('SessionToken'))
        parameters = {"host": [host], "portNumber": [host_port], "localPortNumber": [local_port]}
        response = ssm.start_session( Target=instance,
                                    DocumentName=document,
                                    Reason=reason,
                                    Parameters=parameters)
        cmd = ['session-manager-plugin', json.dumps(response),
                region, 'StartSession', '', json.dumps({"Target": instance,
                                             "DocumentName": document,
                                             "Reason": reason,
                                             "Parameters": parameters}),
                                             'https://ssm.%s.amazonaws.com' % (region)]
        subprocess.run(cmd)
    except Exception as e:
        print("Exception: %s" % (e))
if __name__ == "__main__":
    get_rds_session(PROFILE, "sts",
                    AWS_REGION, INSTANCE, DOCUMENT_NAME,
                    "connect-to-rds", RDS_HOST, RDS_PORT, LOCAL_PORT)