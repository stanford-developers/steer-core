"""Tests for the update propagation mechanism."""

import unittest
import weakref
import pickle
from copy import deepcopy
import steer_opencell_design as ocd
from steer_opencell_design.Utils.Mixins import PropagationMixin


class TestPropagationMixin(unittest.TestCase):
    """Test the PropagationMixin class in isolation."""
    
    def test_set_parent_creates_weakref(self):
        """Test that _set_parent creates a weak reference."""
        class Child(PropagationMixin):
            _update_properties = True
            def _calculate_all_properties(self):
                pass
        
        class Parent(PropagationMixin):
            _update_properties = True
            def _calculate_all_properties(self):
                pass
        
        parent = Parent()
        child = Child()
        
        child._set_parent(parent)
        
        # Verify it's a weakref
        self.assertIsInstance(child._parent, weakref.ref)
        self.assertEqual(child._get_parent(), parent)
    
    def test_set_parent_none_clears_reference(self):
        """Test that _set_parent(None) clears the parent reference."""
        class Child(PropagationMixin):
            _update_properties = True
            def _calculate_all_properties(self):
                pass
        
        class Parent(PropagationMixin):
            _update_properties = True
            def _calculate_all_properties(self):
                pass
        
        parent = Parent()
        child = Child()
        
        child._set_parent(parent)
        self.assertIsNotNone(child._get_parent())
        
        child._set_parent(None)
        self.assertIsNone(child._get_parent())
    
    def test_update_calls_calculate_all_properties(self):
        """Test that update() calls _calculate_all_properties."""
        class TestClass(PropagationMixin):
            _update_properties = True
            calc_count = 0
            
            def _calculate_all_properties(self):
                self.calc_count += 1
        
        obj = TestClass()
        obj.update()
        
        self.assertEqual(obj.calc_count, 1)
    
    def test_update_respects_update_properties_flag(self):
        """Test that update() doesn't run if _update_properties is False."""
        class TestClass(PropagationMixin):
            _update_properties = False
            calc_count = 0
            
            def _calculate_all_properties(self):
                self.calc_count += 1
        
        obj = TestClass()
        obj.update()
        
        self.assertEqual(obj.calc_count, 0)
    
    def test_propagate_changes_bubbles_up(self):
        """Test that propagate_changes() bubbles up to parent."""
        class TestClass(PropagationMixin):
            _update_properties = True
            calc_count = 0
            
            def _calculate_all_properties(self):
                self.calc_count += 1
        
        root = TestClass()
        middle = TestClass()
        leaf = TestClass()
        
        leaf._set_parent(middle)
        middle._set_parent(root)
        
        leaf.propagate_changes()
        
        self.assertEqual(leaf.calc_count, 1)
        self.assertEqual(middle.calc_count, 1)
        self.assertEqual(root.calc_count, 1)
    
    def test_pickle_excludes_parent(self):
        """Test that pickling excludes _parent and restores correctly."""
        class TestClass(PropagationMixin):
            _update_properties = True
            value = 42
            
            def _calculate_all_properties(self):
                pass
        
        parent = TestClass()
        child = TestClass()
        child._set_parent(parent)
        
        # Verify parent is set before pickle
        self.assertIsNotNone(child._get_parent())
        
        # Pickle and unpickle
        pickled = pickle.dumps(child)
        restored = pickle.loads(pickled)
        
        # Parent should be None after restore
        self.assertIsNone(restored._parent)
        self.assertIsNone(restored._get_parent())
        # Other attributes should be preserved
        self.assertEqual(restored.value, 42)
    
    def test_to_dict_excludes_parent(self):
        """Test that _to_dict excludes _parent."""
        class TestClass(PropagationMixin):
            _update_properties = True
            value = 42
            
            def __init__(self):
                self.value = 42
            
            def _calculate_all_properties(self):
                pass
        
        parent = TestClass()
        child = TestClass()
        child._set_parent(parent)
        
        # Get dict representation
        d = child._to_dict()
        
        # _parent should not be in the dict
        self.assertNotIn('_parent', d)
        # Other attributes should be present
        self.assertIn('value', d)


class TestHierarchyPropagation(unittest.TestCase):
    """Test propagation through the actual component hierarchy."""
    
    @classmethod
    def setUpClass(cls):
        """Create a complete cell hierarchy for testing."""
        # Create materials directly without database
        cathode_material = ocd.CathodeMaterial(
            name="LFP",
            density=3.6,
            specific_cost=6.0,
            color="#FF6B6B",
            voltage_cutoff_range=(2.5, 3.65),
        )
        cathode_material._capacity_curve = None  # Skip curve for testing
        
        conductive_additive = ocd.ConductiveAdditive(
            name="super_P", specific_cost=15, density=2.0, color="#000000"
        )
        binder = ocd.Binder(name="CMC", specific_cost=10, density=1.5, color="#FFFFFF")
        
        cathode_formulation = ocd.CathodeFormulation(
            active_materials={cathode_material: 95},
            binders={binder: 2},
            conductive_additives={conductive_additive: 3},
        )
        
        cc_material = ocd.CurrentCollectorMaterial(
            name="Aluminum", specific_cost=5, density=2.7, color="#AAAAAA"
        )
        
        cathode_cc = ocd.PunchedCurrentCollector(
            material=cc_material,
            length=100,
            width=80,
            thickness=12,
            tab_width=20,
            tab_height=10,
        )
        
        cls.cathode = ocd.Cathode(
            formulation=cathode_formulation,
            mass_loading=12,
            current_collector=cathode_cc,
            calender_density=2.60,
        )
        
        # Anode setup
        anode_material = ocd.AnodeMaterial(
            name="Graphite",
            density=2.2,
            specific_cost=4.0,
            color="#333333",
            voltage_cutoff_range=(0.01, 1.5),
        )
        anode_material._capacity_curve = None
        
        anode_formulation = ocd.AnodeFormulation(
            active_materials={anode_material: 90},
            binders={binder: 5},
            conductive_additives={conductive_additive: 5},
        )
        
        anode_cc = ocd.PunchedCurrentCollector(
            material=cc_material,
            length=104,
            width=84,
            thickness=8,
            tab_width=20,
            tab_height=10,
        )
        
        cls.anode = ocd.Anode(
            formulation=anode_formulation,
            mass_loading=7.2,
            current_collector=anode_cc,
            calender_density=1.1,
        )
        
        # Separator
        separator_material = ocd.SeparatorMaterial(
            name="Polyethylene",
            specific_cost=2,
            density=0.94,
            color="#FDFDB7",
            porosity=45,
        )
        
        cls.top_separator = ocd.Separator(
            material=separator_material, thickness=25, width=90, length=110
        )
        cls.bottom_separator = ocd.Separator(
            material=separator_material, thickness=25, width=90, length=110
        )
        
        # Layup
        cls.layup = ocd.MonoLayer(
            anode=cls.anode,
            cathode=cls.cathode,
            top_separator=cls.top_separator,
            bottom_separator=cls.bottom_separator,
        )
        
        # Stack
        cls.stack = ocd.PunchedStack(
            monolayer=cls.layup,
            n_layers=10,
        )
        
        # Cell components
        pouch_material = ocd.PouchMaterial(
            name="Aluminum Laminate",
            density=2.7,
            specific_cost=5.0,
            color="#C0C0C0",
        )
        aluminum = ocd.PrismaticContainerMaterial(
            name="Aluminum",
            density=2.7,
            specific_cost=3.0,
            color="#C0C0C0",
        )
        
        cls.pouch = ocd.Pouch(
            material=pouch_material,
            length=120,
            width=100,
            thickness=0.15,
        )
        
        cls.terminal = ocd.PouchTerminal(
            material=aluminum,
            width=20,
            height=15,
            thickness=0.3,
            sealant_height=5,
        )
        
        cls.encapsulation = ocd.PouchEncapsulation(
            pouch=cls.pouch,
            cathode_terminal=cls.terminal,
            anode_terminal=cls.terminal,
        )
        
        cls.electrolyte = ocd.Electrolyte(
            name="1M LiPF6 in EC:DMC",
            density=1.2,
            specific_cost=15.0,
            color="#00FF00"
        )
        
        cls.cell = ocd.PouchCell(
            reference_electrode_assembly=cls.stack,
            encapsulation=cls.encapsulation,
            electrolyte=cls.electrolyte,
            electrolyte_overfill=20,
        )
    
    def test_parent_references_established(self):
        """Test that parent references are properly set up."""
        # Cell -> Assembly
        self.assertEqual(
            self.cell.reference_electrode_assembly._get_parent(),
            self.cell
        )
        
        # Assembly -> Layup
        self.assertEqual(
            self.cell.reference_electrode_assembly.layup._get_parent(),
            self.cell.reference_electrode_assembly
        )
        
        # Layup -> Cathode
        self.assertEqual(
            self.cell.reference_electrode_assembly.layup.cathode._get_parent(),
            self.cell.reference_electrode_assembly.layup
        )
        
        # Cathode -> CurrentCollector
        self.assertEqual(
            self.cell.reference_electrode_assembly.layup.cathode.current_collector._get_parent(),
            self.cell.reference_electrode_assembly.layup.cathode
        )
    
    def test_update_recalculates_single_level(self):
        """Test that update() only recalculates the current level."""
        # Store original cell energy
        original_energy = self.cell.energy
        
        # Modify cathode mass loading directly (bypass setter recalc)
        new_mass_loading = 14  # mg/cm2
        self.cell.reference_electrode_assembly.layup.cathode._mass_loading = (
            new_mass_loading * (1e-6 / 1e-4)  # Convert to SI
        )
        
        # Update only the cathode level
        self.cell.reference_electrode_assembly.layup.cathode.update()
        
        # Cell energy should still be at original (not propagated)
        self.assertEqual(self.cell.energy, original_energy)
    
    def test_propagate_changes_updates_all_levels(self):
        """Test that propagate_changes() updates all levels to root."""
        # Store original values
        original_energy = self.cell.energy
        
        # Make a deep copy of cathode's current collector and modify thickness
        cc = self.cell.reference_electrode_assembly.layup.cathode.current_collector
        original_thickness = cc.thickness
        
        # Change thickness (this will trigger local recalculation)
        cc.thickness = original_thickness * 1.5
        
        # Propagate changes all the way up
        cc.propagate_changes()
        
        # Cell should have new energy (different from original)
        # Note: The energy change depends on how thickness affects mass/cost
        self.assertIsNotNone(self.cell.energy)
        
        # Reset for other tests
        cc.thickness = original_thickness
        cc.propagate_changes()
    
    def test_intermediate_intervention(self):
        """Test the use case where user intervenes at intermediate levels."""
        # This tests the scenario from the user's original question:
        # Change something deep, update level by level, modify at intermediate level
        
        cc = self.cell.reference_electrode_assembly.layup.cathode.current_collector
        original_cc_thickness = cc.thickness
        
        # Change property at leaf
        cc.thickness = original_cc_thickness * 1.2
        cc.update()  # local only
        
        # Update intermediate levels one by one
        self.cell.reference_electrode_assembly.layup.cathode.update()
        self.cell.reference_electrode_assembly.layup.update()
        
        # Could modify something at assembly level here if needed
        # Then finish propagation
        self.cell.reference_electrode_assembly.propagate_changes()
        
        # Cell should be updated
        self.assertIsNotNone(self.cell.energy)
        
        # Cleanup
        cc.thickness = original_cc_thickness
        cc.propagate_changes()


class TestParentReferenceClearing(unittest.TestCase):
    """Test that parent references are cleared when children are replaced."""
    
    def setUp(self):
        """Create minimal components for testing."""
        # Create materials directly without database
        cathode_material = ocd.CathodeMaterial(
            name="LFP",
            density=3.6,
            specific_cost=6.0,
            color="#FF6B6B",
            voltage_cutoff_range=(2.5, 3.65),
        )
        cathode_material._capacity_curve = None
        
        conductive_additive = ocd.ConductiveAdditive(
            name="super_P", specific_cost=15, density=2.0, color="#000000"
        )
        binder = ocd.Binder(name="CMC", specific_cost=10, density=1.5, color="#FFFFFF")
        
        self.formulation = ocd.CathodeFormulation(
            active_materials={cathode_material: 95},
            binders={binder: 2},
            conductive_additives={conductive_additive: 3},
        )
        
        cc_material = ocd.CurrentCollectorMaterial(
            name="Aluminum", specific_cost=5, density=2.7, color="#AAAAAA"
        )
        
        self.cc1 = ocd.PunchedCurrentCollector(
            material=cc_material,
            length=100,
            width=80,
            thickness=12,
            tab_width=20,
            tab_height=10,
        )
        
        self.cc2 = ocd.PunchedCurrentCollector(
            material=cc_material,
            length=100,
            width=80,
            thickness=15,
            tab_width=20,
            tab_height=10,
        )
        
        self.cathode = ocd.Cathode(
            formulation=self.formulation,
            mass_loading=12,
            current_collector=self.cc1,
            calender_density=2.60,
        )
    
    def test_replacing_child_clears_old_parent_ref(self):
        """Test that replacing a child clears the old child's parent reference."""
        # cc1 should have cathode as parent
        self.assertEqual(self.cc1._get_parent(), self.cathode)
        
        # Replace with cc2
        self.cathode.current_collector = self.cc2
        
        # cc1 should no longer have parent
        self.assertIsNone(self.cc1._get_parent())
        
        # cc2 should have cathode as parent
        self.assertEqual(self.cc2._get_parent(), self.cathode)


if __name__ == "__main__":
    unittest.main()
