/**
 * Created by glucio on 7/5/17.
 * Default lambda JS project.
 */
var AWS = require('aws-sdk');

exports.handler = function(event, context, callback) {

    console.log("Hi, I'm here. Lambda-proxy is working. =)");
    console.log("AWS Event ID: " + context.awsRequestId);
    console.log("Event Body: " + JSON.stringify(event));


    /* NodeJS v0.10.42
     context.succeed("Done"); */

    /* NodeJS v4.3 or v6.10 */
    context.callbackWaitsForEmptyEventLoop = false;
    callback(null, true);
};