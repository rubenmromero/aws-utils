#
# Modules Import
#
import boto3
import json
import os

#
# Variables Definition
#
ecs_cluster = os.environ['ECS_CLUSTER']
result = { 'startedServices': [ ] }

#
# Function to print the boto3 responses in JSON format
#
def json_response(response):
    return json.dumps(
        response,
        default=str,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    )

#
# Main
#
def lambda_handler(event, context):
    print("\n##### Starting execution #####\n")
    
    ecs = boto3.client('ecs')
    
    # Get all services belonging to the ECS cluster
    ecs_services = ecs.list_services(cluster=ecs_cluster)['serviceArns']
    
    for service in ecs_services:
        print("\nScaling out '" + service + "' ECS service tasks to 1...")
        response = ecs.update_service(
            cluster=ecs_cluster,
            service=service,
            desiredCount=1
        )

        #print(json_response(response))
        result['startedServices'].append(service)
    
    print("\nFinal result:\n" + json_response(result) + "\n")
    print("\n##### Execution finished #####\n")
    return {
        'statusCode': 200,
        'body': json_response(result)
    }
