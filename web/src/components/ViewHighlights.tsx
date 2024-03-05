import React from "react";
import AWS from "aws-sdk";
import { useParams } from 'react-router-dom'

interface ViewHighlightsProps {
    bucket_name: string;
}


const ViewHighlights: React.FC<ViewHighlightsProps> = ({ bucket_name = "processed-games" }) => {
    const [url, setUrl] = React.useState("");
    const { video_key } = useParams();

    const getVideo = () => {
        const aws_bucket_info = {
            accessKeyId: process.env.REACT_APP_AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.REACT_APP_AWS_ACCESS_SECRET_KEY,
            Bucket: process.env.REACT_APP_AWS_S3_BUCKET,
            region: process.env.REACT_APP_AWS_REGION,
            ACL: 'public-read'
        };

        AWS.config.update({
            accessKeyId: aws_bucket_info.accessKeyId,
            secretAccessKey: aws_bucket_info.secretAccessKey,
            region: aws_bucket_info.region
        });

        const s3 = new AWS.S3({
            accessKeyId: process.env.REACT_APP_AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.REACT_APP_AWS_SECRET_ACCESS_KEY,
            region: process.env.REACT_APP_AWS_REGION
        });
        console.log(video_key)
        const params: AWS.S3.GetObjectRequest = {
            Bucket: bucket_name,
            Key: video_key ?? "",
        };
        
        const url = s3.getSignedUrlPromise("getObject", params).then((url) => {
            setUrl(url);
        });
    }

    getVideo();

    return (
            <div className="container mx-auto py-8 flex justify-center items-center flex-col">
                <iframe title="highlights-clip" src={url} width={1280} height={720} allowFullScreen></iframe>
            </div>
            
        );
}
export default ViewHighlights;