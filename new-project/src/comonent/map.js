import React from "react";
import "./onesoil.css";
import App from "../App";



function Map() {
    return (
        <div className="map">
            <iframe title="hel"
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d924237.7100743718!2d66.49593735743672!3d25.192983608402326!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3eb33e06651d4bbf%3A0x9cf92f44555a0c23!2sKarachi%2C%20Karachi%20City%2C%20Sindh%2C%20Pakistan!5e0!3m2!1sen!2s!4v1701108625422!5m2!1sen!2s"
                width="850"
                height="640"
                style={{ border: 0 }}
                allowfullscreen=""
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
            ></iframe>
        </div>
    );
}
export default Map;