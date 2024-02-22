import logo from './logo.svg';
import './App.css';
import UploadFile from './pages/UploadFile.tsx';
import Header from './components/Header.tsx';

function App() {
  return (
      <body className='bg-white dark:bg-gray-900'>
        <Header />
        <UploadFile />
      </body>
  );
}

export default App;
