/**
 * Created by glucio on 7/5/17.
 * Default lambda-toolkit proxy to JS projects.
 */
var AWS = require('aws-sdk');
var sqs = new AWS.SQS({region : process.env.AWS_REGION});

exports.handler = function(event, context, callback) {
    var output = {};
    output['event'] = JSON.stringify(event);
    output['context'] = JSON.stringify(context);

    var params = {
        QueueName: 'TEMPLATEQUEUENAME'
    };
    sqs.getQueueUrl(params, function(err, data) {
        if (err) console.log(err, err.stack);
        else {
            var params = {
                MessageBody: JSON.stringify(output),
                QueueUrl: data.QueueUrl,
                MessageDeduplicationId: context.awsRequestId,
                MessageGroupId: 'sameallthetime'
            };
            sqs.sendMessage(params, function(err, data) {
                if (err) console.log(err, err.stack);
            });
        }
    });
};