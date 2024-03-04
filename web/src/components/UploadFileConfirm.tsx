import React, { useState } from 'react';

interface UploadFileConfirmProps {
    file: File;
    onConfirm: () => void;
    onCancel: () => void;
}

const UploadFileConfirm: React.FC<UploadFileConfirmProps> = ({ file, onConfirm, onCancel }) => {
    const [uploadConfirmed, setUploadConfirmed] = useState(false);
    const [modalOpen, setModalOpen] = useState(true);

    if (file.size > 5 * 1024 * 1024 * 1024) {
        return (
            <div className="border border-red-300 rounded p-4">
                <div className="text-red-700">
                    File size exceeds 5GB. Please upload a smaller file.
                </div>
            </div>
        );
    }

    else if (file.size === 0) {
        return (
            <div className="border border-red-300 rounded p-4">
                <div className="text-red-700">
                    File is empty. Please upload a non-empty file.
                </div>
            </div>
        );
    }

    let size;
    let unit;

    if (file.size > 1 * 1024 * 1024 * 1024) {
        size = (file.size / (1024 * 1024 * 1024)).toFixed(2);
        unit = 'GB';
    } else if (file.size > 1 * 1024 * 1024) {
        size = (file.size / (1024 * 1024)).toFixed(2);
        unit = 'MB';
    } else if (file.size > 1 * 1024) {
        size = (file.size / (1024)).toFixed(2);
        unit = 'KB';
    } else {
        size = file.size;
        unit = 'B';
    }


    const handleConfirmUpload = () => {
        // Perform upload logic here
        setUploadConfirmed(true);
        onConfirm();
    };

    const handleCancelUpload = () => {
        // Handle cancellation logic here
        setUploadConfirmed(false);
        setModalOpen(false);
        onCancel();
    };

    return (
        <>
            {modalOpen && (
                <div className="fixed top-0 right-0 bottom-0 left-0 bg-black opacity-70 z-40"></div>
            )}
            modalOpen ?
            <div id="progress-modal" className={`overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full ${modalOpen ? 'flex' : 'hidden'}`}>
                <div className="relative p-4 w-full max-w-md max-h-full">
                    {/* Modal content */}
                    <div className="relative bg-white rounded-lg shadow dark:bg-gray-700">
                        <button type="button" className="absolute top-3 end-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white" onClick={() => handleCancelUpload()}>
                            <svg className="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                            </svg>
                            <span className="sr-only">Close modal</span>
                        </button>
                        <div className="p-4 md:p-5">
                            <h3 className="mb-1 text-xl font-bold text-gray-900 dark:text-white">Confirm Video Upload</h3>
                            <p className="text-gray-500 dark:text-gray-400 mb-6">Is this the video file you want to upload?</p>
                            <div className="flex justify-between mb-1 text-gray-500 dark:text-gray-400">
                                <span className="text-base font-normal">{file.name}</span>
                                <span className="text-sm font-semibold text-gray-900 dark:text-white">{size} {unit}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-600">
                                <div className="bg-orange-500 h-2.5 rounded-full" style={{ width: '0%' }}></div>
                            </div>
                            {/* Modal footer */}
                            <div className="flex items-center justify-between mt-6">
                                <button
                                    data-modal-hide="progress-modal"
                                    type="button"
                                    className="py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
                                    onClick={() => handleCancelUpload()}
                                >
                                    Cancel
                                </button>
                                <button
                                    data-modal-hide="progress-modal"
                                    type="button"
                                    className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                                    onClick={() => handleConfirmUpload()}
                                >
                                    Start Upload
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            : null
        </>
    );
};

export default UploadFileConfirm;