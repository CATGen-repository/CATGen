package org.utbench.productline.http;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.utbench.productline.dto.PostDTO;
import org.utbench.productline.exception.CommonException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Service
public class RestTemplateService {
    private final RestTemplate restTemplate;

    @Value("iamUrl")
    private String iamUrl;
    ResponseEntity<Map> mapResponseEntity;

    private static final String GET_TOKEN_URI = "/auth/token";

    private static final String GET_TOKEN_FORMAT
        = "{\"auth\":{\"identity\":{\"password\":{\"user\":{\"password\":\"%s\",\"domain\":{\"name\":\"%s\"},\"name\":\"%s\"}},\"methods\":[\"password\"]}}}";

    public RestTemplateService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public boolean postForEntry(String uri, String action, String name) throws CommonException {
        ResponseEntity<Map> mapResponseEntity;
        try {
            mapResponseEntity = restTemplate.postForEntity(iamUrl + uri,
                PostDTO.builder().action(action).name(name).build(), Map.class);
        } catch (RestClientException exception) {
            throw new CommonException("Invoke iam failed,", "err.1001");
        }
        if (mapResponseEntity == null) {
            throw new CommonException("Response from IAM is null,", "err.1002");
        }
        return Optional.ofNullable(mapResponseEntity.getBody())
            .map(item -> "ok".equals(item.get("result"))).orElse(false);
    }
}
