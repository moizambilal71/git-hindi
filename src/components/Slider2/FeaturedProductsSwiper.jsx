import React from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/navigation";
import { Navigation } from "swiper/modules";
import './FeaturedProductsSwiper.css';

const FeaturedProductsSwiper = () => {
  const products = [
    { image: "/one.webp", name: "There is some product name", price: "48.99" },
    { image: "/two.webp", name: "There is some product name", price: "14.99" },
    { image: "/three.webp", name: "There is some product name", price: "19.99" },
    { image: "/one.webp", name: "There is some product name", price: "29.99" },
    { image: "/five.webp", name: "There is some product name", price: "34.99" },
    { image: "/six.webp", name: "There is some product name", price: "24.99" },
    { image: "/seven.webp", name: "There is some product name", price: "18.99" },
    { image: "/eight.webp", name: "There is some product name", price: "15.99" },
    { image: "/nine.webp", name: "There is some product name", price: "12.99" },
  ];

  return (
    <div className="m-5 ">
      <div className="container border-0 shadow-sm ">
      <div className="sameColorClass py-4">
      <h2 className="text-center text-bold fw-bold sameColorClass">Today's Featured Products</h2>
      </div>
       
        <div className="position-relative">
          {/* Navigation Buttons */}
          <div className="swiper-button-prev custom-nav">
            <i className="fa fa-chevron-left fs-6"></i>{" "}
            {/* Use fs-6 for a smaller icon size */}
          </div>
          <div className="swiper-button-next custom-nav">
            <i className="fa fa-chevron-right fs-6"></i>
          </div>

          <Swiper
            slidesPerView={7}
            spaceBetween={20}
            navigation={{
              nextEl: ".swiper-button-next",
              prevEl: ".swiper-button-prev",
            }}
            modules={[Navigation]}
            breakpoints={{
              0: { slidesPerView: 2, spaceBetween: 5 },
              576: { slidesPerView: 2, spaceBetween: 8 },
              768: { slidesPerView: 4, spaceBetween: 10 },
              1024: { slidesPerView: 7, spaceBetween: 12 },
            }}
            loop
            speed={600}
            className="mx-3"
          >
            {products.map((product, index) => (
              <SwiperSlide key={index}>
                <div className="card border-0 shadow-sm text-center p-2 mb-4">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="card-img-top rounded mb-2"
                  />
                  {/* <h5 className="card-title mb-1 fw-bold"></h5> */}
                  <p className="fw-semibold sameColorClass" >{product.name}</p>
                  <p className="fw-bold changTextColor" >${product.price}</p>
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        </div>
      </div>
    </div>
  );
};

export default FeaturedProductsSwiper;
