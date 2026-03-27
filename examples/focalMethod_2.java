package org.utbench.productline.basic.function;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.util.Assert;
import org.springframework.util.CollectionUtils;
import org.utbench.productline.model.Author;
import org.utbench.productline.model.BuildInfo;
import org.utbench.productline.model.BuildToolEntity;
import org.utbench.productline.model.EnvInfo;
import org.utbench.productline.model.ImageEntity;
import org.utbench.productline.model.ImageVo;
import org.utbench.productline.model.Property;
import org.utbench.productline.model.Tool;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

@Component
public class ComposeFunction {
    @Autowired
    private ComposedParamForFunction commonService;

    public void setPropertiesValue(Property p, BuildToolEntity tool) {
        String name = p.getName();
        String value = p.getValue();
        if (!org.springframework.util.StringUtils.hasText(value)) {
            return;
        }
        if ("softwareType".equals(name)) {
            tool.setType(value);
        }
        if ("toolType".equals(name)) {
            tool.setToolType(value);
        }
        if ("belongSoftware".equals(name)) {
            tool.setReleaseVersion(value);
        }
        if ("huaweiCode".equals(name)) {
            tool.setHuaweiCode(value);
        }
        if ("version".equals(name)) {
            tool.setVersion(value);
        }
        if ("name".equals(name)) {
            tool.setName(value);
        }
        if ("buildRndType".equals(name)) {
            tool.setBuildRndType(value);
        }
    }
}
