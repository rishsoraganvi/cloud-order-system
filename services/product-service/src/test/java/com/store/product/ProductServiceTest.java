package com.store.product;

import com.store.product.dto.ProductRequest;
import com.store.product.dto.ProductResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
public class ProductServiceTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    public void testGetProductsPaginated() {
        // Test 1: GET /products returns HTTP 200 with paginated list (page, size params work).
        ResponseEntity<String> response = restTemplate.getForEntity("/products?page=0&size=10", String.class);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertTrue(response.getBody().contains("content"));
    }

    @Test
    public void testGetProductById() {
        // First, create a product
        ProductRequest request = new ProductRequest("Widget", "A useful widget", 9.99, 100);
        ResponseEntity<ProductResponse> createResponse = restTemplate.postForEntity("/products", request, ProductResponse.class);
        assertEquals(HttpStatus.CREATED, createResponse.getStatusCode());
        Integer productId = createResponse.getBody().getId();

        // Test 2: GET /products/{id} returns 200 with product detail for valid id
        ResponseEntity<ProductResponse> response = restTemplate.getForEntity("/products/" + productId, ProductResponse.class);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("Widget", response.getBody().getName());

        // Test 2b: 404 for invalid id
        ResponseEntity<ProductResponse> notFoundResponse = restTemplate.getForEntity("/products/99999", ProductResponse.class);
        assertEquals(HttpStatus.NOT_FOUND, notFoundResponse.getStatusCode());
    }

    @Test
    public void testCreateProduct() {
        // Test 3: POST /products accepts product payload, returns 201
        ProductRequest request = new ProductRequest("Gadget", "A cool gadget", 19.99, 50);
        ResponseEntity<ProductResponse> response = restTemplate.postForEntity("/products", request, ProductResponse.class);
        assertEquals(HttpStatus.CREATED, response.getStatusCode());
        assertNotNull(response.getBody().getId());
        assertEquals("Gadget", response.getBody().getName());
    }

    @Test
    public void testReserveStock() {
        // First, create a product
        ProductRequest request = new ProductRequest("Item", "An item", 5.99, 10);
        ResponseEntity<ProductResponse> createResponse = restTemplate.postForEntity("/products", request, ProductResponse.class);
        Integer productId = createResponse.getBody().getId();
        int initialStock = createResponse.getBody().getStock();

        // Test 4: PUT /products/{id}/reserve with qty=1 decrements stock
        ResponseEntity<ProductResponse> response = restTemplate.exchange(
                "/products/" + productId + "/reserve?qty=1",
                org.springframework.http.HttpMethod.PUT,
                null,
                ProductResponse.class
        );
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(initialStock - 1, response.getBody().getStock());

        // Test 4b: qty > available stock returns 409
        ResponseEntity<String> conflictResponse = restTemplate.exchange(
                "/products/" + productId + "/reserve?qty=100",
                org.springframework.http.HttpMethod.PUT,
                null,
                String.class
        );
        assertEquals(HttpStatus.CONFLICT, conflictResponse.getStatusCode());
        assertTrue(conflictResponse.getBody().contains("INSUFFICIENT_STOCK"));
    }
}
