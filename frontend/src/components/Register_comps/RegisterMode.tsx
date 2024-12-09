import './RegisterMode.css';
import { useState } from 'react';
import api from '../../api';


interface RegisterModeProps {
    onOTPChange: (otp: number) => void;
    previousMode: boolean;
}

function RegisterMode({ previousMode ,onOTPChange }: RegisterModeProps) {
    const bt = previousMode ? 'Active' : 'Off';
    const bc = previousMode ? 'button-green' : 'button-red';


    const [buttonClass, setButtonClass] = useState(bc);
    const [buttonText, setButtonText] = useState(bt);


    const handleButtonClick = async () => {
        
        if (buttonText === 'Off') {
            try {
                const response = await api.post('/RegistrationModeOn');
                const otp = response.data.OTP;
                console.log('OTP:', otp);
                onOTPChange(otp);
                
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
