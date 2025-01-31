import React, { useEffect, useState } from "react";
import { api } from "../services/api";

const ProductList = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get("/api/products");
        setProducts(response.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchProducts();
  }, []);

  return (
    <div>
      <h2>Products</h2>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            {product.nome_produto} (Quantity: {product.quantidade_produto})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProductList;
