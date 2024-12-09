import RegisterMode from "./Register_comps/RegisterMode"
import DisplayOtp from "./Register_comps/DisplayOtp"
import './TabHolder.css'
import { useState } from 'react';
import api from '../api';

function RegisterRecruits() {

    const [previousmode, setPreviousMode] = useState(false); // State to hold previous mode

    const fetchdata = async () => {
        try {
            const response = await api.post('/RegistrationModeStatus');
            const value = response.data.OTP;
            const mode = response.data.mode;
            console.log('OTP:', value);
            console.log('Mode:', mode);
            setPreviousMode(mode);
        } catch (error) {
            console.error('Error fetching OTP:', error);
        }
    };

    fetchdata();

    const [OTP, setOTP] = useState(0); // State to hold OTP

        // Function to update OTP state
        const handleOTPUpdate = (otp: number) => {
            setOTP(otp); // Update the OTP value in the parent's state
        };

  return (
    <div className="tab-content-area">
        <div className="rm-top">
            <RegisterMode previousMode={previousmode} onOTPChange={handleOTPUpdate}/>
        </div>
        <div className="rm-bottom">
            <DisplayOtp  otp={OTP}/>
        </div>
    </div>
  )
}

export default RegisterRecruits
