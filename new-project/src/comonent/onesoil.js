import React from "react";
import "./onesoil.css";

import Menu from "../comonent/menu.png";
import Home from "../comonent/home.png";
import Sap from "../comonent/map.png";
import Pin from "../comonent/pin.png";
import Ins from "../comonent/insurance.png";
import Mountain from "../comonent/mountain.png";
import Agr from "../comonent/agriculture.png";
import Tata from "../comonent/database.png";
import Cursor from "../comonent/cursor.png";
import Email from "../comonent/email.png";
import App from "../comonent/mobileapp.png";
import Release from "../comonent/release.png";
import User from "../comonent/userguid.png";
import Upload from "../comonent/upload.png";
import Hello from "../comonent/draw.png";
import Calander from "../comonent/calander.png";

function onesoil() {




  return (
    <div className="container">
      <div className="sidebar">
        <div className="firstSide">
          <div className="partone">
            <div className="one">
              <img src={Home} alt="" />
              <a href="/">My Field</a>
            </div>
            <div className="two">
              <img src={Calander} alt="" />
              <a href="/">Season 2023</a>
            </div>
          </div>
          <div className="partone">
            <div className="two1">
              <img src={Mountain} alt="" />
              <a href="/">Fields</a>
            </div>
            <div className="two">
              <img src={Agr} alt="" />
              <a href="/">Crop Rotation</a>
            </div>
            <div className="two">
              <img src={Pin} alt="" />
              <a href="/">Note</a>
            </div>
            <div className="two">
              <img src={Sap} alt="" />
              <a href="/">VRA Map</a>
            </div>
            <div className="two">
              <img src={Ins} alt="" />
              <a href="/">Weather</a>
            </div>
            <div className="two">
              <img src={Tata} alt="" />
              <a href="/">Field Data</a>
            </div>

            <div className="two">
              <img src={Tata} alt="" />
              <a href="/">Import Files</a>
            </div>
          </div>
          <div className="partone">
            <div className="two">
              <img src={Release} alt="" />
              <a href="/">New Releases</a>
            </div>
            <div className="two">
              <img src={User} alt="" />
              <a href="/">User guid</a>
            </div>
            <div className="two">
              <img src={App} alt="" />
              <a href="/">Mobile App</a>
            </div>
            <div className="two">
              <img src={Email} alt="" />
              <a href="/">Email Address</a>
            </div>
          </div>
          <div className="partone"></div>
        </div>
        <div className="secondSide">
          <div className="parttwo">
            <div className="a">
              
              <img className="menu" src={Menu} alt="" />
              <a href="/">Field</a>
            </div>
          </div>
          <div className="parttwo">
            <div className="kk">
              <img src={Cursor} alt="" />
              <h3>
                Select <br></br>field on the map
              </h3>
            </div>
            <div className="p">
              we identified field boundaries on the map <br></br>select ours{" "}
            </div>
            <button className="myButton">Select on map</button>
          </div>

          <div className="parttwo">
            <div className="jj">
              <img src={Hello} alt="" />
              <h3>
                Draw<br></br>your field
              </h3>
            </div>
            <div className="p">
              if our border arean't sufficiently accurate,you <br></br> can
              dalineate the fields your self{" "}
            </div>
            <button className="myButton">Draw Field</button>
          </div>
          <div className="parttwo">
            <div className="jj">
              <img src={Upload} alt="" />
              <h3>
                Upload <br></br>file
              </h3>
            </div>
            <div className="p">
              Upload a file with field information if you have<br></br> one.
            </div>
            <button className="myButton">Upload Image</button>
          </div>
        </div>
      </div>

  
    </div>


    
  );
  }

export default onesoil;
