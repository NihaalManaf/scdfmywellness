import '../App.css';
import ViewChat from './ViewChat';
import TabHolder from './TabHolder';

function Content() {
  return (
    <div>
      <div className='right-half-box'>
        <ViewChat />
      </div> 
      <div className='left-half-box'>
        <TabHolder />
      </div>
    </div>
  )
}

export default Content
