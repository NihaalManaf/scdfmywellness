import './RegisterMode.css'
import React, { useState } from 'react';

function DisplayOtp() {
  const [otp, setOpt] = useState('Click Active to generate OTP');
  return (
    <div className='the-box'>
      <h1>{otp}</h1>
    </div>
  )
}

export default DisplayOtp
