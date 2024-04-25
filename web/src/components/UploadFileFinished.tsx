import React from 'react';

interface UploadFileFinishedProps {
    filename: string
}

const UploadFileFinished: React.FC<UploadFileFinishedProps> = ({ filename }) => {

    const filename_without_ext = filename.substring(0, filename.lastIndexOf("."))
    const link1 = `/highlights/${filename_without_ext}_highlights.mp4`
    const link2 = `/commentary/${filename_without_ext}_highlights.mp4`

    const handleOpenLink1 = () => {
        window.open(link1, '_blank');
    };

    const handleOpenLink2 = () => {
        window.open(link2, '_blank');
    };

    return (
        <>
            <div className="fixed top-0 right-0 bottom-0 left-0 bg-black opacity-70 z-40"></div>
            <div id="progress-modal" className={`overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full flex`}>
                <div className="relative p-4 w-full max-w-md max-h-full">
                    <div className="relative bg-white rounded-lg shadow dark:bg-gray-700 border-gray-300 dark:border-gray-600 border-2 h-full">
                        <div className="p-4 md:p-6 flex-col justify-items-center items-center justify-evenly flex">
                            <div className="min-h-12 z-10 flex items-center justify-center w-12 h-12 bg-green-600 rounded-full ring-0 ring-white dark:bg-green-900 sm:ring-8 dark:ring-gray-900 shrink-0">
                                <svg className="w-5 h-5 text-green-100 dark:text-green-300" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                                </svg>
                            </div>
                            <h3 className="flex mt-5 text-xl font-bold text-gray-900 dark:text-white">File Upload Finished!</h3>
                            <button onClick={handleOpenLink1} className="mt-3 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75">View Highlights</button>
                            <button onClick={handleOpenLink2} className="mt-3 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75">View Highlights (with commentary)</button>
                            <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">Note: These links may not work until the video is finished being analyzed!</p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default UploadFileFinished;