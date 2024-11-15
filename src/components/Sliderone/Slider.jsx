import Carousel from 'react-bootstrap/Carousel';

function Slider() {
  const slides = [
    {
      image: "/sl1.jpg",
      title: "First slide label",
      description: "This is the first slide description.",
    },
    {
      image: "/sl2.jpg",
      title: "Second slide label",
      description: "This is the second slide description.",
    },
    {
      image: "/sl3.jpg",
      title: "Third slide label",
      description: "This is the third slide description.",
    },
    {
      image: "/sl4.jpg",
      title: "Fourth slide label",
      description: "This is the fourth slide description.",
    },
  ];

  return (
    <Carousel
      className="mt-5"
      interval={2000} // Slide interval of 2 seconds
      slide={true} // Enable sliding animation
      controls={false} // Disable next and previous icons
      indicators={false} // Disable slide indicators (dots)
    >
      {slides.map((slide, index) => (
        <Carousel.Item key={index} style={{ transition: 'transform 2s ease-in-out' }}>
          <img
            className="d-block w-100"
            src={slide.image}
            alt={`${slide.title} image`}
            style={{ height: '400px', objectFit: 'cover' }}
          />
          <Carousel.Caption>
            <h3>{slide.title}</h3>
            <p>{slide.description}</p>
          </Carousel.Caption>
        </Carousel.Item>
      ))}
    </Carousel>
  );
}

export default Slider;
