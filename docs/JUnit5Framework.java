package com.example.codegen.template;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

/**
 * JUnit5 test framework template generator (sanitized).
 */
public class JUnit5Framework extends TestFramework {

    public JUnit5Framework(MockFramework mockFramework, TestFile testFile, GenerateModel model) {
        super(mockFramework, testFile, model);
    }

    @Override
    public void importFramework() {
        addImport("org.junit.jupiter.api.AfterEach");
        addImport("org.junit.jupiter.api.BeforeEach");
        addImport("org.junit.jupiter.api.Test");
        addImport("org.junit.jupiter.api.DisplayName");

        // Mockito / Spring test utils (optional)
        addImport("org.mockito.junit.jupiter.MockitoSettings");
        addImport("org.mockito.quality.Strictness");
        addImport("org.springframework.test.util.ReflectionTestUtils");
    }

    @Override
    public String generateClassAnnotation() {
        if (mockFramework.isAltMockFramework()) { // e.g., JMockit-like
            return "";
        }
        // feature flag example (sanitized)
        if (SettingsState.getInstance().isUseInMemoryDbEnabled()) {
            addImport("org.springframework.boot.test.context.SpringBootTest");
            return "@SpringBootTest(properties = {\n"
                    + "        \"spring.datasource.url=jdbc:h2:mem:testdb;MODE=MYSQL;\",\n"
                    + "        \"spring.datasource.driverClassName=org.h2.Driver\"\n"
                    + "})\n";
        }
        return "@MockitoSettings(strictness = Strictness.LENIENT)\n";
    }

    @Override
    String generateCommonMethod() {
        StringBuilder sb = new StringBuilder();

        sb.append("@BeforeEach\n");
        sb.append("void setUp() throws Exception {\n");
        if (!mockFramework.isAltMockFramework()) {
            openMocks(sb);
            setupBody(sb);
        }
        sb.append("}\n\n");

        sb.append("@AfterEach\n");
        sb.append("void tearDown() throws Exception {\n");
        if (!mockFramework.isAltMockFramework()) {
            if (mockFramework.useClosableMocks()) {
                sb.append("mockitoCloseable.close();\n");
            }
        }
        sb.append("}\n");

        return sb.toString();
    }

    protected void openMocks(StringBuilder sb) {
        if (mockFramework.useClosableMocks()) {
            sb.append("mockitoCloseable = MockitoAnnotations.openMocks(this);\n");
        } else {
            sb.append("MockitoAnnotations.initMocks(this);\n");
        }
    }

    private void setupBody(StringBuilder sb) {
        // init inner classes / reflect fields etc. (sanitized placeholders)
        initReflectField(sb);
    }

    protected void initReflectField(StringBuilder sb) {
        // Using ReflectionTestUtils.setField(...) for @Value-like / private fields injection
        // Actual field selection logic omitted (internal PSI/AST details are sanitized)
        if (testClass.hasReflectFields()) {
            addImport("org.springframework.test.util.ReflectionTestUtils");
            sb.append("// ReflectionTestUtils.setField(target, \"field\", value);\n");
        }
    }

    @Override
    public String generateTestMethod() {
        // de-duplicate by "beforeAssertion" content
        Set<String> dedupKey = new HashSet<>();
        List<TestMethod> dedup = new ArrayList<>();

        for (TestMethod tm : testClass.getTestMethods()) {
            String signature = generateSignature(tm);
            if (!model.isEmptyTemplate()) {
                String body = generateMethodBody(tm);
                tm.setBody(body);

                if (dedupKey.add(tm.getBeforeAssertion())) {
                    tm.setText(signature + body + "}\n");
                    dedup.add(tm);
                }
            } else {
                tm.setText(signature + "}\n");
                dedup.add(tm);
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < dedup.size(); i++) {
            sb.append(dedup.get(i).getText());
            if (i != dedup.size() - 1) sb.append("\n");
        }

        testClass.replaceTestMethods(dedup);
        return sb.toString();
    }

    @Override
    String generateSignature(TestMethod tm) {
        StringBuilder sb = new StringBuilder();

        generateAnnotation(sb, tm);

        // method signature
        String testName = tm.generateMethodName(model, testClass.getMethodNames());
        AtomicReference<String> exceptionName = new AtomicReference<>("Exception");

        // if throws contains Throwable, update
        tm.getThrowsTypes().forEach(t -> {
            if ("Throwable".equals(t)) exceptionName.set("Throwable");
        });

        sb.append("void ").append(testName).append("(").append(tm.renderParameters()).append(") throws ")
                .append(exceptionName.get()).append(" {\n");
        return sb.toString();
    }

    void generateAnnotation(StringBuilder sb, TestMethod tm) {
        // optional: enhance description + @DisplayName
        String displayName = tm.generateDisplayName();

        sb.append("@Test\n");
        sb.append("@DisplayName(\"").append(escape(displayName)).append("\")\n");
    }

    @Override
    String generateMethodBody(TestMethod tm) {
        StringBuilder sb = new StringBuilder();

        // Given
        sb.append(generateInitiations(tm));

        // When
        sb.append(generateExecution(tm));

        // Then
        sb.append(generateAssertion(tm));

        return sb.toString();
    }

    @Override
    String generateInitiations(TestMethod tm) {
        List<String> chunks = new ArrayList<>();

        // example: parameter / field / static initiations (sanitized)
        List<String> givenLines = tm.renderGivenLines(mockFramework, model);
        if (!givenLines.isEmpty()) {
            chunks.add("    // Given\n" + String.join("\n", givenLines));
        }

        return chunks.isEmpty() ? "" : String.join("\n", chunks) + "\n";
    }

    @Override
    String generateExecution(TestMethod tm) {
        StringBuilder sb = new StringBuilder();
        sb.append("\n    // When\n");

        if (!tm.isVoidReturn()) {
            sb.append("    ").append(tm.renderResultDeclaration()).append(" = ");
        } else {
            sb.append("    ");
        }

        sb.append(tm.renderInvocation()).append(";\n");
        return sb.toString();
    }

    @Override
    String generateAssertion(TestMethod tm) {
        if (tm.isExpectingException()) {
            return ""; // handled by assertThrows wrapper in some frameworks
        }

        StringBuilder sb = new StringBuilder();

        if (tm.shouldAssertReturnValue()) {
            sb.append("\n    // Then\n");
            sb.append(tm.renderDefaultAssertion(model)).append("\n");
        }

        if (model.isVerifyMocksEnabled()) {
            sb.append(tm.renderVerifyStatements(mockFramework));
        }

        return sb.toString();
    }

    private String escape(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}