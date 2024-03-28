import React from "react";

interface Settings {
    commentary: boolean;
    clipLength: number;
    numClips: number;
}

export default class Header extends React.Component {

    render(): React.ReactNode {
        return (
            <header className="dark:bg-gray-800 py-4 rounded-lg shadow m-4">
                <div className="container mx-auto flex justify-evenly items-center">
                    <h1 className="text-gray-400 dark:text-gray-300 text-3xl font-bold text-center">Clipper</h1>
                </div>
            </header>
        );
    }
}
