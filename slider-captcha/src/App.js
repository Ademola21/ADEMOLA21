import "./styles.css";
import SliderCaptcha from "@slider-captcha/react";

function verifiedCallback(token) {
  console.log("Captcha token: " + token);
}
export default function App() {
  return (
    <div className="App" style={{ paddingTop: 300 }}>
      <SliderCaptcha
        create="https://dev.joobpay.com/api/v1
/auth/captcha/create"
        verify="https://dev.joobpay.com/api/v1
/auth/captcha/verify"
        callback={verifiedCallback}
      />
    </div>
  );
}
