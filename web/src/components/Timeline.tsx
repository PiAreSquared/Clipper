import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'

interface TimelineProps {
    filename: string;
}

const Timeline: React.FC<TimelineProps> = ({filename = ""}) => {
    const [uploadedVideo, setUploadedVideo] = useState(false);
    const [generatedHighlights, setGeneratedHighlights] = useState(false);
    const [generatedCommentary, setGeneratedCommentary] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const { video_key } = useParams();

    filename = filename ? filename : (video_key ? video_key : "");

    const url = "https://5oj6468sdb.execute-api.us-east-1.amazonaws.com";

    useEffect(() => {
        fetch(`${url}/status?filename=${filename}`)
                .then(response => response.json())
                .then(data => {
                    setUploadedVideo(false);
                    switch (data.progress) {
                        case 'CLIPPED_WITH_COMMENTARY':
                            setGeneratedCommentary(true);
                        case 'CLIPPED':
                            setGeneratedHighlights(true);
                        case 'UPLOADED':
                            setUploadedVideo(true);
                    }
                    setLoaded(true);
                    console.log('Status:', data.progress)
                })
                .catch(error => {
                    console.error('Error checking status:', error);
                });

        const interval = setInterval(() => {
            fetch(`${url}/status?filename=${filename}`)
                .then(response => response.json())
                .then(data => {
                    setUploadedVideo(false);
                    switch (data.progress) {
                        case 'CLIPPED_WITH_COMMENTARY':
                            setGeneratedCommentary(true);
                        case 'CLIPPED':
                            setGeneratedHighlights(true);
                        case 'UPLOADED':
                            setUploadedVideo(true);
                    }
                    console.log('Status:', data.progress)
                })
                .catch(error => {
                    console.error('Error checking status:', error);
                });
        }, 5000);

        return () => {
            clearInterval(interval);
        };
    }, []);

    return (
        <>
            { loaded &&
            <div className="flex px-52 mt-10">
                <ol className="relative border-s border-gray-200 dark:border-gray-700">
                    {uploadedVideo ?
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-green-200 rounded-full mt-1.5 -start-1.5 border border-green dark:border-green-900 dark:bg-green-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-green-400 dark:text-green-300">COMPLETED</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-500">Uploaded Video</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-600">Your video has been uploaded.</p>
                    </li>
                    :
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -start-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">IN PROGRESS</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Uploading Video</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-400">Your video is currently being uploaded.</p>
                    </li>
                    }
                    {generatedHighlights ? 
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-green-200 rounded-full mt-1.5 -start-1.5 border border-green dark:border-green-900 dark:bg-green-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-green-400 dark:text-green-300">COMPLETED</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-500">Generated Highlights</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-600">We've finished finding the best moments of the game!</p>
                        <a href={`/highlights/${filename}`} className="inline-flex items-center px-4 py-2 mt-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-100 focus:text-blue-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 dark:focus:ring-gray-700">
                            Watch Reel <svg className="w-3 h-3 ms-2 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5h12m0 0L9 1m4 4L9 9"/>
                        </svg></a>
                    </li>
                    : !uploadedVideo ?
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -start-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">QUEUED</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Generating Highlights</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-400">Once the upload completes, we'll get started on finding those highlight-worthy clips for you!</p>
                    </li>
                    :
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -start-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">IN PROGRESS</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Generating Highlights</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-400">Hang on as we scrub through your video to find the best moments!</p>
                    </li>
                    }
                    {generatedCommentary ?
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-green-200 rounded-full mt-1.5 -start-1.5 border border-green dark:border-green-900 dark:bg-green-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-green-400 dark:text-green-300">COMPLETED</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-500">Overlayed Commentary</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-600">We've finished adding commentary for your video.</p>
                        <a href={`/commentary/${filename}`} className="inline-flex items-center px-4 py-2 mt-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-100 focus:text-blue-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 dark:focus:ring-gray-700">
                            Watch Reel <svg className="w-3 h-3 ms-2 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5h12m0 0L9 1m4 4L9 9"/>
                        </svg></a>
                    </li>
                    : !generatedHighlights ?
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -start-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">QUEUED</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Overlaying Commentary</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-400">We'll start adding commentary to your highlights reel once the highlights are ready.</p>
                    </li>
                    :
                    <li className="mb-10 ms-4">
                        <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -start-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
                        <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">IN PROGRESS</time>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Overlaying Commentary</h3>
                        <p className="text-base font-normal text-gray-500 dark:text-gray-400">Hold on! We are preparing some commentary to overlay on your highlights reel.</p>
                    </li>
                    }
                </ol>
            </div>
            }
        </>
    );
};

export default Timeline;