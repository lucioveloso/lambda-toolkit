

class LambdaContext:
    def __init__(self, context_json):
        self.aws_request_id = context_json['aws_request_id']
        self.log_stream_name = context_json['log_stream_name']
        self.invoked_function_arn = context_json['invoked_function_arn']
        self.client_context = context_json['client_context']
        self.log_group_name = context_json['log_group_name']
        self.function_name = context_json['function_name']
        self.function_version = context_json['function_version']
        self.identity = context_json['aws_request_id']
        self.memory_limit_in_mb = context_json['memory_limit_in_mb']

    def get_remaining_time_in_millis(self):
        return 50000