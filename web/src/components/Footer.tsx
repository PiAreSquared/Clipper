import React from "react";

export default class Footer extends React.Component {
    render(): React.ReactNode {
        let aws_branch = "";
        if (process.env.AWS_BRANCH !== undefined) {
            aws_branch = "AWS" + process.env.AWS_BRANCH;
        }

        return (
            <footer className="bg-white rounded-lg shadow m-4 dark:bg-gray-800">
                <div className="w-full mx-auto max-w-screen-xl p-4 md:flex md:items-center md:justify-between">
                    <div>
                        <span className="text-sm text-gray-500 sm:text-center dark:text-gray-400">© 2024 <a href="https://www.google.com" className="hover:underline">Clipper</a>. All Rights Reserved. </span>
                    </div>
                    <div className="flex justify-center">
                        <span className="inline-flex items-center bg-orange-100 text-orange-800 text-xs font-medium px-2.5 py-0.5 rounded-full dark:bg-orange-900 dark:text-orange-300">
                            {process.env.NODE_ENV.toUpperCase()}
                            {/* {process.env} */}
                            {process.env.REACT_APP_REMOTE_CONTAINERS === "true" ? " (devcontainer)" : ""}
                            {aws_branch}
                        </span>
                    </div>
                    <ul className="flex flex-wrap items-center mt-3 text-sm font-medium text-gray-500 dark:text-gray-400 sm:mt-0">
                        <li>
                            <a href="https://www.google.com" className="hover:underline me-4 md:me-6">About</a>
                        </li>
                        <li>
                            <a href="https://www.google.com" className="hover:underline me-4 md:me-6">Privacy Policy</a>
                        </li>
                        <li>
                            <a href="https://www.google.com" className="hover:underline me-4 md:me-6">Licensing</a>
                        </li>
                        <li>
                            <a href="https://www.google.com" className="hover:underline">Contact</a>
                        </li>
                    </ul>
                </div>
            </footer>
        );
    }
}
