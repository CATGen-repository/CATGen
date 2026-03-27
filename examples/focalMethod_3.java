package org.utbench.productline.basic.controlflow;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import org.apache.commons.lang3.StringUtils;
import org.springframework.util.CollectionUtils;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;


public class LoopExample {
    private static final String[] CONFIG_KEY_LIST = {"name", "id", "email", "address"};

    private static final String[] USER_CONFIG_KEY_LIST = {"token", "cookie", "session"};

    private static final String PARAM_KEY_REGEX = "[a-zA-Z0-1]{2, 50}";

    private static final String[] TIME_NAME_SUFFIX = {"time", "date"};

    public static boolean checkUserConfig(String rootConfJson) {
        if (StringUtils.isBlank(rootConfJson)) {
            return false;
        }
        JSONArray root = JSONArray.parseArray(rootConfJson);
        for (Object value : root) {
            JSONObject child = (JSONObject) value;
            if (!child.containsKey("USER_CONFIG")) {
                continue;
            }
            JSONArray userConfig = child.getJSONArray("USER_CONFIG");
            for (Object obj : userConfig) {
                JSONObject conf = (JSONObject) obj;
                for (String key : USER_CONFIG_KEY_LIST) {
                    if (conf.containsKey(key)) {
                        return true;
                    }
                }
            }
        }
        return true;
    }
}
