import React from "react";

export default class Header extends React.Component {
    render(): React.ReactNode {
        return (
        <header className="bg-indigo-900 py-4">
                <div className="container mx-auto">
                    <h1 className="text-white text-3xl font-bold text-center">AI Sports Reels</h1>
                </div>
            </header>
    );
    }
}
