import React from 'react';
import AWS from 'aws-sdk';
import { useNavigate } from 'react-router-dom';

interface UploadFileFinishedProps {
}

const UploadFileFinished: React.FC<UploadFileFinishedProps> = () => {


    var sqs = new AWS.SQS({apiVersion: '2012-11-05'});

    var params = {
        MaxNumberOfMessages: 1,
        QueueUrl: "https://sqs.us-east-2.amazonaws.com/992382425958/VideoProcessedQueue",
        WaitTimeSeconds: 600,
    };

    sqs.receiveMessage(params, function(err, data) {
        if (err) {
            console.log("Receive Error", err);
        }
        else {
            const sqsMessageObj = JSON.parse(data.Messages[0].Body);
            const messageObj = JSON.parse(sqsMessageObj.Message);
            const key = messageObj.requestPayload.Records[0].s3.object.key;
            var deleteParams = {
                QueueUrl: "https://sqs.us-east-2.amazonaws.com/992382425958/VideoProcessedQueue",
                ReceiptHandle: data.Messages[0].ReceiptHandle
            };
            sqs.deleteMessage(deleteParams, function(err, data) {
                if (err) {
                    console.log("Delete Error", err);
                }
                else {
                    console.log("Message Deleted", data);
                }
                const filename = key.split('.')[0];
                const final = '/highlights/' + filename + '_highlights.mp4';
                const navigate = useNavigate();
                navigate(final);
            });
        }
    });
    


    return (
        <>
            <div className="fixed top-0 right-0 bottom-0 left-0 bg-black opacity-70 z-40"></div>
            <div id="progress-modal" className={`overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full flex`}>
                <div className="relative p-4 w-full max-w-md max-h-full">
                    <div className="relative bg-white rounded-lg shadow dark:bg-gray-700 border-gray-300 dark:border-gray-600 border-2 h-full">
                        <div className="p-4 md:p-6 flex-col justify-items-center items-center justify-evenly flex">
                            <div className="min-h-12 z-10 flex items-center justify-center w-12 h-12 bg-green-600 rounded-full ring-0 ring-white dark:bg-green-900 sm:ring-8 dark:ring-gray-900 shrink-0">
                                <svg className="w-5 h-5 text-green-100 dark:text-green-300" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                                </svg>
                            </div>
                            <h3 className="flex mt-5 text-xl font-bold text-gray-900 dark:text-white">File Upload Finished!</h3>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default UploadFileFinished;



// var bucketName = 'processed-games';

// const aws_bucket_info = {
//     accessKeyId: process.env.AWS_ACCESS_KEY_ID,
//     secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
//     Bucket: bucketName,
//     region: process.env.AWS_REGION,
//     ACL: 'public-read',
// };

// async function retrieveDataFromS3(message: string) {
//     var s3 = new AWS.S3({
//         accessKeyId: aws_bucket_info.accessKeyId,
//         selectAccessKey: aws_bucket_info.secretAccessKey,
//         region: aws_bucket_info.region
//     });
//     var params = {
//         Bucket: 'video-processed-bucket',
//         Key: message,

//     s3.getObject(params, function(err, data) {
//         if (err) {
//             console.log(err, err.stack);
//         }
//         else {
//             console.log(data);
//         }
//     });
// }

// async function retrieveDataFromS3(message: string, file: string) {
//     const client = new AWS.S3Client({});
    //  const sqsMessageObj = JSON.parse(message);
    //  const messageObj = JSON.parse(sqsMessageObj.Message);
    //  const key = messageObj.requestPayload.Records[0].s3.object.key;
//     if (file === key) {

//         const command = new GetObjectCommand({
//             Bucket: bucketName,
//             Key: key,
//         });
//         try {
//             const response = await client.send(command);
//             return response;
//             console.log(response);
//         }
//         catch (err) {
//             console.log(err);
//         }
//     }
//     else {
//         console.log('File not found');
//     }
// }