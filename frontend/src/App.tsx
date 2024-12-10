import Footer from './components/Footer';
import Content from './components/Content';
import './App.css';


function App() {
  return (
  <div className='layout'>
    <div className='App'>
      <Content />
    </div>
    <div className='footers'>
      <Footer />
    </div>
  </div>
  );
}

export default App;
