import api from '../api';
import './TabHolder.css';
import { useState } from 'react';

function TextBlast() {

  const [message, setMessage] = useState("");

  const sendblast = async () => {
    alert("Message Will Take 5-10 Minutes to Send to All Recruits! Please Do Not Press Submit Multiple Times!");
    console.log(message);
    try {
      const response = await api.post('/TextBlast', {message: message});
      console.log('Message sent:', response.data.status);
      
  } catch (error) {
      console.error('Error activating registration mode:', error);
  }
}

  const handleInputChange = (e: any) => {
    setMessage(e.target.value);
  }



  return (
    <div className="tab-content-area">
        <div className="">
          <div>
            <h1>Text Blast</h1>
            <p>Text Blast is a feature that allows you to send a text message to a group of people at once.</p>
        </div>
          <div>
            <form>
              <div className="mb-3">
                <label htmlFor="textblast" className="form-label">Your Message</label>
                <textarea className="form-control" id="textblast" rows={3} value={message} onChange={handleInputChange}></textarea>
                <div id="emailHelp" className="form-text">Ensure no spelling mistakes and keep the message short and simple!</div> 
              </div>
              <button onClick={sendblast} type="submit" className="btn btn-primary">Submit</button>
            </form>
          </div>
        </div>

        <br/>
        <br/>
        <br/>

        <div>
          <h2>Text Blast History</h2>
          <table className="table">
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Message</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>12/12/2021</td>
                <td>This is just an example - Reminder to complete the survey</td>
              </tr>
              <tr>
                <td>13/12/2021</td>
                <td>Just prototyping - Reminder to complete the homework</td>
              </tr>
              <tr>
                <td>14/12/2021</td>
                <td>Non Functional Text Blast History - Reminder to complete the survey</td>
              </tr>
            </tbody>
          </table>
        </div>
    </div>
  )
}


export default TextBlast;
