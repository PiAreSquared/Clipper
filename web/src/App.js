import logo from './logo.svg';
import './App.css';
import UploadFile from './pages/UploadFile.tsx';
import Header from './components/Header.tsx';
import Footer from './components/Footer.tsx';
import VideoHighlights from './components/ViewHighlights.tsx';
import {Routes, Route} from 'react-router-dom';

function App() {
  return (
      <div className='bg-white dark:bg-gray-900' style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
          <div style={{ flex: 1 }}>
            <Routes>
              <Route path="/" element={<UploadFile />} />
              <Route path="/highlights/:video_key" element={<VideoHighlights />} />
            </Routes>
          </div>
        <Footer />
      </div>
  );
}

export default App;
