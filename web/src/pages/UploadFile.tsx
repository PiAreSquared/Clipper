import React from "react";
import UploadFileBox from "../components/UploadFileBox.tsx";

export default function UploadFile() {
  return (
    <>
        {/* <div className="container mx-auto py-8">
          <h1 className="text-2xl font-bold mb-4 dark:text-white">Usage</h1>
          <div className="grid grid-cols-4 gap-4">
            <div className="flex items-center">
              <div className="flex flex-col items-center">
                <span className="flex items-center justify-center w-8 h-8 bg-indigo-500 text-white rounded-full text-base">1</span>
                <p className="mb-2 text-white text-base">Upload your sports game video</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="flex flex-col items-center">
                <span className="flex items-center justify-center w-8 h-8 bg-indigo-500 text-white rounded-full text-base">2</span>
                <p className="mb-2 text-white text-base">Choose your highlight reel options</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="flex flex-col items-center">
                <span className="flex items-center justify-center w-8 h-8 bg-indigo-500 text-white rounded-full text-base">3</span>
                <p className="mb-2 text-white text-base">Wait for the analysis to complete</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="flex flex-col items-center">
                <span className="flex items-center justify-center w-8 h-8 bg-indigo-500 text-white rounded-full text-base">4</span>
                <p className="mb-2 text-white text-base">Download the generated game highlights reel</p>
              </div>
            </div>
          </div>
      </div> */}
      <UploadFileBox />
    </>
  );
}