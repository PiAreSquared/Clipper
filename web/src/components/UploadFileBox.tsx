import React, { useState } from 'react';
import UploadFileConfirm from './UploadFileConfirm.tsx';
import UploadFileModal from './UploadFileModal.tsx';
import UploadFileFinished from './UploadFileFinished.tsx';
import Timeline from './Timeline.tsx';
import SettingsModal from "./SettingsModal.tsx";
import { IoIosOptions } from "react-icons/io";
import AWS from 'aws-sdk';

interface Settings {
    commentary: boolean;
    clipLength: number;
    numClips: number;
}

export default function UploadFileBox() {
    const [showConfirm, setShowConfirm] = useState(false);
    const [showUploader, setShowUploader] = useState(false);
    const [showUploadedConfirmation, setShowUploadedConfirmation] = useState(false);
    const [numBytesUploaded, setNumBytesUploaded] = useState(0);
    const [file, setFile] = useState(new File([], ''));
    const [last_filename, setLastFilename] = useState('');
    const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
    const [settings, setSettings] = useState({
        commentary: false,
        clipLength: 15,
        numClips: 15
    });

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
        const url = "https://5oj6468sdb.execute-api.us-east-1.amazonaws.com"
        
        const response = await fetch(`${url}/start_upload?filename=${file.name}`);
        const data = await response.json();
        console.log("data from start_upload", data);
        const { upload_id, key } = data;
        const s3_object_key = key ?? '';


        const s3 = new AWS.S3({
            accessKeyId: aws_bucket_info.accessKeyId,
            secretAccessKey: aws_bucket_info.secretAccessKey,
            region: aws_bucket_info.region
        });

        const uploadId = upload_id ?? '';
        const partSize = 5 * 1024 * 1024; // 5MB

        const numParts = Math.ceil(file.size / partSize);
        const partPromises: Promise<AWS.S3.UploadPartOutput>[] = [];

        console.log(uploadId, s3_object_key)

        for (let partNumber = 1; partNumber <= numParts; partNumber++) {
            const start = (partNumber - 1) * partSize;
            const end = Math.min(start + partSize, file.size);

            const partParams = {
                Bucket: aws_bucket_info.Bucket,
                Key: s3_object_key,
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
                    Key: s3_object_key,
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

                fetch(`${url}/clip`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        filename: s3_object_key,
                        commentary: settings.commentary ? "true" : "false",
                        clip_length: settings.clipLength,
                        number_of_clips: settings.numClips
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Clip request sent:', data);
                    })
                    .catch(error => {
                        window.alert('Error request. Please try again.');
                        console.error('Error sending clip request:', error);
                    });
                    
                setTimeout(() => {
                    finishedUploading(s3_object_key);
                }, 2000);
            })
            .catch((err) => {
                console.error(err);
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

    const finishedUploading = (filename) => {
        setShowUploader(false);
        setLastFilename(filename);
        setFile(new File([], ''));
        setShowUploadedConfirmation(true);
        setNumBytesUploaded(0);
    }

    const handleSettingsButtonClick = () => {
        setIsSettingsModalOpen(true);
    };

    const handleSettingsModalClose = () => {
        setIsSettingsModalOpen(false);
    };
    
    const handleSettingsModalSave = (settings_: Settings) => {
        setSettings(settings_);
    };

    return (
        !showUploadedConfirmation ? <div className="container mx-auto py-6">
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
                <div className="flex items-center justify-center pt-4">
                    <button className="text-gray-400 dark:text-gray-300 hover:text-gray-500 dark:hover:text-gray-400 relative flex items-center hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full px-3 py-2"
                            onClick={handleSettingsButtonClick}>
                        <IoIosOptions className="h-6 w-6" /> <span className="ml-2 text-gray-900 dark:text-white">OPTIONS</span>
                    </button>
                </div>
            </div>
            {
                isSettingsModalOpen && <SettingsModal onClose={handleSettingsModalClose} onSave={handleSettingsModalSave} />
            }
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
            {/* {showUploadedConfirmation &&
                // <UploadFileFinished
                //     filename={last_filename}
                //     />
            } */}
        </div> :
        <Timeline filename={last_filename} />
    );
}