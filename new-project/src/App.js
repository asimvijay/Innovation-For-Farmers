
import './App.css';
import Onesoil from './comonent/onesoil';
import Map from './comonent/map'
import React, { useEffect, useState } from 'react';


function App() {
  const [data, setData] = useState({})
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/data')
      const jsonData = await response.json();
      setData(jsonData)     
    }catch(error){console.log('Error', error)}
}


  return (
    <div className="App">
      <Onesoil />
      <Map />
    <h1>{data.messege}</h1>
    </div>
  );
}

export default App;
