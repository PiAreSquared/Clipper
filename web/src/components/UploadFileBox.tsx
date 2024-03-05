import React, { useState } from 'react';
import UploadFileConfirm from './UploadFileConfirm.tsx';
import UploadFileModal from './UploadFileModal.tsx';
import UploadFileFinished from './UploadFileFinished.tsx';
import AWS from 'aws-sdk';


export default function UploadFileBox() {
    const [showConfirm, setShowConfirm] = useState(false);
    const [showUploader, setShowUploader] = useState(false);
    const [showUploadedConfirmation, setShowUploadedConfirmation] = useState(false);
    const [numBytesUploaded, setNumBytesUploaded] = useState(0);
    const [file, setFile] = useState(new File([], ''));
    const [last_filename, setLastFilename] = useState('');

    const aws_bucket_info = {
        accessKeyId: process.env.REACT_APP_AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.REACT_APP_AWS_ACCESS_SECRET_KEY,
        Bucket: process.env.REACT_APP_AWS_S3_BUCKET,
        region: process.env.REACT_APP_AWS_REGION,
        ACL: 'public-read'
    };

    console.log(aws_bucket_info);

    AWS.config.update({
        accessKeyId: aws_bucket_info.accessKeyId,
        secretAccessKey: aws_bucket_info.secretAccessKey,
        region: aws_bucket_info.region
    });

    const uploadFile = async (file: File) => {
        const s3 = new AWS.S3({
            accessKeyId: aws_bucket_info.accessKeyId,
            secretAccessKey: aws_bucket_info.secretAccessKey,
            region: aws_bucket_info.region
        });

        const params: AWS.S3.CreateMultipartUploadRequest = {
            Bucket: aws_bucket_info.Bucket,
            // ACL: aws_bucket_info.ACL,
            Key: file.name,
            ContentType: file.type
        };

        s3.createMultipartUpload(params, (err, data) => {
            if (err) {
                console.error(err);
            } else {
                const uploadId = data.UploadId ?? '';
                const partSize = 5 * 1024 * 1024; // 5MB

                const numParts = Math.ceil(file.size / partSize);
                const partPromises: Promise<AWS.S3.UploadPartOutput>[] = [];

                for (let partNumber = 1; partNumber <= numParts; partNumber++) {
                    const start = (partNumber - 1) * partSize;
                    const end = Math.min(start + partSize, file.size);

                    const partParams = {
                        Bucket: aws_bucket_info.Bucket,
                        Key: file.name,
                        PartNumber: partNumber,
                        UploadId: uploadId,
                        Body: file.slice(start, end)
                    };

                    const partPromise = s3.uploadPart(partParams).promise();
                    partPromise.then((data) => {
                        setNumBytesUploaded((prev) => prev + partParams.Body.size);
                    });
                    partPromises.push(partPromise);
                }

                Promise.all(partPromises)
                    .then((parts) => {
                        const completeParams = {
                            Bucket: aws_bucket_info.Bucket,
                            Key: file.name,
                            MultipartUpload: {
                                Parts: parts.map((part, index) => ({
                                    ETag: part.ETag,
                                    PartNumber: index + 1
                                }))
                            },
                            UploadId: uploadId
                        };

                        return s3.completeMultipartUpload(completeParams).promise();
                    })
                    .then((data) => {
                        console.log('File uploaded successfully:', data.Location);
                        setTimeout(() => {
                            finishedUploading();
                        }, 2000);
                    })
                    .catch((err) => {
                        console.error(err);
                    });
            }
        });
    }

    const handleFileUpload = (event) => {
        const file = event.target.files[0];

        // check filetype is mp4
        if (file.type !== 'video/mp4') {
            alert('Please upload a valid MP4 file.');
            return;
        }

        setShowConfirm(true);
        setFile(file);
    };

    const handleConfirm = () => {
        setShowConfirm(false);
        setShowUploader(true);
        uploadFile(file);
    };

    const handleCancel = () => {
        setShowConfirm(false);
        setFile(new File([], ''));
    };

    const finishedUploading = () => {
        setShowUploader(false);
        setLastFilename(file.name);
        setFile(new File([], ''));
        setShowUploadedConfirmation(true);
        setNumBytesUploaded(0);
    }

    return (
        <div className="container mx-auto py-6">
            <div className="max-w-md mx-auto bg-white dark:bg-gray-800 shadow-md rounded-md p-6">
                {/* <h1 className="text-2xl font-bold mb-4 dark:text-white">File Upload</h1> */}
                <form action="/upload" method="post" encType="multipart/form-data">
                    <div>
                        <div className="flex items-center justify-center w-full">
                            <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                    <svg className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                        <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2" />
                                    </svg>
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">MP4, AVI, or MOV (MAX. 5 GB)</p>
                                </div>
                                <input id="dropzone-file" type="file" className="hidden" onChange={handleFileUpload} />
                            </label>
                        </div>
                    </div>
                </form>
            </div>
            {showConfirm && (
                <UploadFileConfirm
                    file={file ?? new File([], '')}
                    onConfirm={handleConfirm}
                    onCancel={handleCancel}
                />
            )}
            {showUploader &&
                <UploadFileModal
                    file={file ?? new File([], '')}
                    bytesUploaded={numBytesUploaded}
                    onComplete={() => {
                        setShowUploader(false);
                        setFile(new File([], ''));
                    }}
                    onError={() => {
                        setShowUploader(false);
                        setFile(new File([], ''));
                    }}
                />
            }
            {showUploadedConfirmation &&
                <UploadFileFinished
                    filename={last_filename}
                    />
            }
        </div>
    );
}