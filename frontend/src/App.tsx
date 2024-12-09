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
        <h1>Footer goes here</h1>
      </div>
    </div>
  );
}

export default App;
