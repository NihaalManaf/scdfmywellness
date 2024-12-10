import Footer from './components/Footer';
import Content from './components/Content';
import './App.css';


function App() {
  let password = localStorage.getItem('tmp::voice_api_key') || '';
  while (password !== 'SCDF101010$#$') {
    password = prompt('Password please') || '';
  }
  localStorage.setItem('tmp::voice_api_key', password);

  return (
  <div className='layout'>
    <div className='App'>
      <Content />
    </div>
    <div >
      <Footer />
    </div>
  </div>
  );
}

export default App;
