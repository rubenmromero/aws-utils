#
# Modules Import
#
import boto3
import json
import os
import re
from datetime import datetime, date

#
# Variables Definition
#
current_time = datetime.now()
DEBUG = True
ecs_cluster = os.environ['ECS_CLUSTER']
result = { 'startedServices': [ ], 'stoppedServices': [ ] }

#
# Initialize ECS client
#
ecs = boto3.client('ecs')

def json_response(response):
    '''
    Function to print the boto3 responses in JSON format
    '''

    return json.dumps(
        response,
        default=str,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    )

def match(unit, range):
    '''
    Main function to compare the current time with the time defined in cron expression
    The main purpose of this funcion is validate types and formats, and decide if 'unit' match with 'range'
    
    'unit' must be an integer with the current time
    'range' must be a string with the value or values defined in cron expression
    '''
    
    # Validate types
    if type(range) is not str or type(unit) is not int:
        return False
    
    # For wildcards, accept all
    if range == "*":
        return True
    
    # Range parameter must match with some valid cron expression (number, range or enumeration) -> "*", "0", "1-3", "1,3,5,7", etc
    pattern = re.compile("^[0-9]+-[0-9]+$|^[0-9]+(,[0-9]+)*$")
    if not pattern.match(range):
        #print("\nThere is an error in the cron line")
        return False
    
    # If range's length = 1, must be the exact unit number
    if 1 <= len(range) <= 2:
        if unit == int(range):
            return True
    
    # For ranges, the unit must be among range numbers
    if "-" in range:
        units = range.split("-")
        if int(units[0]) <= unit <= int(units[1]):
            return True
        else:
            return False
    
    # For enumerations, the unit must be one of the elements in the enumeration
    if "," in range:
        if str(unit) in range:
            return True
    
    return False

def checkMinutes(cronString):
    return match(current_time.minute, cronString.split()[0])

def checkHours(cronString):
    return match(current_time.hour, cronString.split()[1])

def checkWeekdays(cronString):
    return match(current_time.isoweekday(), cronString.split()[2])
        
def isTime(cronString):
    '''
    This function returns True if this precise moment match with the cron expression.
    This functions can be as smart as you need. Right now, it only match the present hour
    with the hour defined in the cron expression.
    '''
    
    if checkMinutes(cronString) and checkHours(cronString) and checkWeekdays(cronString):
        return True
    
def cronECSExec(cron, service_arn, service_name, service_config, action):
    '''
    Function to control operations on ECS services
    '''

    if DEBUG:   print("\n{2} service: Current time is {0} and cron expression is {1}".format(current_time, cron, action))
    if cron == '':
        print("\nEmpty cron expression; nothing to do")
        return True
    
    if isTime(cron):
        if action == 'start' and service_config['services'][0]['runningCount'] == 0:
            # Start service
            print("\nScaling out '" + service_name + "' service tasks to 1...")
            response = ecs.update_service(
                cluster=ecs_cluster,
                service=service_arn,
                desiredCount=1
            )
            #if DEBUG:   print(json_response(response))
            result['startedServices'].append(service_name)
            
        if action == 'stop' and service_config['services'][0]['runningCount'] > 0:
            # Stop service
            print("\nScaling in '" + service_name + "' service tasks to 0...")
            response = ecs.update_service(
                cluster=ecs_cluster,
                service=service_arn,
                desiredCount=0
            )
            #if DEBUG:   print(json_response(response))
            result['stoppedServices'].append(service_name)
            
def checkECS():
    '''
    Get the tags of each service belonging to the ECS cluster and perform operations on services
    '''

    # Get all services belonging to the ECS cluster
    paginator = ecs.get_paginator('list_services')
    response_iterator = paginator.paginate(cluster=ecs_cluster)
    ecs_services = []
    for page in response_iterator:
        ecs_services.extend(page['serviceArns'])
    
    for service_arn in ecs_services:
        # Get service configuration
        service_name = os.path.basename(service_arn)
        service_config = ecs.describe_services(
            cluster=ecs_cluster,
            services=[service_arn],
            include=['TAGS']
        )

        if DEBUG:   print("\n'{}' service has {} tasks running".format(service_name, service_config['services'][0]['runningCount']))
        if 'tags' in service_config['services'][0]:
            for tag in service_config['services'][0]['tags']:
                if tag['key'] == 'startService':
                    if DEBUG:   print("\nFound a 'startService' tag on '" + service_name + "' service")
                    cronECSExec(tag['value'], service_arn, service_name, service_config, 'start')
            
                if tag['key'] == 'stopService':
                    if DEBUG:   print("\nFound a 'stopService' tag on '" + service_name + "' service")
                    cronECSExec(tag['value'], service_arn, service_name, service_config, 'stop')
                    
    return True

def lambda_handler(event, context):
    print("\n##### Starting execution #####\n")
    
    try:
        checkECS()

        print("\nFinal result:\n" + json_response(result) + "\n")
        print("\n##### Execution finished #####\n")
        return {
            'statusCode': 200,
            'body': json_response(result)
        }
    except Exception as e:
        print(str(e))
        print("\n##### Execution failed #####\n")
        raise
