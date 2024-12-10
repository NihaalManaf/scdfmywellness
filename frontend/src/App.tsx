import ViewChat from './components/ViewChat';
import TabHolder from './components/TabHolder';
import './App.css';


function App() {
  return (
    <div>
      <div className='right-half-box'>
        <ViewChat />
      </div> 
      <div className='left-half-box'>
        <TabHolder />
      </div>
      <div className='footer'>
        <h4>Built By Nihaal Manaf</h4>
        <p>To report any bugs or issues, contact me at nihaalmanaf@gmail.com</p>
        <a href='https://www.google.com'>Click here to read the guide to use this platform</a>
      </div>
    </div>
  );
}

export default App;
