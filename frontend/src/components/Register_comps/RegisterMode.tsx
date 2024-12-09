import './RegisterMode.css';
import { useState } from 'react';
import api from '../../api';

function RegisterMode() {
    const [buttonClass, setButtonClass] = useState('button-red');
    const [buttonText, setButtonText] = useState('Off');

    const handleButtonClick = async () => {
        
        if (buttonText === 'Off') {
            try {
                const response = await api.post('/RegistrationModeOn');
                const otp = response.data.otp;
                console.log('OTP:', otp);
            } catch (error) {
                console.error('Error activating registration mode:', error);
            }
        }

        setButtonClass(buttonClass === 'button-red' ? 'button-green' : 'button-red');
        setButtonText(buttonText === 'Off' ? 'Active' : 'Off');
    };

    return (
        <div className='rm'>
            <div >
                <h1 className='rm-title'>Registration Mode</h1>
            </div>
            <div className='rm-buttons'>
                <button onClick={handleButtonClick} className={buttonClass}>{buttonText}</button>
            </div>
        </div>
    )
}

export default RegisterMode
