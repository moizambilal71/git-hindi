// App.jsx
import React from 'react';
import Slider from './components/Sliderone/Slider';
import './components/Sliderone/Slider.css'; 
import FeaturedProductsSwiper from './components/Slider2/FeaturedProductsSwiper';

function App() {
  return (
    <div>
      {/* <h1 class="display-5 text-primary fw-bold text-center mt-2" >Slider Practise</h1> */}
      {/* <Slider className="mt-3"/> */}
      <FeaturedProductsSwiper/>
    </div>
  );
}

export default App;
