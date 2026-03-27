package org.utbench.productline.basic.function;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.utbench.productline.model.BuildToolEntity;
import org.utbench.productline.model.Property;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;

@MockitoSettings(strictness = Strictness.LENIENT)
class ComposeFunctionTest {
    @InjectMocks
    private ComposeFunction composeFunction;

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
    public void test_setPropertiesValue_with_empty_value() throws Exception {
        Property property = new Property();
        property.setName("testName");
        property.setValue("");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("", buildToolEntity.getType());
        assertEquals("", buildToolEntity.getToolType());
        assertEquals("", buildToolEntity.getReleaseVersion());
        assertEquals("", buildToolEntity.getVersion());
        assertEquals("", buildToolEntity.getName());
        assertEquals("", buildToolEntity.getBuildRndType());
    }

    @Test
    public void test_setPropertiesValue_type() throws Exception {
        Property property = new Property();
        property.setName("softwareType");
        property.setValue("testValue");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("testValue", buildToolEntity.getType());
        assertEquals("", buildToolEntity.getToolType());
        assertEquals("", buildToolEntity.getReleaseVersion());
        assertEquals("", buildToolEntity.getVersion());
        assertEquals("", buildToolEntity.getName());
        assertEquals("", buildToolEntity.getBuildRndType());
    }

    @Test
    public void test_setPropertiesValue_tool_type() throws Exception {
        Property property = new Property();
        property.setName("toolType");
        property.setValue("testValue");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("", buildToolEntity.getType());
        assertEquals("testValue", buildToolEntity.getToolType());
        assertEquals("", buildToolEntity.getReleaseVersion());
        assertEquals("", buildToolEntity.getVersion());
        assertEquals("", buildToolEntity.getName());
        assertEquals("", buildToolEntity.getBuildRndType());
    }

    @Test
    public void test_setPropertiesValue_belong_software() throws Exception {
        Property property = new Property();
        property.setName("belongSoftware");
        property.setValue("testValue");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("", buildToolEntity.getType());
        assertEquals("", buildToolEntity.getToolType());
        assertEquals("testValue", buildToolEntity.getReleaseVersion());
        assertEquals("", buildToolEntity.getVersion());
        assertEquals("", buildToolEntity.getName());
        assertEquals("", buildToolEntity.getBuildRndType());
    }

    @Test
    public void test_setPropertiesValue_huawei_code() throws Exception {
        Property property = new Property();
        property.setName("huaweiCode");
        property.setValue("testValue");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("", buildToolEntity.getType());
        assertEquals("", buildToolEntity.getToolType());
        assertEquals("", buildToolEntity.getReleaseVersion());
        assertEquals("", buildToolEntity.getVersion());
        assertEquals("", buildToolEntity.getName());
        assertEquals("", buildToolEntity.getBuildRndType());
    }

    @Test
    public void test_setPropertiesValue_version() throws Exception {
        Property property = new Property();
        property.setName("version");
        property.setValue("testValue");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("", buildToolEntity.getType());
        assertEquals("", buildToolEntity.getToolType());
        assertEquals("", buildToolEntity.getReleaseVersion());
        assertEquals("testValue", buildToolEntity.getVersion());
        assertEquals("", buildToolEntity.getName());
        assertEquals("", buildToolEntity.getBuildRndType());
    }

    @Test
    public void test_setPropertiesValue_name() throws Exception {
        Property property = new Property();
        property.setName("name");
        property.setValue("testValue");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("", buildToolEntity.getType());
        assertEquals("", buildToolEntity.getToolType());
        assertEquals("", buildToolEntity.getReleaseVersion());
        assertEquals("", buildToolEntity.getVersion());
        assertEquals("testValue", buildToolEntity.getName());
        assertEquals("", buildToolEntity.getBuildRndType());
    }

    @Test
    public void test_setPropertiesValue_build_rnd_type() throws Exception {
        Property property = new Property();
        property.setName("buildRndType");
        property.setValue("testValue");

        BuildToolEntity buildToolEntity = new BuildToolEntity();

        composeFunction.setPropertiesValue(property, buildToolEntity);

        assertEquals("", buildToolEntity.getType());
        assertEquals("", buildToolEntity.getToolType());
        assertEquals("", buildToolEntity.getReleaseVersion());
        assertEquals("", buildToolEntity.getVersion());
        assertEquals("", buildToolEntity.getName());
        assertEquals("testValue", buildToolEntity.getBuildRndType());
    }

    @Test
    void test_setPropertiesValue_should_not_throw_exception() throws Exception {
        assertDoesNotThrow(() -> {
            // Given
            Property p = new Property();
            p.setName("not_empty");
            p.setValue("not_empty");

            BuildToolEntity tool = new BuildToolEntity();

            // When
            composeFunction.setPropertiesValue(p, tool);
        });
    }
}