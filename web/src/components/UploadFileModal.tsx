import React from 'react';


interface UploadFileConfirmProps {
    file: File;
    bytesUploaded: number;
    onComplete: () => void;
    onError: () => void;
}

const UploadFileConfirm: React.FC<UploadFileConfirmProps> = ({ file, bytesUploaded, onComplete, onError }) => {

    return (
        <>
            <div className="fixed top-0 right-0 bottom-0 left-0 bg-black opacity-70 z-40"></div>
            <div id="progress-modal" className={`overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full flex`}>
                <div className="relative p-4 w-full max-w-md max-h-full">
                    <div className="relative bg-white rounded-lg shadow dark:bg-gray-700">
                        <div className="p-4 md:p-5">
                            <h3 className="mb-1 text-xl font-bold text-gray-900 dark:text-white">Uploading File</h3>
                            <div className="flex justify-between mb-1 text-gray-500 dark:text-gray-400">
                                <span className="text-base font-normal">{file.name}</span>
                                <span className="text-sm font-semibold text-gray-900 dark:text-white">{((bytesUploaded / file.size)*100).toFixed(2)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-600">
                                <div className="bg-orange-500 h-2.5 rounded-full" style={{ width: `${((bytesUploaded / file.size)*100)}%` }}></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default UploadFileConfirm;