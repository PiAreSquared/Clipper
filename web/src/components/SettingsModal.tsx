import React, { useState } from 'react';

interface SettingsModalProps {
    settings: Settings
    onClose: () => void;
    onSave: (settings: Settings) => void;
}

interface Settings {
    commentary: boolean;
    clipLength: number;
    numClips: number;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ settings, onClose, onSave }) => {
    const [commentary, setCommentary] = useState(settings.commentary);
    const [clipLength, setClipLength] = useState(settings.clipLength);
    const [numClips, setNumClips] = useState(settings.numClips);

    const handleSave = () => {
        const settings: Settings = {
            commentary,
            clipLength,
            numClips
        };
        onSave(settings);
        onClose();
    };

    return (
        <>
            <div className="fixed top-0 right-0 bottom-0 left-0 bg-black opacity-70 z-40"></div>
            <div className={`overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full flex`}>
                <div className="relative p-4 w-full max-w-md max-h-full">
                    <div className="relative bg-white rounded-lg shadow dark:bg-gray-800">
                        <div className="p-4 md:p-5">
                            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white text-center">Options</h2>
                            <label className="flex items-center mb-2 max-w-xs mx-auto">
                                <label className="switch mr-2">
                                    <input
                                        type="checkbox"
                                        checked={commentary}
                                        onChange={(e) => setCommentary(e.target.checked)}
                                        className='sr-only peer'
                                    />
                                    <div className="relative w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-focus:ring-4 peer-focus:ring-indigo-300 dark:peer-focus:ring-indigo-800 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-600"></div>
                                    <span className="slider"></span>
                                </label>
                                <span className='text-gray-900 dark:text-white'>Include Commentary</span>
                            </label>
                            <div className="mb-2 mx-auto max-w-xs">
                                <label className="mb-2 text-gray-900 dark:text-white block">Clip Length (seconds):</label>
                                <div className="relative flex items-center max-w-[8rem]">
                                    <button 
                                        type="button" 
                                        id="decrement-button" 
                                        data-input-counter-decrement="clip-length-input" 
                                        className="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-s-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none"
                                        onClick={() => setClipLength(clipLength - 1)}
                                        >
                                        <svg className="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 1h16" />
                                        </svg>
                                    </button>
                                    <input
                                        type="text"
                                        id="clip-length-input"
                                        data-input-counter
                                        min={5}
                                        max={30}
                                        className="bg-gray-50 border-x-0 border-gray-300 h-11 text-center text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-full py-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        value={clipLength}
                                        onChange={(e) => setClipLength(Number(e.target.value))}
                                        required />
                                    <button 
                                        type="button" 
                                        id="increment-button" 
                                        data-input-counter-increment="clip-length-input" 
                                        className="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-e-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none"
                                        onClick={() => setClipLength(clipLength + 1)}
                                        >
                                        <svg className="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
                                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 1v16M1 9h16" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div className="mb-2 mx-auto max-w-xs">
                                <label className="mb-2 text-gray-900 dark:text-white">Number of Clips:</label>
                                <div className="relative flex items-center max-w-[8rem]">
                                    <button 
                                        type="button" 
                                        id="decrement-button" 
                                        data-input2-counter-decrement="clip-count-input" 
                                        className="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-s-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none"
                                        onClick={() => setNumClips(numClips - 1)}
                                        >
                                        <svg className="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 1h16" />
                                        </svg>
                                    </button>
                                    <input
                                        type="text"
                                        id="clip-count-input"
                                        data-input2-counter
                                        min={1}
                                        max={10}
                                        className="bg-gray-50 border-x-0 border-gray-300 h-11 text-center text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-full py-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        value={numClips}
                                        onChange={(e) => setNumClips(Number(e.target.value))}
                                        required />
                                    <button 
                                    type="button" 
                                    id="increment-button" 
                                    data-input2-counter-increment="clip-count-input" 
                                    className="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-e-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none"
                                    onClick={() => setNumClips(numClips + 1)}
                                    >
                                        <svg className="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
                                            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 1v16M1 9h16" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div className="flex justify-center pt-10">
                                <button
                                    onClick={handleSave}
                                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2"
                                >
                                    Save
                                </button>
                                <button
                                    onClick={onClose}
                                    className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default SettingsModal;