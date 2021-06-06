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
excluded_services = os.environ['EXCLUDED_SERVICES'].split(' ')
result = { 'stoppedServices': [ ], 'excludedServices': [ ] }

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
    paginator = ecs.get_paginator('list_services')
    response_iterator = paginator.paginate(cluster=ecs_cluster)
    ecs_services = []
    for page in response_iterator:
        ecs_services.extend(page['serviceArns'])
    
    for service in ecs_services:
        if os.path.basename(service) in excluded_services:
            print("\n'" + service + "' ECS service is excluded")
            result['excludedServices'].append(service)
        else:
            print("\nScaling in '" + service + "' ECS service tasks to 0...")
            response = ecs.update_service(
                cluster=ecs_cluster,
                service=service,
                desiredCount=0
            )

            #print(json_response(response))
            result['stoppedServices'].append(service)

    print("\nFinal result:\n" + json_response(result) + "\n")
    print("\n##### Execution finished #####\n")
    return {
        'statusCode': 200,
        'body': json_response(result)
    }
