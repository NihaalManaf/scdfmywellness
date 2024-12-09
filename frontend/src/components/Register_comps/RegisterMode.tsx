import './RegisterMode.css';
import { useState } from 'react';

function RegisterMode() {
    const [buttonClass, setButtonClass] = useState('button-red');
    const [buttonText, setButtonText] = useState('Off');

    const handleButtonClick = () => {
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
