import unittest

from utils.deserializable import json_deserializable
from utils.parsers import *


class ParserTests(unittest.TestCase):

    def test_has_one_class_when_only_one(self):
        class_str = """
        /* ===========================================================
 * JFreeChart : a free chart library for the Java(tm) platform
 * ===========================================================
 *
 * (C) Copyright 2000-2022, by David Gilbert and Contributors.
 *
 * Project Info:  http://www.jfree.org/jfreechart/index.html
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2.1 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
 * USA.
 *
 * [Oracle and Java are registered trademarks of Oracle and/or its affiliates. 
 * Other names may be trademarks of their respective owners.]
 *
 * ---------------------------
 * DefaultFlowDatasetTest.java
 * ---------------------------
 * (C) Copyright 2021-2022, by David Gilbert and Contributors.
 *
 * Original Author:  David Gilbert;
 * Contributor(s):   -;
 *
 */

package org.jfree.data.flow;


import org.jfree.chart.TestUtils;
import org.jfree.chart.api.PublicCloneable;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for the {@link DefaultFlowDataset} class.
 */
public class DefaultFlowDatasetTest {

    /**
     * Some checks for the getValue() method.
     */
    @Test
    public void testGetFlow() {
        DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
        d.setFlow(0, "A", "Z", 1.5);
        assertEquals(1.5, d.getFlow(0, "A", "Z"));
    }

    /**
     * Some tests for the getStageCount() method.
     */
    @Test
    public void testGetStageCount() {
        DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
        assertEquals(1, d.getStageCount());

        d.setFlow(0, "A", "Z", 11.1);
        assertEquals(1, d.getStageCount());

        // a row of all null values is still counted...
        d.setFlow(1, "Z", "P", 5.0);
        assertEquals(2, d.getStageCount());
    }

    /**
     * Confirm that the equals method can distinguish all the required fields.
     */
    @Test
    public void testEquals() {
        DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
        DefaultFlowDataset<String> d2 = new DefaultFlowDataset<>();
        assertEquals(d1, d2);
        
        d1.setFlow(0, "A", "Z", 1.0);
        assertNotEquals(d1, d2);
        d2.setFlow(0, "A", "Z", 1.0);
        assertEquals(d1, d2);
    }

    /**
     * Serialize an instance, restore it, and check for equality.
     */
    @Test
    public void testSerialization() {
        DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
        d1.setFlow(0, "A", "Z", 1.0);
        DefaultFlowDataset<String> d2 = TestUtils.serialised(d1);
        assertEquals(d1, d2);
    }

    /**
     * Confirm that cloning works.
     * @throws java.lang.CloneNotSupportedException
     */
    @Test
    public void testCloning() throws CloneNotSupportedException {
        DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
        d1.setFlow(0, "A", "Z", 1.0);
        DefaultFlowDataset<String> d2 = (DefaultFlowDataset<String>) d1.clone();

        assertNotSame(d1, d2);
        assertSame(d1.getClass(), d2.getClass());
        assertEquals(d1, d2);

        // check that the clone doesn't share the same underlying arrays.
        d1.setFlow(0, "A", "Y", 8.0);
        assertNotEquals(d1, d2);
        d2.setFlow(0, "A", "Y", 8.0);
        assertEquals(d1, d2);
    }

    /**
     * Check that this class implements PublicCloneable.
     */
    @Test
    public void testPublicCloneable() {
        DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
        assertTrue(d instanceof PublicCloneable);
    }

}
"""
        self.assertTrue(has_one_class(class_str))

    def test_has_one_class_when_there_are_two(self):
        class_str = """/* ===========================================================
 * JFreeChart : a free chart library for the Java(tm) platform
 * ===========================================================
 *
 * (C) Copyright 2000-2022, by David Gilbert and Contributors.
 *
 * Project Info:  http://www.jfree.org/jfreechart/index.html
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2.1 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
 * USA.
 *
 * [Oracle and Java are registered trademarks of Oracle and/or its affiliates. 
 * Other names may be trademarks of their respective owners.]
 *
 * ---------------------------
 * DefaultFlowDatasetTest.java
 * ---------------------------
 * (C) Copyright 2021-2022, by David Gilbert and Contributors.
 *
 * Original Author:  David Gilbert;
 * Contributor(s):   -;
 *
 */

package org.jfree.data.flow;


import org.jfree.chart.TestUtils;
import org.jfree.chart.api.PublicCloneable;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for the {@link DefaultFlowDataset} class.
 */
public class DefaultFlowDatasetTest {

    /**
     * Some checks for the getValue() method.
     */
    @Test
    public void testGetFlow() {
        DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
        d.setFlow(0, "A", "Z", 1.5);
        assertEquals(1.5, d.getFlow(0, "A", "Z"));
    }

    /**
     * Some tests for the getStageCount() method.
     */
    @Test
    public void testGetStageCount() {
        DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
        assertEquals(1, d.getStageCount());

        d.setFlow(0, "A", "Z", 11.1);
        assertEquals(1, d.getStageCount());

        // a row of all null values is still counted...
        d.setFlow(1, "Z", "P", 5.0);
        assertEquals(2, d.getStageCount());
    }

    /**
     * Confirm that the equals method can distinguish all the required fields.
     */
    @Test
    public void testEquals() {
        DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
        DefaultFlowDataset<String> d2 = new DefaultFlowDataset<>();
        assertEquals(d1, d2);
        
        d1.setFlow(0, "A", "Z", 1.0);
        assertNotEquals(d1, d2);
        d2.setFlow(0, "A", "Z", 1.0);
        assertEquals(d1, d2);
    }

    /**
     * Serialize an instance, restore it, and check for equality.
     */
    @Test
    public void testSerialization() {
        DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
        d1.setFlow(0, "A", "Z", 1.0);
        DefaultFlowDataset<String> d2 = TestUtils.serialised(d1);
        assertEquals(d1, d2);
    }

    /**
     * Confirm that cloning works.
     * @throws java.lang.CloneNotSupportedException
     */
    @Test
    public void testCloning() throws CloneNotSupportedException {
        DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
        d1.setFlow(0, "A", "Z", 1.0);
        DefaultFlowDataset<String> d2 = (DefaultFlowDataset<String>) d1.clone();

        assertNotSame(d1, d2);
        assertSame(d1.getClass(), d2.getClass());
        assertEquals(d1, d2);

        // check that the clone doesn't share the same underlying arrays.
        d1.setFlow(0, "A", "Y", 8.0);
        assertNotEquals(d1, d2);
        d2.setFlow(0, "A", "Y", 8.0);
        assertEquals(d1, d2);
    }

    /**
     * Check that this class implements PublicCloneable.
     */
    @Test
    public void testPublicCloneable() {
        DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
        assertTrue(d instanceof PublicCloneable);
    }

}

class SomeClass{
}
"""
        self.assertFalse(has_one_class(class_str))

    #     def test_parse_class_declaration_when_one_class(self):
    #         class_str = """
    #         /* ===========================================================
    #  * JFreeChart : a free chart library for the Java(tm) platform
    #  * ===========================================================
    #  *
    #  * (C) Copyright 2000-2022, by David Gilbert and Contributors.
    #  *
    #  * Project Info:  http://www.jfree.org/jfreechart/index.html
    #  *
    #  * This library is free software; you can redistribute it and/or modify it
    #  * under the terms of the GNU Lesser General Public License as published by
    #  * the Free Software Foundation; either version 2.1 of the License, or
    #  * (at your option) any later version.
    #  *
    #  * This library is distributed in the hope that it will be useful, but
    #  * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    #  * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
    #  * License for more details.
    #  *
    #  * You should have received a copy of the GNU Lesser General Public
    #  * License along with this library; if not, write to the Free Software
    #  * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
    #  * USA.
    #  *
    #  * [Oracle and Java are registered trademarks of Oracle and/or its affiliates.
    #  * Other names may be trademarks of their respective owners.]
    #  *
    #  * ---------------------------
    #  * DefaultFlowDatasetTest.java
    #  * ---------------------------
    #  * (C) Copyright 2021-2022, by David Gilbert and Contributors.
    #  *
    #  * Original Author:  David Gilbert;
    #  * Contributor(s):   -;
    #  *
    #  */
    #
    # package org.jfree.data.flow;
    #
    #
    # import org.jfree.chart.TestUtils;
    # import org.jfree.chart.api.PublicCloneable;
    # import org.junit.jupiter.api.Test;
    #
    # import static org.junit.jupiter.api.Assertions.*;
    #
    # /**
    #  * Tests for the {@link DefaultFlowDataset} class.
    #  */
    # public class DefaultFlowDatasetTest {
    #
    #     /**
    #      * Some checks for the getValue() method.
    #      */
    #     @Test
    #     public void testGetFlow() {
    #         DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
    #         d.setFlow(0, "A", "Z", 1.5);
    #         assertEquals(1.5, d.getFlow(0, "A", "Z"));
    #     }
    #
    #     /**
    #      * Some tests for the getStageCount() method.
    #      */
    #     @Test
    #     public void testGetStageCount() {
    #         DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
    #         assertEquals(1, d.getStageCount());
    #
    #         d.setFlow(0, "A", "Z", 11.1);
    #         assertEquals(1, d.getStageCount());
    #
    #         // a row of all null values is still counted...
    #         d.setFlow(1, "Z", "P", 5.0);
    #         assertEquals(2, d.getStageCount());
    #     }
    #
    #     /**
    #      * Confirm that the equals method can distinguish all the required fields.
    #      */
    #     @Test
    #     public void testEquals() {
    #         DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
    #         DefaultFlowDataset<String> d2 = new DefaultFlowDataset<>();
    #         assertEquals(d1, d2);
    #
    #         d1.setFlow(0, "A", "Z", 1.0);
    #         assertNotEquals(d1, d2);
    #         d2.setFlow(0, "A", "Z", 1.0);
    #         assertEquals(d1, d2);
    #     }
    #
    #     /**
    #      * Serialize an instance, restore it, and check for equality.
    #      */
    #     @Test
    #     public void testSerialization() {
    #         DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
    #         d1.setFlow(0, "A", "Z", 1.0);
    #         DefaultFlowDataset<String> d2 = TestUtils.serialised(d1);
    #         assertEquals(d1, d2);
    #     }
    #
    #     /**
    #      * Confirm that cloning works.
    #      * @throws java.lang.CloneNotSupportedException
    #      */
    #     @Test
    #     public void testCloning() throws CloneNotSupportedException {
    #         DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
    #         d1.setFlow(0, "A", "Z", 1.0);
    #         DefaultFlowDataset<String> d2 = (DefaultFlowDataset<String>) d1.clone();
    #
    #         assertNotSame(d1, d2);
    #         assertSame(d1.getClass(), d2.getClass());
    #         assertEquals(d1, d2);
    #
    #         // check that the clone doesn't share the same underlying arrays.
    #         d1.setFlow(0, "A", "Y", 8.0);
    #         assertNotEquals(d1, d2);
    #         d2.setFlow(0, "A", "Y", 8.0);
    #         assertEquals(d1, d2);
    #     }
    #
    #     /**
    #      * Check that this class implements PublicCloneable.
    #      */
    #     @Test
    #     public void testPublicCloneable() {
    #         DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
    #         assertTrue(d instanceof PublicCloneable);
    #     }
    #
    # }
    #
    #         """
    #         class_object = parse_class_declaration(class_str)
    #         self.assertEqual(class_object.name, "DefaultFlowDatasetTest")
    #         self.assertEqual(len(class_object.modifiers), 1)
    #         self.assertEqual(class_object.modifiers[0], 'public')
    #         self.assertEqual(len(class_object.inner_classes), 0)
    #         self.assertEqual(class_object.signature, 'public class DefaultFlowDatasetTest')
    #         self.assertEqual(len(class_object.imports), 4)
    #
    #     def test_parse_class_declaration_when_two_classes(self):
    #         class_str = """
    #         /* ===========================================================
    #  * JFreeChart : a free chart library for the Java(tm) platform
    #  * ===========================================================
    #  *
    #  * (C) Copyright 2000-2022, by David Gilbert and Contributors.
    #  *
    #  * Project Info:  http://www.jfree.org/jfreechart/index.html
    #  *
    #  * This library is free software; you can redistribute it and/or modify it
    #  * under the terms of the GNU Lesser General Public License as published by
    #  * the Free Software Foundation; either version 2.1 of the License, or
    #  * (at your option) any later version.
    #  *
    #  * This library is distributed in the hope that it will be useful, but
    #  * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    #  * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
    #  * License for more details.
    #  *
    #  * You should have received a copy of the GNU Lesser General Public
    #  * License along with this library; if not, write to the Free Software
    #  * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
    #  * USA.
    #  *
    #  * [Oracle and Java are registered trademarks of Oracle and/or its affiliates.
    #  * Other names may be trademarks of their respective owners.]
    #  *
    #  * ---------------------------
    #  * DefaultFlowDatasetTest.java
    #  * ---------------------------
    #  * (C) Copyright 2021-2022, by David Gilbert and Contributors.
    #  *
    #  * Original Author:  David Gilbert;
    #  * Contributor(s):   -;
    #  *
    #  */
    #
    # package org.jfree.data.flow;
    #
    #
    # import org.jfree.chart.TestUtils;
    # import org.jfree.chart.api.PublicCloneable;
    # import org.junit.jupiter.api.Test;
    #
    # import static org.junit.jupiter.api.Assertions.*;
    #
    # /**
    #  * Tests for the {@link DefaultFlowDataset} class.
    #  */
    # public class DefaultFlowDatasetTest {
    #
    #     /**
    #      * Some checks for the getValue() method.
    #      */
    #     @Test
    #     public void testGetFlow() {
    #         DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
    #         d.setFlow(0, "A", "Z", 1.5);
    #         assertEquals(1.5, d.getFlow(0, "A", "Z"));
    #     }
    #
    #     /**
    #      * Some tests for the getStageCount() method.
    #      */
    #     @Test
    #     public void testGetStageCount() {
    #         DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
    #         assertEquals(1, d.getStageCount());
    #
    #         d.setFlow(0, "A", "Z", 11.1);
    #         assertEquals(1, d.getStageCount());
    #
    #         // a row of all null values is still counted...
    #         d.setFlow(1, "Z", "P", 5.0);
    #         assertEquals(2, d.getStageCount());
    #     }
    #
    #     /**
    #      * Confirm that the equals method can distinguish all the required fields.
    #      */
    #     @Test
    #     public void testEquals() {
    #         DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
    #         DefaultFlowDataset<String> d2 = new DefaultFlowDataset<>();
    #         assertEquals(d1, d2);
    #
    #         d1.setFlow(0, "A", "Z", 1.0);
    #         assertNotEquals(d1, d2);
    #         d2.setFlow(0, "A", "Z", 1.0);
    #         assertEquals(d1, d2);
    #     }
    #
    #     /**
    #      * Serialize an instance, restore it, and check for equality.
    #      */
    #     @Test
    #     public void testSerialization() {
    #         DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
    #         d1.setFlow(0, "A", "Z", 1.0);
    #         DefaultFlowDataset<String> d2 = TestUtils.serialised(d1);
    #         assertEquals(d1, d2);
    #     }
    #
    #     /**
    #      * Confirm that cloning works.
    #      * @throws java.lang.CloneNotSupportedException
    #      */
    #     @Test
    #     public void testCloning() throws CloneNotSupportedException {
    #         DefaultFlowDataset<String> d1 = new DefaultFlowDataset<>();
    #         d1.setFlow(0, "A", "Z", 1.0);
    #         DefaultFlowDataset<String> d2 = (DefaultFlowDataset<String>) d1.clone();
    #
    #         assertNotSame(d1, d2);
    #         assertSame(d1.getClass(), d2.getClass());
    #         assertEquals(d1, d2);
    #
    #         // check that the clone doesn't share the same underlying arrays.
    #         d1.setFlow(0, "A", "Y", 8.0);
    #         assertNotEquals(d1, d2);
    #         d2.setFlow(0, "A", "Y", 8.0);
    #         assertEquals(d1, d2);
    #     }
    #
    #     /**
    #      * Check that this class implements PublicCloneable.
    #      */
    #     @Test
    #     public void testPublicCloneable() {
    #         DefaultFlowDataset<String> d = new DefaultFlowDataset<>();
    #         assertTrue(d instanceof PublicCloneable);
    #     }
    #
    # }
    #
    # class SomeClass{
    # }"""
    #         class_object = parse_class_declaration(class_str)
    #         self.assertEqual(len(class_object.inner_classes), 1)
    #
    #     def test_parse_class_declaration_when_no_class(self):
    #         cls_str = """
    #         /* ===========================================================
    #          * JFreeChart : a free chart library for the Java(tm) platform
    #          * ===========================================================
    #          *
    #          * (C) Copyright 2000-2022, by David Gilbert and Contributors.
    #          *
    #          * Project Info:  http://www.jfree.org/jfreechart/index.html
    #          *
    #          * This library is free software; you can redistribute it and/or modify it
    #          * under the terms of the GNU Lesser General Public License as published by
    #          * the Free Software Foundation; either version 2.1 of the License, or
    #          * (at your option) any later version.
    #          *
    #          * This library is distributed in the hope that it will be useful, but
    #          * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    #          * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
    #          * License for more details.
    #          *
    #          * You should have received a copy of the GNU Lesser General Public
    #          * License along with this library; if not, write to the Free Software
    #          * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
    #          * USA.
    #          *
    #          * [Oracle and Java are registered trademarks of Oracle and/or its affiliates.
    #          * Other names may be trademarks of their respective owners.]
    #          *
    #          * -----------------------
    #          * DefaultTitleEditor.java
    #          * -----------------------
    #          * (C) Copyright 2005-2022, by David Gilbert.
    #          *
    #          * Original Author:  David Gilbert;
    #          * Contributor(s):   Arnaud Lelievre;
    #          *                   Daniel Gredler;
    #          *
    #          */
    #
    #         package org.jfree.chart.swing.editor;
    #
    #         import java.awt.BorderLayout;
    #         import java.awt.Color;
    #         import java.awt.Font;
    #         import java.awt.Paint;
    #         import java.awt.event.ActionEvent;
    #         import java.awt.event.ActionListener;
    #         import java.util.ResourceBundle;
    #
    #         import javax.swing.BorderFactory;
    #         import javax.swing.JButton;
    #         import javax.swing.JCheckBox;
    #         import javax.swing.JColorChooser;
    #         import javax.swing.JLabel;
    #         import javax.swing.JOptionPane;
    #         import javax.swing.JPanel;
    #         import javax.swing.JTextField;
    #
    #         import org.jfree.chart.JFreeChart;
    #         import org.jfree.chart.title.TextTitle;
    #         import org.jfree.chart.title.Title;
    #
    #         /**
    #          * A panel for editing the properties of a chart title.
    #          */
    #         class DefaultTitleEditor extends JPanel implements ActionListener {
    #
    #             /** Whether or not to display the title on the chart. */
    #             private boolean showTitle;
    #
    #             /** The checkbox to indicate whether or not to display the title. */
    #             private final JCheckBox showTitleCheckBox;
    #
    #             /** A field for displaying/editing the title text. */
    #             private final JTextField titleField;
    #
    #             /** The font used to draw the title. */
    #             private Font titleFont;
    #
    #             /** A field for displaying a description of the title font. */
    #             private final JTextField fontfield;
    #
    #             /** The button to use to select a new title font. */
    #             private final JButton selectFontButton;
    #
    #             /** The paint (color) used to draw the title. */
    #             private final PaintSample titlePaint;
    #
    #             /** The button to use to select a new paint (color) to draw the title. */
    #             private final JButton selectPaintButton;
    #
    #             /** The resourceBundle for the localization. */
    #             protected static ResourceBundle localizationResources
    #                     = ResourceBundle.getBundle("org.jfree.chart.editor.LocalizationBundle");
    #
    #             /**
    #              * Standard constructor: builds a panel for displaying/editing the
    #              * properties of the specified title.
    #              *
    #              * @param title  the title, which should be changed.
    #              */
    #             public DefaultTitleEditor(Title title) {
    #
    #                 TextTitle t = (title != null ? (TextTitle) title
    #                         : new TextTitle(localizationResources.getString("Title")));
    #                 this.showTitle = (title != null);
    #                 this.titleFont = t.getFont();
    #                 this.titleField = new JTextField(t.getText());
    #                 this.titlePaint = new PaintSample(t.getPaint());
    #
    #                 setLayout(new BorderLayout());
    #
    #                 JPanel general = new JPanel(new BorderLayout());
    #                 general.setBorder(
    #                     BorderFactory.createTitledBorder(
    #                         BorderFactory.createEtchedBorder(),
    #                         localizationResources.getString("General")
    #                     )
    #                 );
    #
    #                 JPanel interior = new JPanel(new LCBLayout(4));
    #                 interior.setBorder(BorderFactory.createEmptyBorder(0, 5, 0, 5));
    #
    #                 interior.add(new JLabel(localizationResources.getString("Show_Title")));
    #                 this.showTitleCheckBox = new JCheckBox();
    #                 this.showTitleCheckBox.setSelected(this.showTitle);
    #                 this.showTitleCheckBox.setActionCommand("ShowTitle");
    #                 this.showTitleCheckBox.addActionListener(this);
    #                 interior.add(new JPanel());
    #                 interior.add(this.showTitleCheckBox);
    #
    #                 JLabel titleLabel = new JLabel(localizationResources.getString("Text"));
    #                 interior.add(titleLabel);
    #                 interior.add(this.titleField);
    #                 interior.add(new JPanel());
    #
    #                 JLabel fontLabel = new JLabel(localizationResources.getString("Font"));
    #                 this.fontfield = new FontDisplayField(this.titleFont);
    #                 this.selectFontButton = new JButton(
    #                     localizationResources.getString("Select...")
    #                 );
    #                 this.selectFontButton.setActionCommand("SelectFont");
    #                 this.selectFontButton.addActionListener(this);
    #                 interior.add(fontLabel);
    #                 interior.add(this.fontfield);
    #                 interior.add(this.selectFontButton);
    #
    #                 JLabel colorLabel = new JLabel(
    #                     localizationResources.getString("Color")
    #                 );
    #                 this.selectPaintButton = new JButton(
    #                     localizationResources.getString("Select...")
    #                 );
    #                 this.selectPaintButton.setActionCommand("SelectPaint");
    #                 this.selectPaintButton.addActionListener(this);
    #                 interior.add(colorLabel);
    #                 interior.add(this.titlePaint);
    #                 interior.add(this.selectPaintButton);
    #
    #                 this.enableOrDisableControls();
    #
    #                 general.add(interior);
    #                 add(general, BorderLayout.NORTH);
    #             }
    #
    #             /**
    #              * Returns the title text entered in the panel.
    #              *
    #              * @return The title text entered in the panel.
    #              */
    #             public String getTitleText() {
    #                 return this.titleField.getText();
    #             }
    #
    #             /**
    #              * Returns the font selected in the panel.
    #              *
    #              * @return The font selected in the panel.
    #              */
    #             public Font getTitleFont() {
    #                 return this.titleFont;
    #             }
    #
    #             /**
    #              * Returns the paint selected in the panel.
    #              *
    #              * @return The paint selected in the panel.
    #              */
    #             public Paint getTitlePaint() {
    #                 return this.titlePaint.getPaint();
    #             }
    #
    #             /**
    #              * Handles button clicks by passing control to an appropriate handler
    #              * method.
    #              *
    #              * @param event  the event
    #              */
    #             @Override
    #             public void actionPerformed(ActionEvent event) {
    #
    #                 String command = event.getActionCommand();
    #
    #                 if (command.equals("SelectFont")) {
    #                     attemptFontSelection();
    #                 }
    #                 else if (command.equals("SelectPaint")) {
    #                     attemptPaintSelection();
    #                 }
    #                 else if (command.equals("ShowTitle")) {
    #                     attemptModifyShowTitle();
    #                 }
    #             }
    #
    #             /**
    #              * Presents a font selection dialog to the user.
    #              */
    #             public void attemptFontSelection() {
    #
    #                 FontChooserPanel panel = new FontChooserPanel(this.titleFont);
    #                 int result =
    #                     JOptionPane.showConfirmDialog(
    #                         this, panel, localizationResources.getString("Font_Selection"),
    #                         JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE
    #                     );
    #
    #                 if (result == JOptionPane.OK_OPTION) {
    #                     this.titleFont = panel.getSelectedFont();
    #                     this.fontfield.setText(
    #                         this.titleFont.getFontName() + " " + this.titleFont.getSize()
    #                     );
    #                 }
    #             }
    #
    #             /**
    #              * Allow the user the opportunity to select a Paint object.  For now, we
    #              * just use the standard color chooser - all colors are Paint objects, but
    #              * not all Paint objects are colors (later we can implement a more general
    #              * Paint chooser).
    #              */
    #             public void attemptPaintSelection() {
    #                 Paint p = this.titlePaint.getPaint();
    #                 Color defaultColor = (p instanceof Color ? (Color) p : Color.BLUE);
    #                 Color c = JColorChooser.showDialog(
    #                     this, localizationResources.getString("Title_Color"), defaultColor
    #                 );
    #                 if (c != null) {
    #                     this.titlePaint.setPaint(c);
    #                 }
    #             }
    #
    #             /**
    #              * Allow the user the opportunity to change whether the title is
    #              * displayed on the chart or not.
    #              */
    #             private void attemptModifyShowTitle() {
    #                 this.showTitle = this.showTitleCheckBox.isSelected();
    #                 this.enableOrDisableControls();
    #             }
    #
    #             /**
    #              * If we are supposed to show the title, the controls are enabled.
    #              * If we are not supposed to show the title, the controls are disabled.
    #              */
    #             private void enableOrDisableControls() {
    #                 boolean enabled = (this.showTitle == true);
    #                 this.titleField.setEnabled(enabled);
    #                 this.selectFontButton.setEnabled(enabled);
    #                 this.selectPaintButton.setEnabled(enabled);
    #             }
    #
    #             /**
    #              * Sets the properties of the specified title to match the properties
    #              * defined on this panel.
    #              *
    #              * @param chart  the chart whose title is to be modified.
    #              */
    #             public void setTitleProperties(JFreeChart chart) {
    #                 if (this.showTitle) {
    #                     TextTitle title = chart.getTitle();
    #                     if (title == null) {
    #                         title = new TextTitle();
    #                         chart.setTitle(title);
    #                     }
    #                     title.setText(getTitleText());
    #                     title.setFont(getTitleFont());
    #                     title.setPaint(getTitlePaint());
    #                 }
    #                 else {
    #                     chart.setTitle((TextTitle) null);
    #                 }
    #             }
    #
    #         }
    #         """
    #         class_obj = parse_class_declaration(cls_str)
    #         self.assertIsNotNone(class_obj)

    def test_parse_variables_one_at_a_time(self):
        cls_str = """
                package org.jfree.chart.swing.editor;

                import java.awt.BorderLayout;
                import java.awt.Color;
                import java.awt.Font;
                import java.awt.Paint;
                import java.awt.event.ActionEvent;
                import java.awt.event.ActionListener;
                import java.util.ResourceBundle;

                import javax.swing.BorderFactory;
                import javax.swing.JButton;
                import javax.swing.JCheckBox;
                import javax.swing.JColorChooser;
                import javax.swing.JLabel;
                import javax.swing.JOptionPane;
                import javax.swing.JPanel;
                import javax.swing.JTextField;

                import org.jfree.chart.JFreeChart;
                import org.jfree.chart.title.TextTitle;
                import org.jfree.chart.title.Title;

                /**
                 * A panel for editing the properties of a chart title.
                 */
                class DefaultTitleEditor extends JPanel implements ActionListener {

                    @Override
                    public void actionPerformed(ActionEvent event) {

                        String command = event.getActionCommand();

                        if (command.equals("SelectFont")) {
                            attemptFontSelection();
                        }
                        else if (command.equals("SelectPaint")) {
                            attemptPaintSelection();
                        }
                        else if (command.equals("ShowTitle")) {
                            attemptModifyShowTitle();
                        }
                    }

                    /**
                     * Presents a font selection dialog to the user.
                     */
                    public void attemptFontSelection() {

                        FontChooserPanel panel = new FontChooserPanel(this.titleFont);
                        int result =
                            JOptionPane.showConfirmDialog(
                                this, panel, localizationResources.getString("Font_Selection"),
                                JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE
                            );

                        if (result == JOptionPane.OK_OPTION) {
                            this.titleFont = panel.getSelectedFont();
                            this.fontfield.setText(
                                this.titleFont.getFontName() + " " + this.titleFont.getSize()
                            );
                        }
                    }

                    /**
                     * Allow the user the opportunity to select a Paint object.  For now, we
                     * just use the standard color chooser - all colors are Paint objects, but
                     * not all Paint objects are colors (later we can implement a more general
                     * Paint chooser).
                     */
                    public void attemptPaintSelection() {
                        Paint p = this.titlePaint.getPaint();
                        Color defaultColor = (p instanceof Color ? (Color) p : Color.BLUE);
                        Color c = JColorChooser.showDialog(
                            this, localizationResources.getString("Title_Color"), defaultColor
                        );
                        int i,j,k;
                        if (c != null) {
                            this.titlePaint.setPaint(c);
                        }
                    }

                    /**
                     * Sets the properties of the specified title to match the properties
                     * defined on this panel.
                     *
                     * @param chart  the chart whose title is to be modified.
                     */
                    public void setTitleProperties(JFreeChart chart) {
                        if (this.showTitle) {
                            TextTitle title = chart.getTitle();
                            if (title == null) {
                                title = new TextTitle();
                                chart.setTitle(title);
                            }
                            title.setText(getTitleText());
                            title.setFont(getTitleFont());
                            title.setPaint(getTitlePaint());
                        }
                        else {
                            chart.setTitle((TextTitle) null);
                        }
                    }

                }
                """
        method_objs = parse_methods(cls_str)
        self.assertEqual(sum([
            len(m.variables) for m in method_objs
        ]), 10)

    def test_parse_fields(self):
        class_str = """public class DiverseFieldsExample {
    
        // Public instance field with initialization
        public int publicInt = 10;
    
        // Private instance field without initialization
        private String privateString;
    
        // Protected instance field with initialization
        protected double protectedDouble = 20.5;
    
        // Package-private (default) instance field without initialization
        boolean defaultBoolean;
    
        // Public static field with initialization
        public static final String CONSTANT_STRING = "constant";
    
        // Private static field without initialization
        private static int staticInt;
    
        // Protected static field with initialization
        protected static float staticFloat = 15.0f;
    
        // Package-private static field without initialization
        static boolean staticBoolean;
    
        // Public instance field without initialization
        public char publicChar;
    
        // Private instance field with initialization
        private long privateLong = 100L;
    
        // Protected instance field without initialization
        protected short protectedShort;
    
        // Package-private instance field with initialization
        byte defaultByte = 1;
    
        // Public static final field with initialization
        public static final double STATIC_FINAL_DOUBLE = 99.99;
    
        // Private static final field with initialization
        private static final String STATIC_FINAL_STRING = "static_final";
    
        // Protected static final field without initialization
        protected static final int STATIC_FINAL_INT;
    
        // Static block to initialize static final field
        static {
            STATIC_FINAL_INT = 42;
        }
    
        // Public instance array field with initialization
        public int[] publicIntArray = {1, 2, 3};
    
        // Private instance array field without initialization
        private String[] privateStringArray;
    
        // Protected instance array field with initialization
        protected double[] protectedDoubleArray = new double[5];
    
        // Package-private instance array field without initialization
        byte[] defaultByteArray;
    
        // Static instance array field with initialization
        public static final String[] STATIC_FINAL
        }
    """
        fields = parse_fields(class_str)
        self.assertEqual(len(fields), 20)

    def test_parse_method(self):
        class_str = """public class ExampleClass {
        
        public ExampleConstructor(int instanceVariable,int instanceVariable2) {
            this.instanceVariable = instanceVariable;
        }
    
        
        @Test
        public void ExampleClass(int instanceVariable,int instanceVariable2) {
            this.instanceVariable = instanceVariable;
        }
    
        @CustomAnnotation("StaticMethod")
        public static void staticMethod() {
            System.out.println("This is a static method.");
        }
    
        @Override
        @CustomAnnotation("PublicInstanceMethod")
        public void publicInstanceMethod() {
            System.out.println("This is a public instance method.");
        }
        
    
        public static void staticMethod() {
            System.out.println("This is a static method.");
        }
    
        public void publicInstanceMethod() {
            System.out.println("This is a public instance method.");
        }
    
        private void privateInstanceMethod() {
            System.out.println("This is a private instance method.");
        }
    
        protected void protectedInstanceMethod() {
            System.out.println("This is a protected instance method.");
        }
    
        void defaultAccessMethod() {
            System.out.println("This is a default access method.");
        }
    
        public void methodWithParameters(int param1, String param2) {
            System.out.println("Parameter 1: " + param1);
            System.out.println("Parameter 2: " + param2);
        }
    
        public int methodWithReturnValue() {
            return instanceVariable;
        }
    
        public static int staticMethodWithReturnValue(int param) {
            return param * 2;
        }
    
        public void overloadedMethod(int param) {
            System.out.println("One parameter: " + param);
        }
    
        public void overloadedMethod(int param1, int param2) {
            System.out.println("Two parameters: " + param1 + ", " + param2);
        }
    
        public static void main(String[] args) {
            // 创建ExampleClass对象
            ExampleClass example = new ExampleClass(10);
    
            // 调用各种方法
            ExampleClass.staticMethod();
            example.publicInstanceMethod();
            example.privateInstanceMethod(); // 注意：私有方法只能在类的内部调用
            example.protectedInstanceMethod();
            example.defaultAccessMethod();
            example.methodWithParameters(5, "test");
            int value = example.methodWithReturnValue();
            System.out.println("Return value: " + value);
            int staticValue = ExampleClass.staticMethodWithReturnValue(5);
            System.out.println("Static method return value: " + staticValue);
            example.overloadedMethod();
            example.overloadedMethod(1);
            example.overloadedMethod(1, 2);
        }
    }
    """
        method_obs = parse_methods(class_str)
        self.assertEqual(len(method_obs), 15)

    def test_parse_method(self):
        str = """
package com.example;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.*;
import java.util.HashMap;
import java.util.Date;
import java.util.Random;
import java.util.concurrent.atomic.AtomicInteger;

public class HelloWorld {
    // Public instance field with initialization
    public Map<String, List<Integer>> publicInt;
    
        // Private instance field without initialization
    private String privateString;

    // Protected instance field with initialization
    protected Date protectedDate = new Date();

    // Package-private instance field with initialization
    AtomicInteger atomicCounter = new AtomicInteger(0);

    // Method definition
    @Test()
    public static greet(String name) {
        System.out.println("Hello, " + name + "!");
        AtomicInteger x;
        // Local variable
        List<String> greetings = new ArrayList<>();
        greetings.add("Hello");
        greetings.add("Hi");
        greetings.add("Hey");

        // Using a wildcard import
        for (String greeting : greetings) {
            System.out.println(greeting + ", " + name + "!");
        }
    }

    // Method with return value
    public static int divide(int a, int b) {
        return a / b;
    }

    // Method with external class parameters and local variables
    public void processItems(Map<String, Integer> items) {
        // Local variable
        Map<String, Integer> processedItems = new HashMap<>();
        
        for (Map.Entry<String, Integer> entry : items.entrySet()) {
            processedItems.put(entry.getKey(), entry.getValue() * 2);
        }
        
        System.out.println("Processed Items: " + processedItems);
    }

    // New method using external class as field variable
    public void generateRandomNumbers(int count) {
        // Local variable
        Random random = new Random();
        List<Integer> numbers = new ArrayList<>();
        
        for (int i = 0; i < count; i++) {
            numbers.add(random.nextInt(100));
        }
        
        System.out.println("Generated Random Numbers: " + numbers);
    }

}


"""
        x = parse_class_declaration(str)[0]
        x.replace_import_types()
        j = x.convert2json()
        y = json_deserializable(j)
        print('123')


if __name__ == '__main__':
    unittest.main()
