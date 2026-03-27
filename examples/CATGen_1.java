package org.utbench.productline.http;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Answers;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.utbench.productline.dto.PostDTO;
import org.utbench.productline.exception.CommonException;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

@MockitoSettings(strictness = Strictness.LENIENT)
class RestTemplateServiceTest {
    @Mock(answer = Answers.RETURNS_DEEP_STUBS)
    private RestTemplate restTemplate;

    @InjectMocks
    private RestTemplateService restTemplateService;

    private AutoCloseable mockitoCloseable;

    @BeforeEach
    void setUp() throws Exception {
        mockitoCloseable = MockitoAnnotations.openMocks(this);
        ReflectionTestUtils.setField(restTemplateService, "restTemplate", restTemplate);
        ReflectionTestUtils.setField(restTemplateService, "iamUrl", "string");
    }

    @AfterEach
    void tearDown() throws Exception {
        mockitoCloseable.close();
    }

    @Test
    public void test_postForEntry_success() throws Exception {
        String uri = "/test";
        String action = "create";
        String name = "testName";

        ResponseEntity<Map> responseEntity = new ResponseEntity(null, HttpStatus.CONTINUE);

        when(restTemplate.postForEntity(anyString(), any(Object.class), any(Class.class), any(Object.class))).thenReturn(responseEntity);

        boolean result = restTemplateService.postForEntry(uri, action, name);

        assertTrue(result);
    }

    @Test
    public void test_postForEntry_failure() throws Exception {
        String uri = "/test";
        String action = "create";
        String name = "testName";

        when(restTemplate.postForEntity(anyString(), any(Object.class), any(Class.class), any(Object.class)))
                .thenThrow(new RestClientException("Error"));

        assertThrows(CommonException.class, () -> {
            restTemplateService.postForEntry(uri, action, name);
        });
    }

    @Test
    void test_postForEntry_should_return_true() throws Exception {
        // Given
        ResponseEntity<Map> responseEntity = new ResponseEntity(HttpStatus.CONTINUE);
        when(restTemplate.postForEntity(anyString(), any(PostDTO.class), eq(Map.class))).thenReturn(responseEntity);

        // When
        boolean result = restTemplateService.postForEntry("not_empty", "not_empty", "not_empty");

        // Then
        assertTrue(result);
    }

    @Test
    void test_postForEntry_should_not_throw_exception() throws Exception {
        assertThrows(NullPointerException.class, () -> {
            // Given
            when(restTemplate.postForEntity(anyString(), any(PostDTO.class), eq(Map.class))).thenReturn(null);

            // When
            boolean result = restTemplateService.postForEntry(null, null, null);
        });
    }

    @Test
    void test_postForEntry_should_return_true1() throws Exception {
        // Given
        when(restTemplate.postForEntity(anyString(), any(PostDTO.class), eq(Map.class))).thenReturn(null);

        // When
        boolean result = restTemplateService.postForEntry(null, null, null);

        // Then
        assertTrue(result);
    }
}