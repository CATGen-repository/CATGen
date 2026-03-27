package org.utbench.productline.basic.controlflow;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mockStatic;

@MockitoSettings(strictness = Strictness.LENIENT)
class LoopExampleTest {
    private AutoCloseable mockitoCloseable;

    @BeforeEach
    void setUp() throws Exception {
        mockitoCloseable = MockitoAnnotations.openMocks(this);
    }

    @AfterEach
    void tearDown() throws Exception {
        mockitoCloseable.close();
    }

    @Test
    public void test_checkUserConfig_with_empty_json() throws Exception {
        try (MockedStatic<StringUtils> stringUtilsMock = mockStatic(StringUtils.class)) {
            stringUtilsMock.when(() -> StringUtils.isBlank(any(CharSequence.class))).thenReturn(true);
            assertFalse(LoopExample.checkUserConfig(""));
        }
    }

    @Test
    public void test_checkUserConfig_without_user_config() throws Exception {
        try (MockedStatic<StringUtils> stringUtilsMock = mockStatic(StringUtils.class)) {
            stringUtilsMock.when(() -> StringUtils.isBlank(any(CharSequence.class))).thenReturn(false);
            JSONArray jsonArray = new JSONArray();
            jsonArray.add(new JSONObject());
            assertFalse(LoopExample.checkUserConfig(jsonArray.toJSONString()));
        }
    }

    @Test
    public void test_checkUserConfig_with_user_config_but_no_matching_keys() throws Exception {
        try (MockedStatic<StringUtils> stringUtilsMock = mockStatic(StringUtils.class)) {
            stringUtilsMock.when(() -> StringUtils.isBlank(any(CharSequence.class))).thenReturn(false);
            JSONArray jsonArray = new JSONArray();
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("USER_CONFIG", new JSONArray());
            jsonArray.add(jsonObject);
            assertFalse(LoopExample.checkUserConfig(jsonArray.toJSONString()));
        }
    }

    @Test
    public void test_checkUserConfig_with_user_config_and_matching_keys() throws Exception {
        try (MockedStatic<StringUtils> stringUtilsMock = mockStatic(StringUtils.class)) {
            stringUtilsMock.when(() -> StringUtils.isBlank(any(CharSequence.class))).thenReturn(false);
            JSONArray jsonArray = new JSONArray();
            JSONObject jsonObject = new JSONObject();
            JSONArray userConfigArray = new JSONArray();
            JSONObject userConfigObject = new JSONObject();
            userConfigObject.put("token", "value");
            userConfigArray.add(userConfigObject);
            jsonObject.put("USER_CONFIG", userConfigArray);
            jsonArray.add(jsonObject);
            assertTrue(LoopExample.checkUserConfig(jsonArray.toJSONString()));
        }
    }

    @Test
    void test_checkUserConfig_should_not_throw_exception() throws Exception {
        assertThrows(NullPointerException.class, () -> {
            try (MockedStatic<JSON> mockedStaticJSON = mockStatic(JSON.class, RETURNS_DEEP_STUBS)) {
                // Given
                mockedStaticJSON.when(() -> JSON.parseArray(anyString())).thenReturn(null);

                // When
                boolean result = LoopExample.checkUserConfig(null);
            }
        });
    }

    @Test
    void test_checkUserConfig_should_return_true6() throws Exception {
        try (MockedStatic<JSON> mockedStaticJSON = mockStatic(JSON.class, RETURNS_DEEP_STUBS)) {
            // Given
            mockedStaticJSON.when(() -> JSON.parseArray(anyString())).thenReturn(null);

            // When
            boolean result = LoopExample.checkUserConfig(null);

            // Then
            assertTrue(result);
        }
    }
}