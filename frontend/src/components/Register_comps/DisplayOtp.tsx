import './RegisterMode.css'


interface Props {
  otp: number;
}

function DisplayOtp(props: Props) {

  return (
    <div className='the-box'>
      <h1>OTP: {props.otp}</h1>
    </div>
  )
}

export default DisplayOtp
