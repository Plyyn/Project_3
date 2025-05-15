from dataclasses import dataclass


@dataclass
class ProductData:
    link: str
    name: str
    price: str
    weight: str
    brand: str