import RegisterMode from "./Register_comps/RegisterMode"
import DisplayOtp from "./Register_comps/DisplayOtp"
import './TabHolder.css'

function RegisterRecruits() {
  return (
    <div className="tab-content-area">
        <div className="rm-top">
            <RegisterMode />
        </div>
        <div className="rm-bottom">
            <DisplayOtp />
        </div>
    </div>
  )
}

export default RegisterRecruits
