import './RegisterMode.css'
import { useState } from 'react';

interface Props {
  otp: number;
}

function DisplayOtp(props: Props) {

  return (
    <div className='the-box'>
      <h1>{props.otp}</h1>
    </div>
  )
}

export default DisplayOtp
