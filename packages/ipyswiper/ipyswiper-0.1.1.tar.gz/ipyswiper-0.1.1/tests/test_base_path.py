from ipyswiper import IpySwiper

def test_base_path():
    images = [
        {"label": "Image 1", "image": "image1.jpg"},
        {"label": "Image 2", "image": "/abs/path/image2.jpg"},
    ]
    swiper = IpySwiper(images, base_path="/my/base/path")
    assert swiper.images[0]["image"] == "/my/base/path/image1.jpg"
    assert swiper.images[1]["image"] == "/abs/path/image2.jpg"
