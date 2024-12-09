import './RegisterMode.css';
import { useState } from 'react';
import api from '../../api';
import { useEffect } from 'react';


interface RegisterModeProps {
    onOTPChange: (otp: number) => void;
    previousMode: boolean;
}

function RegisterMode({ previousMode ,onOTPChange }: RegisterModeProps) {

    const [buttonClass, setButtonClass] = useState('button-red');
    const [buttonText, setButtonText] = useState('off');

    useEffect(() => {
        setButtonText(previousMode ? 'Active' : 'Off');
        setButtonClass(previousMode ? 'button-green' : 'button-red');
    }, [previousMode]);

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

        if (buttonText === 'Active') {
            try {
                const response = await api.post('/RegistrationModeOff');
                console.log('Registration mode deactivated: status:', response.data.status);

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
