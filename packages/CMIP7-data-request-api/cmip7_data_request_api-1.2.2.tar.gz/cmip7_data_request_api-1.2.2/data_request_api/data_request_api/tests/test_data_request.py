#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test data_request.py
"""
from __future__ import print_function, division, unicode_literals, absolute_import

import copy
import os
import tempfile
import unittest


from data_request_api.utilities.tools import read_json_input_file_content
from data_request_api.query.data_request import DRObjects, ExperimentsGroup, VariablesGroup, Opportunity, \
    DataRequest, version
from data_request_api.query.vocabulary_server import VocabularyServer, ConstantValueObj
from data_request_api.tests import filepath


class TestDRObjects(unittest.TestCase):
    def setUp(self):
        self.dr = DataRequest.from_separated_inputs(VS_input=filepath("one_base_VS_output.json"),
                                                    DR_input=filepath("one_base_DR_output.json"))

    def test_init(self):
        with self.assertRaises(TypeError):
            DRObjects()

        with self.assertRaises(TypeError):
            DRObjects("link::my_id")

        with self.assertRaises(TypeError):
            DRObjects(self.dr)

        obj = DRObjects("link::my_id", self.dr)
        obj = DRObjects(id="link::my_id", dr=self.dr)
        self.assertEqual(obj.DR_type, "undef")

    def test_from_input(self):
        with self.assertRaises(TypeError):
            DRObjects.from_input()

        with self.assertRaises(TypeError):
            DRObjects.from_input("link::my_id")

        with self.assertRaises(TypeError):
            DRObjects.from_input(self.dr)

        obj = DRObjects.from_input(dr=self.dr, id="link::my_id")

        obj = DRObjects.from_input(dr=self.dr, id="link::my_id", DR_type="priority_level")

        obj = DRObjects.from_input(dr=self.dr, id="link::527f5c94-8c97-11ef-944e-41a8eb05f654", DR_type="priority_level")

    def test_check(self):
        obj = DRObjects("my_id", self.dr)
        obj.check()

    def test_print(self):
        obj = DRObjects(id="link::my_id", dr=self.dr)
        self.assertEqual(str(obj), "undef: undef (id: my_id)")

    def test_eq(self):
        obj = DRObjects(id="link::my_id", dr=self.dr)
        obj2 = copy.deepcopy(obj)
        self.assertEqual(obj, obj2)

        obj3 = DRObjects(id="link::my_id_2", dr=self.dr)
        self.assertNotEqual(obj, obj3)
        self.assertTrue(obj < obj3)
        self.assertFalse(obj > obj3)

    def test_hash(self):
        obj = DRObjects(id="link::my_id", dr=self.dr)
        my_set = set()
        my_set.add(obj)
        my_set.add(DRObjects(id="link::my_id_2", dr=self.dr))
        my_set.add(copy.deepcopy(obj))
        self.assertEqual(len(my_set), 2)

        my_dict = dict()
        obj2 = self.dr.find_element("cmip7_frequency", "link::63215c10-8ca5-11ef-944e-41a8eb05f654")
        obj3 = self.dr.find_element("cmip7_frequency", "link::63215c11-8ca5-11ef-944e-41a8eb05f654")
        self.assertTrue(isinstance(obj2, DRObjects))
        self.assertTrue(isinstance(obj2.name, ConstantValueObj))
        self.assertTrue(isinstance(obj3.name, ConstantValueObj))
        my_dict[obj2.id] = obj2
        my_dict[obj2.name] = obj2
        my_dict[obj3.id] = obj3
        my_dict[obj3.name] = obj3

    def test_get(self):
        obj1 = DRObjects(id="my_id", dr=self.dr)
        self.assertEqual(obj1.get("id"), "my_id")
        self.assertEqual(obj1.get("DR_type"), "undef")
        self.assertEqual(obj1.get("test"), "undef")

    def test_filter_on_request(self):
        obj1 = DRObjects(id="my_id", DR_type="test", dr=self.dr)
        obj2 = copy.deepcopy(obj1)
        obj3 = DRObjects(id="my_other_id", DR_type="test", dr=self.dr)
        obj4 = DRObjects(id="my_id", DR_type="test2", dr=self.dr)
        self.assertEqual(obj1.filter_on_request(obj2), (True, True))
        self.assertEqual(obj1.filter_on_request(obj3), (True, False))
        self.assertEqual(obj1.filter_on_request(obj4), (False, False))


class TestExperimentsGroup(unittest.TestCase):
    def setUp(self):
        self.dr = DataRequest.from_separated_inputs(VS_input=filepath("one_base_VS_output.json"),
                                                    DR_input=filepath("one_base_DR_output.json"))

    def test_init(self):
        with self.assertRaises(TypeError):
            ExperimentsGroup()

        with self.assertRaises(TypeError):
            ExperimentsGroup("link::my_id")

        with self.assertRaises(TypeError):
            ExperimentsGroup(self.dr)

        obj = ExperimentsGroup("link::my_id", self.dr)

        obj = ExperimentsGroup(id="link::my_id", dr=self.dr, name="test")
        self.assertEqual(obj.DR_type, "experiment_groups")

    def test_from_input(self):
        with self.assertRaises(TypeError):
            ExperimentsGroup.from_input()

        with self.assertRaises(TypeError):
            ExperimentsGroup.from_input("link::my_id")

        with self.assertRaises(TypeError):
            ExperimentsGroup.from_input(self.dr)

        obj = ExperimentsGroup.from_input(id="link::my_id", dr=self.dr)

        with self.assertRaises(ValueError):
            obj = ExperimentsGroup.from_input(id="link::my_id", dr=self.dr, experiments=["link::test", ])

        obj = ExperimentsGroup.from_input(id="link::my_id", dr=self.dr,
                                          experiments=["link::527f5c49-8c97-11ef-944e-41a8eb05f654", "link::527f5c3a-8c97-11ef-944e-41a8eb05f654"])

    def test_check(self):
        obj = ExperimentsGroup(id="link::my_id", dr=self.dr)
        obj.check()

        obj = ExperimentsGroup(id="link::my_id", dr=self.dr, experiments=["link::527f5c49-8c97-11ef-944e-41a8eb05f654", "link::527f5c3a-8c97-11ef-944e-41a8eb05f654"])
        obj.check()

    def test_methods(self):
        obj = ExperimentsGroup(id="link::my_id", dr=self.dr)
        self.assertEqual(obj.count(), 0)
        self.assertEqual(obj.get_experiments(), list())

        obj = ExperimentsGroup.from_input(id="link::80ab7324-a698-11ef-914a-613c0433d878", dr=self.dr,
                                          experiments=["link::527f5c49-8c97-11ef-944e-41a8eb05f654", "link::527f5c3a-8c97-11ef-944e-41a8eb05f654"])
        self.assertEqual(obj.count(), 2)
        self.assertListEqual(obj.get_experiments(),
                             [self.dr.find_element("experiments", "link::527f5c49-8c97-11ef-944e-41a8eb05f654"),
                              self.dr.find_element("experiments", "link::527f5c3a-8c97-11ef-944e-41a8eb05f654")])
        self.assertEqual(obj.get_experiments()[0].DR_type, "experiments")

    def test_print(self):
        obj = ExperimentsGroup.from_input(id="link::dafc7490-8c95-11ef-944e-41a8eb05f654", dr=self.dr,
                                          experiments=["link::527f5c3f-8c97-11ef-944e-41a8eb05f654", "link::527f5c3d-8c97-11ef-944e-41a8eb05f654"], name="historical")
        ref_str = "experiment_group: historical (id: dafc7490-8c95-11ef-944e-41a8eb05f654)"
        ref_str_2 = [
            ref_str,
            "    Experiments included:",
            "        experiment: historical (id: 527f5c3f-8c97-11ef-944e-41a8eb05f654)",
            "        experiment: esm-hist (id: 527f5c3d-8c97-11ef-944e-41a8eb05f654)"
        ]
        self.assertEqual(obj.print_content(add_content=False), [ref_str, ])
        self.assertEqual(obj.print_content(level=1, add_content=False), ["    " + ref_str, ])
        self.assertEqual(obj.print_content(), ref_str_2)
        self.assertEqual(obj.print_content(level=1), ["    " + elt for elt in ref_str_2])
        self.assertEqual(str(obj), os.linesep.join(ref_str_2))

    def test_eq(self):
        obj = ExperimentsGroup(id="link::my_id", dr=self.dr)
        obj2 = copy.deepcopy(obj)
        self.assertEqual(obj, obj2)

        obj3 = ExperimentsGroup(id="link::my_id_2", dr=self.dr)
        self.assertNotEqual(obj, obj3)

        obj4 = ExperimentsGroup(id="link::my_id", dr=self.dr, experiments=["link::527f5c3a-8c97-11ef-944e-41a8eb05f654", "link::527f5c4c-8c97-11ef-944e-41a8eb05f654"])
        self.assertNotEqual(obj, obj4)

        obj5 = DRObjects(id="link::my_id", dr=self.dr)
        self.assertNotEqual(obj, obj5)

    def test_filter_on_request(self):
        exp_grp1 = self.dr.find_element("experiment_groups", "link::80ab723e-a698-11ef-914a-613c0433d878")
        exp_grp2 = copy.deepcopy(exp_grp1)
        exp_grp3 = self.dr.find_element("experiment_groups", "link::dafc748d-8c95-11ef-944e-41a8eb05f654")
        exp_1 = self.dr.find_element("experiments", "link::527f5c53-8c97-11ef-944e-41a8eb05f654")
        exp_2 = self.dr.find_element("experiments", "link::527f5c3d-8c97-11ef-944e-41a8eb05f654")
        obj = DRObjects(id="link::my_id", dr=self.dr)
        self.assertEqual(exp_grp1.filter_on_request(exp_grp2), (True, True))
        self.assertEqual(exp_grp1.filter_on_request(exp_grp3), (True, False))
        self.assertEqual(exp_grp1.filter_on_request(exp_1), (True, True))
        self.assertEqual(exp_grp1.filter_on_request(exp_2), (True, False))
        self.assertEqual(exp_grp1.filter_on_request(obj), (False, False))


class TestVariables(unittest.TestCase):
    def setUp(self):
        self.dr = DataRequest.from_separated_inputs(VS_input=filepath("one_base_VS_output.json"),
                                                    DR_input=filepath("one_base_DR_output.json"))

    def test_print(self):
        obj = self.dr.find_element("variable", "1aab80fc-b006-11e6-9289-ac72891c3257")
        ref_str = 'variable: wo at frequency mon (id: 1aab80fc-b006-11e6-9289-ac72891c3257, title: Sea Water Vertical Velocity)'
        ref_str_2 = [
            ref_str,
        ]
        self.assertEqual(obj.print_content(add_content=False), [ref_str, ])
        self.assertEqual(obj.print_content(level=1, add_content=False), ["    " + ref_str, ])
        self.assertEqual(obj.print_content(), ref_str_2)
        self.assertEqual(obj.print_content(level=1), ["    " + elt for elt in ref_str_2])
        self.assertEqual(str(obj), os.linesep.join(ref_str_2))

    def test_filter_on_request(self):
        var_1 = self.dr.find_element("variable", "1aab80fc-b006-11e6-9289-ac72891c3257")
        var_2 = copy.deepcopy(var_1)
        var_3 = self.dr.find_element("variable", "5a070350-c77d-11e6-8a33-5404a60d96b5")
        table_1 = self.dr.find_element("table_identifier", "527f5d06-8c97-11ef-944e-41a8eb05f654")
        table_2 = self.dr.find_element("table_identifier", "527f5d03-8c97-11ef-944e-41a8eb05f654")
        tshp_1 = self.dr.find_element("temporal_shape", "cf34c974-80be-11e6-97ee-ac72891c3257")
        tshp_2 = self.dr.find_element("temporal_shape", "a06034e5-bbca-11ef-9840-9de7167a7ecb")
        sshp_1 = self.dr.find_element("spatial_shape", "a6562c2a-8883-11e5-b571-ac72891c3257")
        sshp_2 = self.dr.find_element("spatial_shape", "a6562a9a-8883-11e5-b571-ac72891c3257")
        param_1 = self.dr.find_element("physical_parameter", "d476e6113f5c466d27fd3aa9e9c35411")
        param_2 = self.dr.find_element("physical_parameter", "d76ba4c5868a0a9a02f433dc3c86d5d2")
        realm_1 = self.dr.find_element("modelling_realm", "ocean")
        realm_2 = self.dr.find_element("modelling_realm", "atmos")
        bcv_1 = self.dr.find_element("esm-bcv", "80ab7377-a698-11ef-914a-613c0433d878")
        bcv_2 = self.dr.find_element("esm-bcv", "80ab737f-a698-11ef-914a-613c0433d878")
        cf_1 = self.dr.find_element("cf_standard_name", "3ba9a909-8ca2-11ef-944e-41a8eb05f654")
        cf_2 = self.dr.find_element("cf_standard_name", "3ba9a9ae-8ca2-11ef-944e-41a8eb05f654")
        cell_method_1 = self.dr.find_element("cell_method", "a269a4cd-8c9b-11ef-944e-41a8eb05f654")
        cell_method_2 = self.dr.find_element("cell_method", "a269a4ce-8c9b-11ef-944e-41a8eb05f654")
        cell_measure_1 = self.dr.find_element("cell_measure", "a269a4f6-8c9b-11ef-944e-41a8eb05f654")
        cell_measure_2 = self.dr.find_element("cell_measure", "a269a4f4-8c9b-11ef-944e-41a8eb05f654")
        obj = DRObjects(id="link::my_id", dr=self.dr)
        self.assertEqual(var_1.filter_on_request(var_2), (True, True))
        self.assertEqual(var_1.filter_on_request(var_3), (True, False))
        self.assertEqual(var_1.filter_on_request(table_1), (True, True))
        self.assertEqual(var_1.filter_on_request(table_2), (True, False))
        self.assertEqual(var_1.filter_on_request(tshp_1), (True, True))
        self.assertEqual(var_1.filter_on_request(tshp_2), (True, False))
        self.assertEqual(var_1.filter_on_request(sshp_1), (True, True))
        self.assertEqual(var_1.filter_on_request(sshp_2), (True, False))
        self.assertEqual(var_1.filter_on_request(param_1), (True, True))
        self.assertEqual(var_1.filter_on_request(param_2), (True, False))
        self.assertEqual(var_1.filter_on_request(realm_1), (True, True))
        self.assertEqual(var_1.filter_on_request(realm_2), (True, False))
        self.assertEqual(var_1.filter_on_request(bcv_1), (True, True))
        self.assertEqual(var_1.filter_on_request(bcv_2), (True, False))
        self.assertEqual(var_1.filter_on_request(cf_1), (True, True))
        self.assertEqual(var_1.filter_on_request(cf_2), (True, False))
        self.assertEqual(var_1.filter_on_request(cell_method_1), (True, True))
        self.assertEqual(var_1.filter_on_request(cell_method_2), (True, False))
        self.assertEqual(var_1.filter_on_request(cell_measure_1), (True, True))
        self.assertEqual(var_1.filter_on_request(cell_measure_2), (True, False))
        self.assertEqual(var_1.filter_on_request(obj), (False, False))


class TestVariablesGroup(unittest.TestCase):
    def setUp(self):
        self.dr = DataRequest.from_separated_inputs(DR_input=filepath("one_base_DR_output.json"),
                                                    VS_input=filepath("one_base_VS_output.json"))

    def test_init(self):
        with self.assertRaises(TypeError):
            VariablesGroup()

        with self.assertRaises(TypeError):
            VariablesGroup("link::my_id")

        with self.assertRaises(TypeError):
            VariablesGroup(self.dr)

        obj = VariablesGroup("link::my_id", self.dr)
        self.assertEqual(obj.DR_type, "variable_groups")

        with self.assertRaises(ValueError):
            VariablesGroup("link::my_id", self.dr, name="test", physical_parameter="link::my_link")

    def test_from_input(self):
        with self.assertRaises(TypeError):
            VariablesGroup.from_input()

        with self.assertRaises(TypeError):
            VariablesGroup.from_input("link::my_id")

        with self.assertRaises(TypeError):
            VariablesGroup.from_input(self.dr)

        obj = VariablesGroup.from_input(id="link::my_id", dr=self.dr)

        with self.assertRaises(ValueError):
            obj = VariablesGroup.from_input(id="link:my_id", dr=self.dr, variables=["link::test", ])

        obj = VariablesGroup.from_input(id="link::my_id", dr=self.dr,
                                        variables=["link::bab3cb52-e5dd-11e5-8482-ac72891c3257",
                                                   "link::bab48ce0-e5dd-11e5-8482-ac72891c3257"])

    def test_check(self):
        obj = VariablesGroup(id="link::my_id", dr=self.dr)
        obj.check()

        obj = VariablesGroup(id="link::my_id", dr=self.dr,
                             variables=["link::bab3cb52-e5dd-11e5-8482-ac72891c3257",
                                        "link::bab48ce0-e5dd-11e5-8482-ac72891c3257"])
        obj.check()

    def test_methods(self):
        obj = VariablesGroup.from_input(id="link::my_id", dr=self.dr, priority_level="High")
        self.assertEqual(obj.count(), 0)
        self.assertEqual(obj.get_variables(), list())
        self.assertEqual(obj.get_mips(), list())
        self.assertEqual(obj.get_priority_level(), self.dr.find_element("priority_level", "High"))

        obj = VariablesGroup.from_input(id="link::dafc7484-8c95-11ef-944e-41a8eb05f654", dr=self.dr,
                                        variables=["link::bab3cb52-e5dd-11e5-8482-ac72891c3257",
                                                   "link::bab48ce0-e5dd-11e5-8482-ac72891c3257"],
                                        mips=["link::527f5c7f-8c97-11ef-944e-41a8eb05f654", ], priority_level="High")
        self.assertEqual(obj.count(), 2)
        self.assertListEqual(obj.get_variables(),
                             [self.dr.find_element("variables", "link::bab3cb52-e5dd-11e5-8482-ac72891c3257"),
                              self.dr.find_element("variables", "link::bab48ce0-e5dd-11e5-8482-ac72891c3257")])
        self.assertEqual(obj.get_mips(), [self.dr.find_element("mips", "link::527f5c7f-8c97-11ef-944e-41a8eb05f654")])
        self.assertDictEqual(obj.get_priority_level().attributes,
                             {'name': "High", "notes": "The variables support the core objectives of the opportunity.  These are required to make the opportunity viable.", "value": 2,
                              'id': "527f5c94-8c97-11ef-944e-41a8eb05f654", 'uid': '527f5c94-8c97-11ef-944e-41a8eb05f654'})

    def test_filter_on_request(self):
        var_grp1 = self.dr.find_element("variable_groups", "dafc743a-8c95-11ef-944e-41a8eb05f654")
        var_grp2 = copy.deepcopy(var_grp1)
        var_grp3 = self.dr.find_element("variable_groups", "dafc7435-8c95-11ef-944e-41a8eb05f654")
        var_2 = self.dr.find_element("variable", "baa71c7c-e5dd-11e5-8482-ac72891c3257")
        var_1 = self.dr.find_element("variable", "83bbfc6e-7f07-11ef-9308-b1dd71e64bec")
        mip_2 = self.dr.find_element("mips", "527f5c7d-8c97-11ef-944e-41a8eb05f654")
        mip_1 = self.dr.find_element("mips", "527f5c6c-8c97-11ef-944e-41a8eb05f654")
        prio_2 = self.dr.find_element("priority_level", "527f5c94-8c97-11ef-944e-41a8eb05f654")
        prio_1 = self.dr.find_element("priority_level", "527f5c95-8c97-11ef-944e-41a8eb05f654")
        max_prio_1 = self.dr.find_element("max_priority_level", "527f5c95-8c97-11ef-944e-41a8eb05f654")
        max_prio_2 = self.dr.find_element("max_priority_level", "527f5c94-8c97-11ef-944e-41a8eb05f654")
        table_1 = self.dr.find_element("table_identifier", "527f5d03-8c97-11ef-944e-41a8eb05f654")
        table_2 = self.dr.find_element("table_identifier", "527f5d06-8c97-11ef-944e-41a8eb05f654")
        tshp_1 = self.dr.find_element("temporal_shape", "cf34c974-80be-11e6-97ee-ac72891c3257")
        tshp_2 = self.dr.find_element("temporal_shape", "a06034e5-bbca-11ef-9840-9de7167a7ecb")
        sshp_1 = self.dr.find_element("spatial_shape", "a656047a-8883-11e5-b571-ac72891c3257")
        sshp_2 = self.dr.find_element("spatial_shape", "a65615fa-8883-11e5-b571-ac72891c3257")
        param_1 = self.dr.find_element("physical_parameter", "2fabd221-a80c-11ef-851e-c9d2077e3a3c")
        param_2 = self.dr.find_element("physical_parameter", "00e77372e8b909d9a827a0790e991fd9")
        realm_1 = self.dr.find_element("modelling_realm", "ocean")
        realm_2 = self.dr.find_element("modelling_realm", "atmos")
        bcv_2 = self.dr.find_element("esm-bcv", "link::80ab7303-a698-11ef-914a-613c0433d878")
        cf_std_1 = self.dr.find_element("cf_standard_name", "3ba8dccf-8ca2-11ef-944e-41a8eb05f654")
        cf_std_2 = self.dr.find_element("cf_standard_name", "3ba9a9af-8ca2-11ef-944e-41a8eb05f654")
        cell_method_1 = self.dr.find_element("cell_methods", "a269a4cd-8c9b-11ef-944e-41a8eb05f654")
        cell_method_2 = self.dr.find_element("cell_methods", "a269a4e2-8c9b-11ef-944e-41a8eb05f654")
        cell_measure_1 = self.dr.find_element("cell_measure", "link::a269a4f5-8c9b-11ef-944e-41a8eb05f654")
        cell_measure_2 = self.dr.find_element("cell_measure", "link::a269a4f8-8c9b-11ef-944e-41a8eb05f654")
        obj = DRObjects(id="link::my_id", dr=self.dr)
        self.assertEqual(var_grp1.filter_on_request(var_grp2), (True, True))
        self.assertEqual(var_grp1.filter_on_request(var_grp3), (True, False))
        self.assertEqual(var_grp1.filter_on_request(var_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(var_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(mip_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(mip_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(prio_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(prio_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(max_prio_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(max_prio_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(table_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(table_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(tshp_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(tshp_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(sshp_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(sshp_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(param_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(param_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(realm_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(realm_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(bcv_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(cf_std_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(cf_std_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(cell_method_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(cell_method_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(cell_measure_1), (True, True))
        self.assertEqual(var_grp1.filter_on_request(cell_measure_2), (True, False))
        self.assertEqual(var_grp1.filter_on_request(obj), (False, False))

    def test_print(self):
        obj = VariablesGroup.from_input(id="link::dafc73dd-8c95-11ef-944e-41a8eb05f654", dr=self.dr, priority_level="Medium",
                                        name="baseline_monthly",
                                        variables=["link::bab3cb52-e5dd-11e5-8482-ac72891c3257",
                                                   "link::bab48ce0-e5dd-11e5-8482-ac72891c3257"])
        ref_str = "variable_group: baseline_monthly (id: dafc73dd-8c95-11ef-944e-41a8eb05f654)"
        ref_str_2 = [
            ref_str,
            "    Variables included:",
            "        variable: pr at frequency mon (id: bab3cb52-e5dd-11e5-8482-ac72891c3257, title: Precipitation)",
            "        variable: psl at frequency mon (id: bab48ce0-e5dd-11e5-8482-ac72891c3257, "
            "title: Sea Level Pressure)"
        ]
        self.assertEqual(obj.print_content(add_content=False), [ref_str, ])
        self.assertEqual(obj.print_content(level=1, add_content=False), ["    " + ref_str, ])
        self.assertEqual(obj.print_content(), ref_str_2)
        self.assertEqual(obj.print_content(level=1), ["    " + elt for elt in ref_str_2])
        self.assertEqual(str(obj), os.linesep.join(ref_str_2))

    def test_eq(self):
        obj = VariablesGroup(id="link::my_id", dr=self.dr)
        obj2 = copy.deepcopy(obj)
        self.assertEqual(obj, obj2)

        obj3 = VariablesGroup(id="link::my_id_2", dr=self.dr)
        self.assertNotEqual(obj, obj3)

        obj4 = VariablesGroup(id="link::my_id", dr=self.dr, variables=["link::bab3cb52-e5dd-11e5-8482-ac72891c3257",
                                                                       "link::bab48ce0-e5dd-11e5-8482-ac72891c3257"])
        self.assertNotEqual(obj, obj4)

        obj5 = VariablesGroup(id="link::my_id", dr=self.dr, mips=["link::527f5c7f-8c97-11ef-944e-41a8eb05f654", ])
        self.assertNotEqual(obj, obj5)

        obj6 = VariablesGroup(id="link::my_id", dr=self.dr, priority="Medium")
        self.assertNotEqual(obj, obj6)

        obj7 = DRObjects(id="link::my_id", dr=self.dr)
        self.assertNotEqual(obj, obj7)


class TestOpportunity(unittest.TestCase):
    def setUp(self):
        self.dr = DataRequest.from_separated_inputs(DR_input=filepath("one_base_DR_output.json"),
                                                    VS_input=filepath("one_base_VS_output.json"))

    def test_init(self):
        with self.assertRaises(TypeError):
            Opportunity()

        with self.assertRaises(TypeError):
            Opportunity("my_id")

        with self.assertRaises(TypeError):
            Opportunity(self.dr)

        obj = Opportunity("my_id", self.dr)

        obj = Opportunity(id="my_id", dr=self.dr, variables_groups=["test1", "test2"],
                          experiments_groups=["test3", "test4"], themes=["theme1", "theme2"])
        self.assertEqual(obj.DR_type, "opportunities")

    def test_from_input(self):
        with self.assertRaises(TypeError):
            Opportunity.from_input()

        with self.assertRaises(TypeError):
            Opportunity.from_input("my_id")

        with self.assertRaises(TypeError):
            Opportunity.from_input(self.dr)

        obj = Opportunity.from_input("my_id", self.dr)

        obj = Opportunity.from_input(id="my_id", dr=self.dr)

        with self.assertRaises(ValueError):
            obj = Opportunity.from_input(id="my_id", dr=self.dr, variable_groups=["test", ])

        obj = Opportunity.from_input(id="my_id", dr=self.dr,
                                     variable_groups=["link::dafc747f-8c95-11ef-944e-41a8eb05f654", "link::dafc7428-8c95-11ef-944e-41a8eb05f654"],
                                     experiment_groups=["link::dafc748e-8c95-11ef-944e-41a8eb05f654", ],
                                     data_request_themes=["link::527f5c90-8c97-11ef-944e-41a8eb05f654", "link::527f5c93-8c97-11ef-944e-41a8eb05f654",
                                                          "link::527f5c8f-8c97-11ef-944e-41a8eb05f654"])

    def test_check(self):
        obj = Opportunity(id="my_id", dr=self.dr)
        obj.check()

        obj = Opportunity(id="my_id", dr=self.dr, variables_groups=["default_733", "default_734"])
        obj.check()

    def test_methods(self):
        obj = Opportunity(id="my_id", dr=self.dr)
        self.assertEqual(obj.get_experiment_groups(), list())
        self.assertEqual(obj.get_variable_groups(), list())
        self.assertEqual(obj.get_themes(), list())

        obj = Opportunity.from_input(id="link::default_425", dr=self.dr,
                                     variable_groups=["link::dafc747f-8c95-11ef-944e-41a8eb05f654", "link::dafc7428-8c95-11ef-944e-41a8eb05f654"],
                                     experiment_groups=["link::dafc748e-8c95-11ef-944e-41a8eb05f654", ],
                                     data_request_themes=["link::527f5c93-8c97-11ef-944e-41a8eb05f654", "link::527f5c8f-8c97-11ef-944e-41a8eb05f654",
                                                          "link::527f5c92-8c97-11ef-944e-41a8eb05f654"])
        self.assertListEqual(obj.get_experiment_groups(), [self.dr.find_element("experiment_groups", "dafc748e-8c95-11ef-944e-41a8eb05f654")])
        self.assertListEqual(obj.get_variable_groups(),
                             [self.dr.find_element("variable_groups", "link::dafc747f-8c95-11ef-944e-41a8eb05f654"),
                              self.dr.find_element("variable_groups", "link::dafc7428-8c95-11ef-944e-41a8eb05f654")])
        self.assertListEqual(obj.get_themes(),
                             [self.dr.find_element("data_request_themes", "link::527f5c93-8c97-11ef-944e-41a8eb05f654"),
                              self.dr.find_element("data_request_themes", "link::527f5c8f-8c97-11ef-944e-41a8eb05f654"),
                              self.dr.find_element("data_request_themes", "link::527f5c92-8c97-11ef-944e-41a8eb05f654")
                              ])

    def test_print(self):
        obj = Opportunity.from_input(id="link::dafc73a5-8c95-11ef-944e-41a8eb05f654", dr=self.dr, name="Ocean Extremes",
                                     variable_groups=["link::dafc73dd-8c95-11ef-944e-41a8eb05f654", "link::dafc73de-8c95-11ef-944e-41a8eb05f654"],
                                     experiment_groups=["link::dafc748e-8c95-11ef-944e-41a8eb05f654", ],
                                     data_request_themes=["link::527f5c90-8c97-11ef-944e-41a8eb05f654", "link::527f5c8f-8c97-11ef-944e-41a8eb05f654",
                                                          "link::527f5c91-8c97-11ef-944e-41a8eb05f654"])
        ref_str = "opportunity: Ocean Extremes (id: dafc73a5-8c95-11ef-944e-41a8eb05f654)"
        ref_str_2 = [
            ref_str,
            "    Experiments groups included:",
            "        experiment_group: fast-track (id: dafc748e-8c95-11ef-944e-41a8eb05f654)",
            "    Variables groups included:",
            "        variable_group: baseline_monthly (id: dafc73dd-8c95-11ef-944e-41a8eb05f654)",
            "        variable_group: baseline_subdaily (id: dafc73de-8c95-11ef-944e-41a8eb05f654)",
            "    Themes included:",
            "        data_request_theme: Atmosphere (id: 527f5c90-8c97-11ef-944e-41a8eb05f654)",
            "        data_request_theme: Impacts & Adaptation (id: 527f5c8f-8c97-11ef-944e-41a8eb05f654)",
            "        data_request_theme: Land & Land-Ice (id: 527f5c91-8c97-11ef-944e-41a8eb05f654)",
            "    Time subsets included:"
        ]
        self.assertEqual(obj.print_content(add_content=False), [ref_str, ])
        self.assertEqual(obj.print_content(level=1, add_content=False), ["    " + ref_str, ])
        self.assertEqual(obj.print_content(), ref_str_2)
        self.assertEqual(obj.print_content(level=1), ["    " + elt for elt in ref_str_2])
        self.assertEqual(str(obj), os.linesep.join(ref_str_2))

    def test_eq(self):
        obj = Opportunity(id="my_id", dr=self.dr)
        obj2 = copy.deepcopy(obj)
        self.assertEqual(obj, obj2)

        obj3 = Opportunity(id="my_id_2", dr=self.dr)
        self.assertNotEqual(obj, obj3)

        obj4 = Opportunity(id="my_id", dr=self.dr, experiments_groups=["dafc748e-8c95-11ef-944e-41a8eb05f654", ])
        self.assertNotEqual(obj, obj4)

        obj5 = Opportunity(id="my_id", dr=self.dr, variables_groups=["default_733", "default_734"])
        self.assertNotEqual(obj, obj5)

        obj6 = Opportunity(id="my_id", dr=self.dr, themes=["63215c10-8ca5-11ef-944e-41a8eb05f654", "63215c11-8ca5-11ef-944e-41a8eb05f654", "default_106"])
        self.assertNotEqual(obj, obj6)

        obj7 = DRObjects(id="my_id", dr=self.dr)
        self.assertNotEqual(obj, obj7)

    def test_filter_on_request(self):
        op_1 = self.dr.find_element("opportunities", "dafc73a5-8c95-11ef-944e-41a8eb05f654")
        op_2 = copy.deepcopy(op_1)
        op_3 = self.dr.find_element("opportunities", "dafc73bd-8c95-11ef-944e-41a8eb05f654")
        theme_1 = self.dr.find_element("data_request_theme", "527f5c90-8c97-11ef-944e-41a8eb05f654")
        theme_2 = self.dr.find_element("data_request_theme", "527f5c92-8c97-11ef-944e-41a8eb05f654")
        var_grp_1 = self.dr.find_element("variable_group", "dafc747f-8c95-11ef-944e-41a8eb05f654")
        var_grp_2 = self.dr.find_element("variable_group", "dafc7428-8c95-11ef-944e-41a8eb05f654")
        exp_grp_1 = self.dr.find_element("experiment_group", "dafc7490-8c95-11ef-944e-41a8eb05f654")
        exp_grp_2 = self.dr.find_element("experiment_group", "dafc748e-8c95-11ef-944e-41a8eb05f654")
        exp_1 = self.dr.find_element("experiment", "527f5c3d-8c97-11ef-944e-41a8eb05f654")
        exp_2 = self.dr.find_element("experiment", "527f5c40-8c97-11ef-944e-41a8eb05f654")
        time_1 = self.dr.find_element("time_subset", "link::527f5cac-8c97-11ef-944e-41a8eb05f654")
        var_2 = self.dr.find_element("variable", "5a070350-c77d-11e6-8a33-5404a60d96b5")
        var_1 = self.dr.find_element("variable", "83bbfc6e-7f07-11ef-9308-b1dd71e64bec")
        mip_2 = self.dr.find_element("mips", "527f5c77-8c97-11ef-944e-41a8eb05f654")
        mip_1 = self.dr.find_element("mips", "527f5c6c-8c97-11ef-944e-41a8eb05f654")
        prio_2 = self.dr.find_element("priority_level", "527f5c94-8c97-11ef-944e-41a8eb05f654")
        prio_1 = self.dr.find_element("priority_level", "527f5c95-8c97-11ef-944e-41a8eb05f654")
        max_prio_1 = self.dr.find_element("max_priority_level", "527f5c95-8c97-11ef-944e-41a8eb05f654")
        max_prio_2 = self.dr.find_element("max_priority_level", "527f5c94-8c97-11ef-944e-41a8eb05f654")
        table_1 = self.dr.find_element("table_identifier", "527f5d03-8c97-11ef-944e-41a8eb05f654")
        table_2 = self.dr.find_element("table_identifier", "527f5ce9-8c97-11ef-944e-41a8eb05f654")
        tshp_1 = self.dr.find_element("temporal_shape", "cf34c974-80be-11e6-97ee-ac72891c3257")
        tshp_2 = self.dr.find_element("temporal_shape", "a06034e5-bbca-11ef-9840-9de7167a7ecb")
        sshp_1 = self.dr.find_element("spatial_shape", "a656047a-8883-11e5-b571-ac72891c3257")
        sshp_2 = self.dr.find_element("spatial_shape", "a65615fa-8883-11e5-b571-ac72891c3257")
        param_1 = self.dr.find_element("physical_parameter", "3e3ddc77800e7d421834b9cb808602d7")
        param_2 = self.dr.find_element("physical_parameter", "00e77372e8b909d9a827a0790e991fd9")
        realm_1 = self.dr.find_element("modelling_realm", "ocean")
        realm_2 = self.dr.find_element("modelling_realm", "land")
        bcv_2 = self.dr.find_element("esm-bcv", "link::80ab7303-a698-11ef-914a-613c0433d878")
        cf_std_1 = self.dr.find_element("cf_standard_name", "3ba8131b-8ca2-11ef-944e-41a8eb05f654")
        cf_std_2 = self.dr.find_element("cf_standard_name", "3ba9a9af-8ca2-11ef-944e-41a8eb05f654")
        cell_method_1 = self.dr.find_element("cell_methods", "a269a4cd-8c9b-11ef-944e-41a8eb05f654")
        cell_method_2 = self.dr.find_element("cell_methods", "a269a4c3-8c9b-11ef-944e-41a8eb05f654")
        cell_measure_1 = self.dr.find_element("cell_measure", "link::a269a4f5-8c9b-11ef-944e-41a8eb05f654")
        cell_measure_2 = self.dr.find_element("cell_measure", "link::a269a4f8-8c9b-11ef-944e-41a8eb05f654")
        obj = DRObjects(id="link::my_id", dr=self.dr)
        self.assertEqual(op_1.filter_on_request(op_2), (True, True))
        self.assertEqual(op_1.filter_on_request(op_3), (True, False))
        self.assertEqual(op_3.filter_on_request(theme_1), (True, True))
        self.assertEqual(op_3.filter_on_request(theme_2), (True, False))
        self.assertEqual(op_3.filter_on_request(exp_1), (True, True))
        self.assertEqual(op_3.filter_on_request(exp_2), (True, False))
        self.assertEqual(op_3.filter_on_request(time_1), (True, True))
        self.assertEqual(op_1.filter_on_request(time_1), (True, False))
        self.assertEqual(op_3.filter_on_request(exp_grp_1), (True, True))
        self.assertEqual(op_3.filter_on_request(exp_grp_2), (True, False))
        self.assertEqual(op_1.filter_on_request(var_grp_1), (True, True))
        self.assertEqual(op_1.filter_on_request(var_grp_2), (True, False))
        self.assertEqual(op_1.filter_on_request(var_1), (True, True))
        self.assertEqual(op_1.filter_on_request(var_2), (True, False))
        self.assertEqual(op_1.filter_on_request(mip_1), (True, True))
        self.assertEqual(op_1.filter_on_request(mip_2), (True, False))
        self.assertEqual(op_1.filter_on_request(prio_1), (True, True))
        self.assertEqual(op_1.filter_on_request(prio_2), (True, True))
        self.assertEqual(op_1.filter_on_request(max_prio_1), (True, True))
        self.assertEqual(op_1.filter_on_request(max_prio_2), (True, True))
        self.assertEqual(op_1.filter_on_request(table_1), (True, True))
        self.assertEqual(op_1.filter_on_request(table_2), (True, False))
        self.assertEqual(op_1.filter_on_request(tshp_1), (True, True))
        self.assertEqual(op_1.filter_on_request(tshp_2), (True, False))
        self.assertEqual(op_1.filter_on_request(sshp_1), (True, True))
        self.assertEqual(op_1.filter_on_request(sshp_2), (True, False))
        self.assertEqual(op_1.filter_on_request(param_1), (True, True))
        self.assertEqual(op_1.filter_on_request(param_2), (True, False))
        self.assertEqual(op_1.filter_on_request(realm_1), (True, True))
        self.assertEqual(op_1.filter_on_request(realm_2), (True, False))
        self.assertEqual(op_1.filter_on_request(bcv_2), (True, False))
        self.assertEqual(op_1.filter_on_request(cf_std_1), (True, True))
        self.assertEqual(op_1.filter_on_request(cf_std_2), (True, False))
        self.assertEqual(op_1.filter_on_request(cell_method_1), (True, True))
        self.assertEqual(op_1.filter_on_request(cell_method_2), (True, False))
        self.assertEqual(op_1.filter_on_request(cell_measure_1), (True, True))
        self.assertEqual(op_1.filter_on_request(cell_measure_2), (True, False))
        self.assertEqual(op_1.filter_on_request(obj), (False, False))


class TestDataRequest(unittest.TestCase):
    def setUp(self):
        self.vs_file = filepath("one_base_VS_output.json")
        self.vs_dict = read_json_input_file_content(self.vs_file)
        self.vs = VocabularyServer.from_input(self.vs_file)
        self.input_database_file = filepath("one_base_DR_output.json")
        self.input_database = read_json_input_file_content(self.input_database_file)
        self.complete_input_file = filepath("one_base_input.json")
        self.complete_input = read_json_input_file_content(self.complete_input_file)
        self.DR_dump = filepath("one_base_DR_dump.txt")

    def test_init(self):
        with self.assertRaises(TypeError):
            DataRequest()

        with self.assertRaises(TypeError):
            DataRequest(self.vs)

        with self.assertRaises(TypeError):
            DataRequest(self.input_database)

        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        self.assertEqual(len(obj.get_experiment_groups()), 7)
        self.assertEqual(len(obj.get_variable_groups()), 13)
        self.assertEqual(len(obj.get_opportunities()), 4)

    def test_from_input(self):
        with self.assertRaises(TypeError):
            DataRequest.from_input()

        with self.assertRaises(TypeError):
            DataRequest.from_input(self.complete_input)

        with self.assertRaises(TypeError):
            DataRequest.from_input("test")

        with self.assertRaises(TypeError):
            DataRequest.from_input(self.input_database, version=self.vs)

        with self.assertRaises(TypeError):
            DataRequest.from_input(self.complete_input_file + "tmp", version="test")

        obj = DataRequest.from_input(json_input=self.complete_input, version="test")
        self.assertEqual(len(obj.get_experiment_groups()), 7)
        self.assertEqual(len(obj.get_variable_groups()), 13)
        self.assertEqual(len(obj.get_opportunities()), 4)

        obj = DataRequest.from_input(json_input=self.complete_input_file, version="test")
        self.assertEqual(len(obj.get_experiment_groups()), 7)
        self.assertEqual(len(obj.get_variable_groups()), 13)
        self.assertEqual(len(obj.get_opportunities()), 4)

    def test_from_separated_inputs(self):
        with self.assertRaises(TypeError):
            DataRequest.from_separated_inputs()

        with self.assertRaises(TypeError):
            DataRequest.from_separated_inputs(self.input_database)

        with self.assertRaises(TypeError):
            DataRequest.from_separated_inputs(self.vs)

        with self.assertRaises(TypeError):
            DataRequest.from_separated_inputs(DR_input=self.input_database, VS_input=self.vs_file + "tmp")

        with self.assertRaises(TypeError):
            DataRequest.from_separated_inputs(DR_input=self.input_database_file + "tmp", VS_input=self.vs_dict)

        with self.assertRaises(TypeError):
            DataRequest.from_separated_inputs(DR_input=self.input_database_file, VS_input=self.vs)

        obj = DataRequest.from_separated_inputs(DR_input=self.input_database, VS_input=self.vs_dict)
        self.assertEqual(len(obj.get_experiment_groups()), 7)
        self.assertEqual(len(obj.get_variable_groups()), 13)
        self.assertEqual(len(obj.get_opportunities()), 4)

        obj = DataRequest.from_separated_inputs(DR_input=self.input_database_file, VS_input=self.vs_dict)
        self.assertEqual(len(obj.get_experiment_groups()), 7)
        self.assertEqual(len(obj.get_variable_groups()), 13)
        self.assertEqual(len(obj.get_opportunities()), 4)

        obj = DataRequest.from_separated_inputs(DR_input=self.input_database, VS_input=self.vs_file)
        self.assertEqual(len(obj.get_experiment_groups()), 7)
        self.assertEqual(len(obj.get_variable_groups()), 13)
        self.assertEqual(len(obj.get_opportunities()), 4)

        obj = DataRequest.from_separated_inputs(DR_input=self.input_database_file, VS_input=self.vs_file)
        self.assertEqual(len(obj.get_experiment_groups()), 7)
        self.assertEqual(len(obj.get_variable_groups()), 13)
        self.assertEqual(len(obj.get_opportunities()), 4)

    def test_split_content_from_input_json(self):
        with self.assertRaises(TypeError):
            DataRequest._split_content_from_input_json()

        with self.assertRaises(TypeError):
            DataRequest._split_content_from_input_json(self.complete_input)

        with self.assertRaises(TypeError):
            DataRequest._split_content_from_input_json("test")

        with self.assertRaises(TypeError):
            DataRequest._split_content_from_input_json(self.input_database, version=self.vs)

        with self.assertRaises(TypeError):
            DataRequest._split_content_from_input_json(self.complete_input_file + "tmp", version="test")

        DR, VS = DataRequest._split_content_from_input_json(input_json=self.complete_input, version="test")
        self.assertDictEqual(DR, self.input_database)
        self.assertDictEqual(VS, self.vs_dict)

        DR, VS = DataRequest._split_content_from_input_json(input_json=self.complete_input_file, version="test")
        self.assertDictEqual(DR, self.input_database)
        self.assertDictEqual(VS, self.vs_dict)

    def test_check(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        obj.check()

    def test_version(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        self.assertEqual(obj.software_version, version)
        self.assertEqual(obj.content_version, self.input_database["version"])
        self.assertEqual(obj.version, f"Software {version} - Content {self.input_database['version']}")

    def test_str(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        with open(self.DR_dump, encoding="utf-8", newline="\n") as f:
            ref_str = f.read()
        self.assertEqual(str(obj), ref_str)

    def test_get_experiment_groups(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        exp_groups = obj.get_experiment_groups()
        self.assertEqual(len(exp_groups), 7)
        self.assertListEqual(exp_groups,
                             [obj.find_element("experiment_groups", id)
                              for id in ["80ab723e-a698-11ef-914a-613c0433d878", "80ab72c9-a698-11ef-914a-613c0433d878",
                                         "80ac3142-a698-11ef-914a-613c0433d878", "dafc748d-8c95-11ef-944e-41a8eb05f654",
                                         "dafc748e-8c95-11ef-944e-41a8eb05f654", "dafc748f-8c95-11ef-944e-41a8eb05f654",
                                         "dafc7490-8c95-11ef-944e-41a8eb05f654"]])

    def test_get_experiment_group(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        exp_grp = obj.get_experiment_group("link::dafc748e-8c95-11ef-944e-41a8eb05f654")
        self.assertEqual(exp_grp,
                         obj.find_element("experiment_groups", "link::dafc748e-8c95-11ef-944e-41a8eb05f654"))
        with self.assertRaises(ValueError):
            exp_grp = obj.get_experiment_group("test")

    def test_get_opportunities(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        opportunities = obj.get_opportunities()
        self.assertEqual(len(opportunities), 4)
        self.assertListEqual(opportunities, [obj.find_element("opportunities", id)
                                             for id in ["dafc739e-8c95-11ef-944e-41a8eb05f654", "dafc739f-8c95-11ef-944e-41a8eb05f654",
                                                        "dafc73a5-8c95-11ef-944e-41a8eb05f654", "dafc73bd-8c95-11ef-944e-41a8eb05f654"]])

    def test_get_opportunity(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        opportunity = obj.get_opportunity("link::dafc73bd-8c95-11ef-944e-41a8eb05f654")
        self.assertEqual(opportunity,
                         obj.find_element("opportunities", "link::dafc73bd-8c95-11ef-944e-41a8eb05f654"))
        with self.assertRaises(ValueError):
            op = obj.get_opportunity("test")

    def test_get_variable_groups(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        var_groups = obj.get_variable_groups()
        self.assertEqual(len(var_groups), 13)
        self.assertListEqual(var_groups,
                             [obj.find_element("variable_groups", id)
                              for id in ["80ab723b-a698-11ef-914a-613c0433d878", "80ab73e2-a698-11ef-914a-613c0433d878",
                                         "80ab73e4-a698-11ef-914a-613c0433d878", "dafc73da-8c95-11ef-944e-41a8eb05f654",
                                         "dafc73dc-8c95-11ef-944e-41a8eb05f654", "dafc73dd-8c95-11ef-944e-41a8eb05f654",
                                         "dafc73de-8c95-11ef-944e-41a8eb05f654", "dafc7428-8c95-11ef-944e-41a8eb05f654",
                                         "dafc7435-8c95-11ef-944e-41a8eb05f654", "dafc7436-8c95-11ef-944e-41a8eb05f654",
                                         "dafc743a-8c95-11ef-944e-41a8eb05f654", "dafc7464-8c95-11ef-944e-41a8eb05f654",
                                         "dafc747f-8c95-11ef-944e-41a8eb05f654"]])

    def test_get_variable_group(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        var_grp = obj.get_variable_group("link::dafc73dd-8c95-11ef-944e-41a8eb05f654")
        self.assertEqual(var_grp,
                         obj.find_element("variable_groups", "link::dafc73dd-8c95-11ef-944e-41a8eb05f654"))
        with self.assertRaises(ValueError):
            var_grp = obj.get_variable_group("test")

    def test_get_variables(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        variables = obj.get_variables()
        self.assertListEqual(variables,
                             [obj.find_element("variables", f"link::{nb}")
                              for nb in sorted(list(self.vs.vocabulary_server["variables"]))])

    def test_get_mips(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        mips = obj.get_mips()
        self.assertListEqual(mips,
                             [obj.find_element("mips", f"link::{nb}")
                              for nb in sorted(list(self.vs.vocabulary_server["mips"]))])

    def test_get_experiments(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        experiments = obj.get_experiments()
        self.assertListEqual(experiments,
                             [obj.find_element("experiments", f"link::{nb}")
                              for nb in sorted(list(self.vs.vocabulary_server["experiments"]))])

    def test_get_themes(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        themes = obj.get_data_request_themes()
        self.assertListEqual(themes,
                             [obj.find_element("data_request_themes", f"link::{nb}")
                              for nb in sorted(list(self.vs.vocabulary_server["data_request_themes"]))])

    def test_get_filtering_structure(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        self.assertSetEqual(obj.get_filtering_structure("variable_groups"), {"opportunities", })
        self.assertSetEqual(obj.get_filtering_structure("variables"), {"opportunities", "variable_groups"})
        self.assertSetEqual(obj.get_filtering_structure("physical_parameters"), {"opportunities", "variable_groups", "variables"})
        self.assertSetEqual(obj.get_filtering_structure("experiment_groups"), {"opportunities", })
        self.assertSetEqual(obj.get_filtering_structure("experiments"), {"opportunities", "experiment_groups"})
        self.assertSetEqual(obj.get_filtering_structure("test"), set())
        self.assertSetEqual(obj.get_filtering_structure("opportunities"), set())

    def test_find_element(self):
        obj = DataRequest(input_database=self.input_database, VS=self.vs)
        elt1 = obj.find_element("theme", "Atmosphere")
        self.assertEqual(elt1.DR_type, "data_request_themes")
        elt2 = obj.find_element("priority_level", "Medium")
        self.assertEqual(elt2.DR_type, "priority_levels")
        elt3 = obj.find_element("max_priority_level", "High")
        self.assertEqual(elt3.DR_type, "max_priority_levels")


class TestDataRequestFilter(unittest.TestCase):
    def setUp(self):
        self.vs_file = filepath("one_base_VS_output.json")
        self.vs = VocabularyServer.from_input(self.vs_file)
        self.input_database_file = filepath("one_base_DR_output.json")
        self.input_database = read_json_input_file_content(self.input_database_file)
        self.dr = DataRequest(input_database=self.input_database, VS=self.vs)
        self.exp_export = filepath("experiments_export.txt")
        self.exp_expgrp_summmary = filepath("exp_expgrp_summary.txt")
        self.maxDiff = None

    def test_element_per_identifier_from_vs(self):
        id_var = "link::1aab80fc-b006-11e6-9289-ac72891c3257"
        name_var = "ocean.wo.tavg-ol-hxy-sea.mon.GLB"
        target_var = self.dr.find_element("variables", id_var)
        self.assertEqual(self.dr.find_element_per_identifier_from_vs(element_type="variables", key="id", value=id_var),
                         target_var)
        self.assertEqual(self.dr.find_element_per_identifier_from_vs(element_type="variables", key="name",
                                                                     value=name_var),
                         target_var)
        with self.assertRaises(ValueError):
            self.dr.find_element_per_identifier_from_vs(element_type="variables", key="name", value="toto")
        with self.assertRaises(ValueError):
            self.dr.find_element_per_identifier_from_vs(element_type="variables", key="id", value="link::toto")
        self.assertEqual(self.dr.find_element_per_identifier_from_vs(element_type="variables", key="id",
                                                                     value="link::toto", default=None),
                         None)
        self.assertEqual(self.dr.find_element_per_identifier_from_vs(element_type="variables", key="name",
                                                                     value="toto", default=None),
                         None)
        with self.assertRaises(ValueError):
            self.dr.find_element_per_identifier_from_vs(element_type="opportunity/variable_group_comments", key="name",
                                                        value="undef")

        self.assertEqual(self.dr.find_element_per_identifier_from_vs(element_type="variable", value=None, key="id", default=None),
                         None)

    def test_element_from_vs(self):
        id_var = "link::1aab80fc-b006-11e6-9289-ac72891c3257"
        name_var = "ocean.wo.tavg-ol-hxy-sea.mon.GLB"
        target_var = self.dr.find_element("variables", id_var)
        self.assertEqual(self.dr.find_element_from_vs(element_type="variables", value=id_var), target_var)
        self.assertEqual(self.dr.find_element_from_vs(element_type="variables", value=name_var), target_var)
        with self.assertRaises(ValueError):
            self.dr.find_element_from_vs(element_type="variables", value="toto")
        with self.assertRaises(ValueError):
            self.dr.find_element_from_vs(element_type="variables", value="link::toto")
        self.assertEqual(self.dr.find_element_from_vs(element_type="variables", value="link::toto", default=None), None)
        self.assertEqual(self.dr.find_element_from_vs(element_type="variables", value="toto", default=None), None)
        with self.assertRaises(ValueError):
            self.dr.find_element_from_vs(element_type="opportunity/variable_group_comments", value="undef")
        self.assertEqual(self.dr.find_element_from_vs(element_type="variables", value=id_var, key="id"), target_var)

    def test_filter_elements_per_request(self):
        with self.assertRaises(TypeError):
            self.dr.filter_elements_per_request()

        self.assertEqual(self.dr.filter_elements_per_request("opportunities"), self.dr.get_opportunities())
        self.assertEqual(self.dr.filter_elements_per_request("opportunities", request_operation="any"),
                         self.dr.get_opportunities())
        with self.assertRaises(ValueError):
            self.dr.filter_elements_per_request("opportunities", request_operation="one")

        with self.assertRaises(ValueError):
            self.dr.filter_elements_per_request("opportunities", requests=dict(variables="link::test_dummy"))
        self.assertListEqual(self.dr.filter_elements_per_request("opportunities", skip_if_missing=True,
                                                                 requests=dict(variables="link::test_dummy")),
                             self.dr.get_opportunities())

        self.assertListEqual(self.dr.filter_elements_per_request("experiment_groups",
                                                                 requests=dict(variable="1aab80fc-b006-11e6-9289-ac72891c3257")),
                             [self.dr.find_element("experiment_group", id)
                              for id in ["link::80ab72c9-a698-11ef-914a-613c0433d878", "link::80ac3142-a698-11ef-914a-613c0433d878",
                                         "link::dafc748d-8c95-11ef-944e-41a8eb05f654", "link::dafc748e-8c95-11ef-944e-41a8eb05f654",
                                         "link::dafc748f-8c95-11ef-944e-41a8eb05f654", "link::dafc7490-8c95-11ef-944e-41a8eb05f654"]])
        list_var_grp = [self.dr.find_element("variable_groups", id)
                        for id in ["link::80ab73e2-a698-11ef-914a-613c0433d878", "link::80ab73e4-a698-11ef-914a-613c0433d878",
                                   "link::dafc73da-8c95-11ef-944e-41a8eb05f654", "link::dafc73dc-8c95-11ef-944e-41a8eb05f654",
                                   "link::dafc73dd-8c95-11ef-944e-41a8eb05f654", "link::dafc73de-8c95-11ef-944e-41a8eb05f654",
                                   "link::dafc7435-8c95-11ef-944e-41a8eb05f654", "link::dafc7436-8c95-11ef-944e-41a8eb05f654",
                                   "link::dafc743a-8c95-11ef-944e-41a8eb05f654", "link::dafc7464-8c95-11ef-944e-41a8eb05f654",
                                   "link::dafc747f-8c95-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.filter_elements_per_request("variable_groups",
                                                                 requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654")),
                             list_var_grp)
        found_vargrp_all = self.dr.filter_elements_per_request("variable_groups",
                                                               requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654"),
                                                               not_requests=dict(
                                                                   opportunity="dafc739f-8c95-11ef-944e-41a8eb05f654",
                                                                   variable=["babb20b4-e5dd-11e5-8482-ac72891c3257", "d243ba76-4a9f-11e6-b84e-ac72891c3257"]),
                                                               not_request_operation="all")
        self.assertEqual(len(found_vargrp_all), len(list_var_grp))
        self.assertListEqual(found_vargrp_all, list_var_grp)
        found_vargrp_any = self.dr.filter_elements_per_request("variable_groups",
                                                               requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654"),
                                                               not_requests=dict(
                                                                   opportunity="dafc739f-8c95-11ef-944e-41a8eb05f654",
                                                                   variable=["babb20b4-e5dd-11e5-8482-ac72891c3257", "d243ba76-4a9f-11e6-b84e-ac72891c3257"]),
                                                               not_request_operation="any")
        list_vargrp_any = [self.dr.find_element("variable_group", elt)
                           for elt in ["link::80ab73e2-a698-11ef-914a-613c0433d878", "link::dafc7436-8c95-11ef-944e-41a8eb05f654",
                                       "link::dafc743a-8c95-11ef-944e-41a8eb05f654", "link::dafc7464-8c95-11ef-944e-41a8eb05f654"]]
        self.assertEqual(len(found_vargrp_any), len(list_vargrp_any))
        self.assertListEqual(found_vargrp_any, list_vargrp_any)
        found_vargrp_anyofall = self.dr.filter_elements_per_request("variable_groups",
                                                                    requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654"),
                                                                    not_requests=dict(
                                                                        opportunity="dafc739f-8c95-11ef-944e-41a8eb05f654",
                                                                        variable=["babb20b4-e5dd-11e5-8482-ac72891c3257", "d243ba76-4a9f-11e6-b84e-ac72891c3257"]),
                                                                    not_request_operation="any_of_all")
        list_vargrp_anyofall = [self.dr.find_element("variable_group", elt)
                                for elt in ["link::80ab73e2-a698-11ef-914a-613c0433d878", "link::dafc7435-8c95-11ef-944e-41a8eb05f654",
                                            "link::dafc7436-8c95-11ef-944e-41a8eb05f654", "link::dafc743a-8c95-11ef-944e-41a8eb05f654",
                                            "link::dafc7464-8c95-11ef-944e-41a8eb05f654"]]
        self.assertEqual(len(found_vargrp_anyofall), len(list_vargrp_anyofall))
        self.assertListEqual(found_vargrp_anyofall, list_vargrp_anyofall)
        found_vargrp_allofany = self.dr.filter_elements_per_request("variable_groups",
                                                                    requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654"),
                                                                    not_requests=dict(
                                                                        opportunity="dafc739f-8c95-11ef-944e-41a8eb05f654",
                                                                        variable=["babb20b4-e5dd-11e5-8482-ac72891c3257", "d243ba76-4a9f-11e6-b84e-ac72891c3257"]),
                                                                    not_request_operation="all_of_any")
        self.assertEqual(len(found_vargrp_allofany), len(list_var_grp))
        self.assertListEqual(found_vargrp_allofany, list_var_grp)
        self.assertListEqual(self.dr.filter_elements_per_request("variable_groups",
                                                                 requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654"),
                                                                 not_requests=dict(opportunity="dafc739f-8c95-11ef-944e-41a8eb05f654")),
                             [self.dr.find_element("variable_group", elt)
                              for elt in ["link::80ab73e2-a698-11ef-914a-613c0433d878", "link::dafc7435-8c95-11ef-944e-41a8eb05f654",
                                          "link::dafc7436-8c95-11ef-944e-41a8eb05f654", "link::dafc743a-8c95-11ef-944e-41a8eb05f654",
                                          "link::dafc7464-8c95-11ef-944e-41a8eb05f654", "link::dafc747f-8c95-11ef-944e-41a8eb05f654"]])
        self.assertListEqual(self.dr.filter_elements_per_request(self.dr.get_variable_groups(),
                                                                 requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654")),
                             list_var_grp)
        self.assertListEqual(self.dr.filter_elements_per_request(self.dr.get_variable_group("dafc7435-8c95-11ef-944e-41a8eb05f654"),
                                                                 requests=dict(experiment="527f5c48-8c97-11ef-944e-41a8eb05f654")),
                             [self.dr.find_element("variable_group", "dafc7435-8c95-11ef-944e-41a8eb05f654"), ])

    def test_find_variables_per_priority(self):
        priority = "Medium"
        priority_obj = self.dr.find_element("priority_level", "link::527f5c95-8c97-11ef-944e-41a8eb05f654")
        target_var_list = [self.dr.find_element("variables", id)
                           for id in ["link::80ab71f9-a698-11ef-914a-613c0433d878", "link::80ab71fa-a698-11ef-914a-613c0433d878",
                                      "link::80ab71fb-a698-11ef-914a-613c0433d878", "link::80ab71fc-a698-11ef-914a-613c0433d878",
                                      "link::80ab7430-a698-11ef-914a-613c0433d878", "link::80ab7431-a698-11ef-914a-613c0433d878",
                                      "link::80ab7432-a698-11ef-914a-613c0433d878", "link::80ab7433-a698-11ef-914a-613c0433d878",
                                      "link::80ab7434-a698-11ef-914a-613c0433d878", "link::80ab7435-a698-11ef-914a-613c0433d878",
                                      "link::83bbfb6e-7f07-11ef-9308-b1dd71e64bec", "link::83bbfb71-7f07-11ef-9308-b1dd71e64bec",
                                      "link::83bbfb7c-7f07-11ef-9308-b1dd71e64bec", "link::83bbfb7f-7f07-11ef-9308-b1dd71e64bec",
                                      "link::83bbfb94-7f07-11ef-9308-b1dd71e64bec", "link::83bbfc6e-7f07-11ef-9308-b1dd71e64bec",
                                      "link::83bbfc6f-7f07-11ef-9308-b1dd71e64bec", "link::ba9f3ac0-e5dd-11e5-8482-ac72891c3257",
                                      "link::ba9f643c-e5dd-11e5-8482-ac72891c3257", "link::ba9f686a-e5dd-11e5-8482-ac72891c3257",
                                      "link::ba9f91f0-e5dd-11e5-8482-ac72891c3257", "link::baa4e07e-e5dd-11e5-8482-ac72891c3257",
                                      "link::baa720e6-e5dd-11e5-8482-ac72891c3257", "link::baa72514-e5dd-11e5-8482-ac72891c3257",
                                      "link::bab52b5a-e5dd-11e5-8482-ac72891c3257", "link::bab59202-e5dd-11e5-8482-ac72891c3257",
                                      "link::bab5df78-e5dd-11e5-8482-ac72891c3257", "link::bab65138-e5dd-11e5-8482-ac72891c3257",
                                      "link::c9180bae-c5e8-11e6-84e6-5404a60d96b5", "link::c9181982-c5e8-11e6-84e6-5404a60d96b5"]]
        var_list = self.dr.find_variables_per_priority(priority=priority)
        self.assertEqual(len(var_list), 30)
        self.assertListEqual(var_list, target_var_list)
        var_list = self.dr.find_variables_per_priority(priority=priority_obj)
        self.assertEqual(len(var_list), 30)
        self.assertListEqual(var_list, target_var_list)

    def test_find_opportunities_per_theme(self):
        theme_id = "link::527f5c90-8c97-11ef-944e-41a8eb05f654"
        theme_name = "Atmosphere"
        theme_target = self.dr.find_element("data_request_themes", theme_id)
        opportunities = [self.dr.get_opportunity(id)
                         for id in ["link::dafc739e-8c95-11ef-944e-41a8eb05f654", "link::dafc739f-8c95-11ef-944e-41a8eb05f654",
                                    "link::dafc73bd-8c95-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.find_opportunities_per_theme(theme_id), opportunities)
        self.assertListEqual(self.dr.find_opportunities_per_theme(theme_name), opportunities)
        self.assertListEqual(self.dr.find_opportunities_per_theme(theme_target), opportunities)
        with self.assertRaises(ValueError):
            self.dr.find_opportunities_per_theme("toto")
        with self.assertRaises(ValueError):
            self.dr.find_opportunities_per_theme("link::toto")

    def test_find_experiments_per_theme(self):
        theme_id = "link::527f5c90-8c97-11ef-944e-41a8eb05f654"
        theme_name = "Atmosphere"
        theme_target = self.dr.find_element("data_request_themes", theme_id)
        exp = [self.dr.find_element("experiments", id)
               for id in ['link::527f5c3a-8c97-11ef-944e-41a8eb05f654', 'link::527f5c3b-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c3c-8c97-11ef-944e-41a8eb05f654', 'link::527f5c3d-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c3e-8c97-11ef-944e-41a8eb05f654', 'link::527f5c3f-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c40-8c97-11ef-944e-41a8eb05f654', 'link::527f5c41-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c42-8c97-11ef-944e-41a8eb05f654', 'link::527f5c43-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c44-8c97-11ef-944e-41a8eb05f654', 'link::527f5c45-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c46-8c97-11ef-944e-41a8eb05f654', 'link::527f5c47-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c48-8c97-11ef-944e-41a8eb05f654', 'link::527f5c49-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c4a-8c97-11ef-944e-41a8eb05f654', 'link::527f5c4b-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c4c-8c97-11ef-944e-41a8eb05f654', 'link::527f5c4d-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c4e-8c97-11ef-944e-41a8eb05f654', 'link::527f5c4f-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c50-8c97-11ef-944e-41a8eb05f654', 'link::527f5c51-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c52-8c97-11ef-944e-41a8eb05f654', 'link::527f5c53-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c54-8c97-11ef-944e-41a8eb05f654', 'link::527f5c55-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c56-8c97-11ef-944e-41a8eb05f654', 'link::527f5c57-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c58-8c97-11ef-944e-41a8eb05f654', 'link::527f5c59-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c5a-8c97-11ef-944e-41a8eb05f654', 'link::527f5c5b-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c5c-8c97-11ef-944e-41a8eb05f654', 'link::527f5c5d-8c97-11ef-944e-41a8eb05f654',
                          'link::527f5c5e-8c97-11ef-944e-41a8eb05f654', 'link::527f5c5f-8c97-11ef-944e-41a8eb05f654',
                          'link::80ab724d-a698-11ef-914a-613c0433d878', 'link::80ab72ae-a698-11ef-914a-613c0433d878',
                          'link::80ab72af-a698-11ef-914a-613c0433d878', 'link::80ab72b0-a698-11ef-914a-613c0433d878',
                          'link::80ab72b1-a698-11ef-914a-613c0433d878', 'link::80ab72b2-a698-11ef-914a-613c0433d878',
                          'link::80ab72b3-a698-11ef-914a-613c0433d878', 'link::80ab72b4-a698-11ef-914a-613c0433d878',
                          'link::80ab72b5-a698-11ef-914a-613c0433d878', 'link::80ab72b6-a698-11ef-914a-613c0433d878',
                          'link::80ab72b7-a698-11ef-914a-613c0433d878', 'link::80ab72b8-a698-11ef-914a-613c0433d878',
                          'link::80ab72b9-a698-11ef-914a-613c0433d878', 'link::80ab72ba-a698-11ef-914a-613c0433d878',
                          'link::80ab72bb-a698-11ef-914a-613c0433d878', 'link::80ab72bc-a698-11ef-914a-613c0433d878',
                          'link::80ab72bd-a698-11ef-914a-613c0433d878', 'link::80ab72be-a698-11ef-914a-613c0433d878',
                          'link::80ab72bf-a698-11ef-914a-613c0433d878', 'link::80ab72c0-a698-11ef-914a-613c0433d878',
                          'link::80ab72c1-a698-11ef-914a-613c0433d878', 'link::80ab72c2-a698-11ef-914a-613c0433d878',
                          'link::80ab72c3-a698-11ef-914a-613c0433d878', 'link::80ab72c4-a698-11ef-914a-613c0433d878',
                          'link::80ab72c5-a698-11ef-914a-613c0433d878', 'link::80ab72c6-a698-11ef-914a-613c0433d878',
                          'link::80ab72c7-a698-11ef-914a-613c0433d878', 'link::80ab72cc-a698-11ef-914a-613c0433d878',
                          'link::80ab72cd-a698-11ef-914a-613c0433d878', 'link::80ab72ce-a698-11ef-914a-613c0433d878',
                          'link::80ab72cf-a698-11ef-914a-613c0433d878', 'link::80ab72d0-a698-11ef-914a-613c0433d878',
                          'link::80ab72d1-a698-11ef-914a-613c0433d878', 'link::80ab72d2-a698-11ef-914a-613c0433d878',
                          'link::80ab73b0-a698-11ef-914a-613c0433d878', 'link::80ab73b1-a698-11ef-914a-613c0433d878',
                          'link::80ab73b2-a698-11ef-914a-613c0433d878', 'link::80ab73b3-a698-11ef-914a-613c0433d878',
                          'link::80ab73b4-a698-11ef-914a-613c0433d878', 'link::80ab73b5-a698-11ef-914a-613c0433d878',
                          'link::80ab73b6-a698-11ef-914a-613c0433d878', 'link::80ab73b7-a698-11ef-914a-613c0433d878',
                          'link::80ab73b8-a698-11ef-914a-613c0433d878', 'link::80ab73b9-a698-11ef-914a-613c0433d878',
                          'link::80ab73ba-a698-11ef-914a-613c0433d878', 'link::80ab73bb-a698-11ef-914a-613c0433d878',
                          'link::80ab73e9-a698-11ef-914a-613c0433d878', 'link::80ab73ea-a698-11ef-914a-613c0433d878',
                          'link::80ab73eb-a698-11ef-914a-613c0433d878', 'link::80ab73ee-a698-11ef-914a-613c0433d878',
                          'link::80ab73f0-a698-11ef-914a-613c0433d878', 'link::80ab73f1-a698-11ef-914a-613c0433d878']]
        self.assertListEqual(self.dr.find_experiments_per_theme(theme_id), exp)
        self.assertListEqual(self.dr.find_experiments_per_theme(theme_name), exp)
        self.assertListEqual(self.dr.find_experiments_per_theme(theme_target), exp)

    def test_find_variables_per_theme(self):
        theme_id = "link::527f5c90-8c97-11ef-944e-41a8eb05f654"
        theme_name = "Atmosphere"
        theme_target = self.dr.find_element("data_request_themes", theme_id)
        var = [self.dr.find_element("variables", id)
               for id in ['link::1aab80fc-b006-11e6-9289-ac72891c3257', 'link::5a070350-c77d-11e6-8a33-5404a60d96b5',
                          'link::6a35d178-aa6a-11e6-9736-5404a60d96b5', 'link::711075e2-faa7-11e6-bfb7-ac72891c3257',
                          'link::71237944-faa7-11e6-bfb7-ac72891c3257', 'link::714344cc-faa7-11e6-bfb7-ac72891c3257',
                          'link::7147b8fe-faa7-11e6-bfb7-ac72891c3257', 'link::714b603a-faa7-11e6-bfb7-ac72891c3257',
                          'link::714eec6e-faa7-11e6-bfb7-ac72891c3257', 'link::80ab71f6-a698-11ef-914a-613c0433d878',
                          'link::80ab71f9-a698-11ef-914a-613c0433d878', 'link::80ab71fa-a698-11ef-914a-613c0433d878',
                          'link::80ab71fb-a698-11ef-914a-613c0433d878', 'link::80ab71fc-a698-11ef-914a-613c0433d878',
                          'link::80ab71fd-a698-11ef-914a-613c0433d878', 'link::80ab740d-a698-11ef-914a-613c0433d878',
                          'link::80ab740e-a698-11ef-914a-613c0433d878', 'link::80ab740f-a698-11ef-914a-613c0433d878',
                          'link::80ab7410-a698-11ef-914a-613c0433d878', 'link::80ab7416-a698-11ef-914a-613c0433d878',
                          'link::80ab7417-a698-11ef-914a-613c0433d878', 'link::80ab7418-a698-11ef-914a-613c0433d878',
                          'link::80ab7419-a698-11ef-914a-613c0433d878', 'link::80ab741a-a698-11ef-914a-613c0433d878',
                          'link::80ab741b-a698-11ef-914a-613c0433d878', 'link::80ab741c-a698-11ef-914a-613c0433d878',
                          'link::80ab741d-a698-11ef-914a-613c0433d878', 'link::80ab741e-a698-11ef-914a-613c0433d878',
                          'link::80ab741f-a698-11ef-914a-613c0433d878', 'link::80ab7420-a698-11ef-914a-613c0433d878',
                          'link::80ab7421-a698-11ef-914a-613c0433d878', 'link::80ab7422-a698-11ef-914a-613c0433d878',
                          'link::80ab7423-a698-11ef-914a-613c0433d878', 'link::80ab7424-a698-11ef-914a-613c0433d878',
                          'link::80ab7425-a698-11ef-914a-613c0433d878', 'link::80ab7426-a698-11ef-914a-613c0433d878',
                          'link::80ab7427-a698-11ef-914a-613c0433d878', 'link::80ab7428-a698-11ef-914a-613c0433d878',
                          'link::80ab7429-a698-11ef-914a-613c0433d878', 'link::80ab742a-a698-11ef-914a-613c0433d878',
                          'link::80ab742b-a698-11ef-914a-613c0433d878', 'link::80ab742c-a698-11ef-914a-613c0433d878',
                          'link::80ab742d-a698-11ef-914a-613c0433d878', 'link::80ab742e-a698-11ef-914a-613c0433d878',
                          'link::80ab7430-a698-11ef-914a-613c0433d878', 'link::80ab7431-a698-11ef-914a-613c0433d878',
                          'link::80ab7432-a698-11ef-914a-613c0433d878', 'link::80ab7433-a698-11ef-914a-613c0433d878',
                          'link::80ab7434-a698-11ef-914a-613c0433d878', 'link::80ab7435-a698-11ef-914a-613c0433d878',
                          'link::80ab743a-a698-11ef-914a-613c0433d878', 'link::80ab743b-a698-11ef-914a-613c0433d878',
                          'link::80ab743c-a698-11ef-914a-613c0433d878', 'link::80ab743d-a698-11ef-914a-613c0433d878',
                          'link::80ab743e-a698-11ef-914a-613c0433d878', 'link::80ab743f-a698-11ef-914a-613c0433d878',
                          'link::80ab7440-a698-11ef-914a-613c0433d878', 'link::80ab7441-a698-11ef-914a-613c0433d878',
                          'link::80ab7442-a698-11ef-914a-613c0433d878', 'link::80ab7443-a698-11ef-914a-613c0433d878',
                          'link::80ab7444-a698-11ef-914a-613c0433d878', 'link::80ab7449-a698-11ef-914a-613c0433d878',
                          'link::80ab744a-a698-11ef-914a-613c0433d878', 'link::80ab744b-a698-11ef-914a-613c0433d878',
                          'link::80ab744c-a698-11ef-914a-613c0433d878', 'link::80ab744d-a698-11ef-914a-613c0433d878',
                          'link::80ab744e-a698-11ef-914a-613c0433d878', 'link::83bbfb69-7f07-11ef-9308-b1dd71e64bec',
                          'link::83bbfc71-7f07-11ef-9308-b1dd71e64bec', 'link::85c3e888-357c-11e7-8257-5404a60d96b5',
                          'link::86119ff6-357c-11e7-8257-5404a60d96b5', 'link::8bae55ba-4a5b-11e6-9cd2-ac72891c3257',
                          'link::8bae5aba-4a5b-11e6-9cd2-ac72891c3257', 'link::8baebea6-4a5b-11e6-9cd2-ac72891c3257',
                          'link::917b8532-267c-11e7-8933-ac72891c3257', 'link::baa3e4d0-e5dd-11e5-8482-ac72891c3257',
                          'link::baa3ea2a-e5dd-11e5-8482-ac72891c3257', 'link::baa3ee94-e5dd-11e5-8482-ac72891c3257',
                          'link::baa3f2e0-e5dd-11e5-8482-ac72891c3257', 'link::baa3f718-e5dd-11e5-8482-ac72891c3257',
                          'link::baa3fb50-e5dd-11e5-8482-ac72891c3257', 'link::baa507f2-e5dd-11e5-8482-ac72891c3257',
                          'link::baa51058-e5dd-11e5-8482-ac72891c3257', 'link::baa5147c-e5dd-11e5-8482-ac72891c3257',
                          'link::baa518c8-e5dd-11e5-8482-ac72891c3257', 'link::baa51d00-e5dd-11e5-8482-ac72891c3257',
                          'link::baa5255c-e5dd-11e5-8482-ac72891c3257', 'link::baa52de0-e5dd-11e5-8482-ac72891c3257',
                          'link::baa5491a-e5dd-11e5-8482-ac72891c3257', 'link::baa557f2-e5dd-11e5-8482-ac72891c3257',
                          'link::baa57688-e5dd-11e5-8482-ac72891c3257', 'link::baa586e6-e5dd-11e5-8482-ac72891c3257',
                          'link::baa58b1e-e5dd-11e5-8482-ac72891c3257', 'link::baa58f74-e5dd-11e5-8482-ac72891c3257',
                          'link::baa5942e-e5dd-11e5-8482-ac72891c3257', 'link::baa598c0-e5dd-11e5-8482-ac72891c3257',
                          'link::baa6c33a-e5dd-11e5-8482-ac72891c3257', 'link::baa6cf38-e5dd-11e5-8482-ac72891c3257',
                          'link::baa6d366-e5dd-11e5-8482-ac72891c3257', 'link::baa720e6-e5dd-11e5-8482-ac72891c3257',
                          'link::baa72514-e5dd-11e5-8482-ac72891c3257', 'link::baa83a12-e5dd-11e5-8482-ac72891c3257',
                          'link::baaa4302-e5dd-11e5-8482-ac72891c3257', 'link::baaa8326-e5dd-11e5-8482-ac72891c3257',
                          'link::baaa9852-e5dd-11e5-8482-ac72891c3257', 'link::baaace4e-e5dd-11e5-8482-ac72891c3257',
                          'link::baaad7e0-e5dd-11e5-8482-ac72891c3257', 'link::baab0382-e5dd-11e5-8482-ac72891c3257',
                          'link::baab1818-e5dd-11e5-8482-ac72891c3257', 'link::baad45c0-e5dd-11e5-8482-ac72891c3257',
                          'link::baad5d9e-e5dd-11e5-8482-ac72891c3257', 'link::baad6596-e5dd-11e5-8482-ac72891c3257',
                          'link::baaefbcc-e5dd-11e5-8482-ac72891c3257', 'link::baaefe2e-e5dd-11e5-8482-ac72891c3257',
                          'link::baaf8452-e5dd-11e5-8482-ac72891c3257', 'link::baaf86a0-e5dd-11e5-8482-ac72891c3257',
                          'link::baafe578-e5dd-11e5-8482-ac72891c3257', 'link::baafec80-e5dd-11e5-8482-ac72891c3257',
                          'link::baaff41e-e5dd-11e5-8482-ac72891c3257', 'link::bab00b98-e5dd-11e5-8482-ac72891c3257',
                          'link::bab0135e-e5dd-11e5-8482-ac72891c3257', 'link::bab01dfe-e5dd-11e5-8482-ac72891c3257',
                          'link::bab0238a-e5dd-11e5-8482-ac72891c3257', 'link::bab034a6-e5dd-11e5-8482-ac72891c3257',
                          'link::bab0919e-e5dd-11e5-8482-ac72891c3257', 'link::bab1688a-e5dd-11e5-8482-ac72891c3257',
                          'link::bab17a6e-e5dd-11e5-8482-ac72891c3257', 'link::bab19ff8-e5dd-11e5-8482-ac72891c3257',
                          'link::bab1a782-e5dd-11e5-8482-ac72891c3257', 'link::bab1c08c-e5dd-11e5-8482-ac72891c3257',
                          'link::bab1c668-e5dd-11e5-8482-ac72891c3257', 'link::bab1c85c-e5dd-11e5-8482-ac72891c3257',
                          'link::bab2f9d4-e5dd-11e5-8482-ac72891c3257', 'link::bab3c904-e5dd-11e5-8482-ac72891c3257',
                          'link::bab3cb52-e5dd-11e5-8482-ac72891c3257', 'link::bab3d692-e5dd-11e5-8482-ac72891c3257',
                          'link::bab3f8a2-e5dd-11e5-8482-ac72891c3257', 'link::bab42b88-e5dd-11e5-8482-ac72891c3257',
                          'link::bab45df6-e5dd-11e5-8482-ac72891c3257', 'link::bab46db4-e5dd-11e5-8482-ac72891c3257',
                          'link::bab47354-e5dd-11e5-8482-ac72891c3257', 'link::bab47b56-e5dd-11e5-8482-ac72891c3257',
                          'link::bab48ce0-e5dd-11e5-8482-ac72891c3257', 'link::bab491f4-e5dd-11e5-8482-ac72891c3257',
                          'link::bab52b5a-e5dd-11e5-8482-ac72891c3257', 'link::bab52da8-e5dd-11e5-8482-ac72891c3257',
                          'link::bab5540e-e5dd-11e5-8482-ac72891c3257', 'link::bab578d0-e5dd-11e5-8482-ac72891c3257',
                          'link::bab59202-e5dd-11e5-8482-ac72891c3257', 'link::bab5aad0-e5dd-11e5-8482-ac72891c3257',
                          'link::bab5bcdc-e5dd-11e5-8482-ac72891c3257', 'link::bab5c7fe-e5dd-11e5-8482-ac72891c3257',
                          'link::bab5df78-e5dd-11e5-8482-ac72891c3257', 'link::bab5e1b2-e5dd-11e5-8482-ac72891c3257',
                          'link::bab5ecd4-e5dd-11e5-8482-ac72891c3257', 'link::bab607c8-e5dd-11e5-8482-ac72891c3257',
                          'link::bab6219a-e5dd-11e5-8482-ac72891c3257', 'link::bab65138-e5dd-11e5-8482-ac72891c3257',
                          'link::bab6537c-e5dd-11e5-8482-ac72891c3257', 'link::bab670b4-e5dd-11e5-8482-ac72891c3257',
                          'link::bab68ebe-e5dd-11e5-8482-ac72891c3257', 'link::bab69c06-e5dd-11e5-8482-ac72891c3257',
                          'link::bab6f494-e5dd-11e5-8482-ac72891c3257', 'link::bab6fe58-e5dd-11e5-8482-ac72891c3257',
                          'link::bab73a76-e5dd-11e5-8482-ac72891c3257', 'link::bab742c8-e5dd-11e5-8482-ac72891c3257',
                          'link::bab7c2d4-e5dd-11e5-8482-ac72891c3257', 'link::bab81e50-e5dd-11e5-8482-ac72891c3257',
                          'link::bab8fa0a-e5dd-11e5-8482-ac72891c3257', 'link::bab902e8-e5dd-11e5-8482-ac72891c3257',
                          'link::bab91b20-e5dd-11e5-8482-ac72891c3257', 'link::bab9237c-e5dd-11e5-8482-ac72891c3257',
                          'link::bab928ae-e5dd-11e5-8482-ac72891c3257', 'link::bab942a8-e5dd-11e5-8482-ac72891c3257',
                          'link::bab94a50-e5dd-11e5-8482-ac72891c3257', 'link::bab955ea-e5dd-11e5-8482-ac72891c3257',
                          'link::bab95fae-e5dd-11e5-8482-ac72891c3257', 'link::bab96cc4-e5dd-11e5-8482-ac72891c3257',
                          'link::bab9888a-e5dd-11e5-8482-ac72891c3257', 'link::bab9bd00-e5dd-11e5-8482-ac72891c3257',
                          'link::babaef0e-e5dd-11e5-8482-ac72891c3257', 'link::babb12ae-e5dd-11e5-8482-ac72891c3257',
                          'link::babb4b34-e5dd-11e5-8482-ac72891c3257', 'link::babb5084-e5dd-11e5-8482-ac72891c3257',
                          'link::babb5db8-e5dd-11e5-8482-ac72891c3257', 'link::babb67c2-e5dd-11e5-8482-ac72891c3257',
                          'link::babb6cea-e5dd-11e5-8482-ac72891c3257', 'link::babbb25e-e5dd-11e5-8482-ac72891c3257',
                          'link::babbbbe6-e5dd-11e5-8482-ac72891c3257', 'link::babbcd34-e5dd-11e5-8482-ac72891c3257',
                          'link::babbd25c-e5dd-11e5-8482-ac72891c3257', 'link::babbdec8-e5dd-11e5-8482-ac72891c3257',
                          'link::babd0906-e5dd-11e5-8482-ac72891c3257', 'link::babd0e56-e5dd-11e5-8482-ac72891c3257',
                          'link::babd9ace-e5dd-11e5-8482-ac72891c3257', 'link::babda032-e5dd-11e5-8482-ac72891c3257',
                          'link::d241a6d2-4a9f-11e6-b84e-ac72891c3257', 'link::f2fad86e-c38d-11e6-abc1-1b922e5e1118']]
        self.assertListEqual(self.dr.find_variables_per_theme(theme_id), var)
        self.assertListEqual(self.dr.find_variables_per_theme(theme_name), var)
        self.assertListEqual(self.dr.find_variables_per_theme(theme_target), var)

    def test_find_mips_per_theme(self):
        theme_id = "link::527f5c90-8c97-11ef-944e-41a8eb05f654"
        theme_name = "Atmosphere"
        theme_target = self.dr.find_element("data_request_themes", theme_id)
        mips = [self.dr.find_element("mips", id)
                for id in ["link::527f5c6c-8c97-11ef-944e-41a8eb05f654", "link::527f5c6d-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c6e-8c97-11ef-944e-41a8eb05f654", "link::527f5c70-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c74-8c97-11ef-944e-41a8eb05f654", "link::527f5c75-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c76-8c97-11ef-944e-41a8eb05f654", "link::527f5c77-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c83-8c97-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.find_mips_per_theme(theme_id), mips)
        self.assertListEqual(self.dr.find_mips_per_theme(theme_name), mips)
        self.assertListEqual(self.dr.find_mips_per_theme(theme_target), mips)

    def test_themes_per_opportunity(self):
        op_id = "link::dafc73bd-8c95-11ef-944e-41a8eb05f654"
        op_name = "Accurate assessment of land-atmosphere coupling"
        op_target = self.dr.find_element("opportunities", op_id)
        themes = [self.dr.find_element("data_request_themes", id)
                  for id in ["link::527f5c90-8c97-11ef-944e-41a8eb05f654", "link::527f5c91-8c97-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.find_themes_per_opportunity(op_id), themes)
        self.assertListEqual(self.dr.find_themes_per_opportunity(op_name), themes)
        self.assertListEqual(self.dr.find_themes_per_opportunity(op_target), themes)

    def test_experiments_per_opportunity(self):
        op_id = "link::dafc73bd-8c95-11ef-944e-41a8eb05f654"
        op_name = "Accurate assessment of land-atmosphere coupling"
        op_target = self.dr.find_element("opportunities", op_id)
        exp = [self.dr.find_element("experiments", id)
               for id in ["link::527f5c3d-8c97-11ef-944e-41a8eb05f654", "link::527f5c3f-8c97-11ef-944e-41a8eb05f654",
                          "link::527f5c5a-8c97-11ef-944e-41a8eb05f654", "link::527f5c5b-8c97-11ef-944e-41a8eb05f654",
                          "link::527f5c5c-8c97-11ef-944e-41a8eb05f654", "link::527f5c5d-8c97-11ef-944e-41a8eb05f654",
                          "link::527f5c5e-8c97-11ef-944e-41a8eb05f654", "link::527f5c5f-8c97-11ef-944e-41a8eb05f654",
                          "link::80ab72ae-a698-11ef-914a-613c0433d878", "link::80ab72af-a698-11ef-914a-613c0433d878",
                          "link::80ab72b0-a698-11ef-914a-613c0433d878", "link::80ab72b1-a698-11ef-914a-613c0433d878",
                          "link::80ab72b2-a698-11ef-914a-613c0433d878", "link::80ab72b3-a698-11ef-914a-613c0433d878"]]
        self.assertListEqual(self.dr.find_experiments_per_opportunity(op_id), exp)
        self.assertListEqual(self.dr.find_experiments_per_opportunity(op_name), exp)
        self.assertListEqual(self.dr.find_experiments_per_opportunity(op_target), exp)

    def test_variables_per_opportunity(self):
        op_id = "link::dafc73bd-8c95-11ef-944e-41a8eb05f654"
        op_name = "Accurate assessment of land-atmosphere coupling"
        op_target = self.dr.find_element("opportunities", op_id)
        var = [self.dr.find_element("variables", id)
               for id in ['link::80ab71f9-a698-11ef-914a-613c0433d878', 'link::80ab71fa-a698-11ef-914a-613c0433d878',
                          'link::80ab71fb-a698-11ef-914a-613c0433d878', 'link::80ab71fc-a698-11ef-914a-613c0433d878',
                          'link::80ab71fd-a698-11ef-914a-613c0433d878', 'link::80ab7430-a698-11ef-914a-613c0433d878',
                          'link::80ab7431-a698-11ef-914a-613c0433d878', 'link::80ab7432-a698-11ef-914a-613c0433d878',
                          'link::80ab7433-a698-11ef-914a-613c0433d878', 'link::80ab7434-a698-11ef-914a-613c0433d878',
                          'link::80ab7435-a698-11ef-914a-613c0433d878', 'link::83bbfc71-7f07-11ef-9308-b1dd71e64bec',
                          'link::baaefbcc-e5dd-11e5-8482-ac72891c3257', 'link::baaf8452-e5dd-11e5-8482-ac72891c3257',
                          'link::bab034a6-e5dd-11e5-8482-ac72891c3257', 'link::bab1c668-e5dd-11e5-8482-ac72891c3257',
                          'link::bab3c904-e5dd-11e5-8482-ac72891c3257', 'link::bab47354-e5dd-11e5-8482-ac72891c3257',
                          'link::bab52b5a-e5dd-11e5-8482-ac72891c3257', 'link::bab59202-e5dd-11e5-8482-ac72891c3257',
                          'link::bab5df78-e5dd-11e5-8482-ac72891c3257', 'link::bab65138-e5dd-11e5-8482-ac72891c3257',
                          'link::bab91b20-e5dd-11e5-8482-ac72891c3257', 'link::babb12ae-e5dd-11e5-8482-ac72891c3257']]
        self.assertListEqual(self.dr.find_variables_per_opportunity(op_id), var)
        self.assertListEqual(self.dr.find_variables_per_opportunity(op_name), var)
        self.assertListEqual(self.dr.find_variables_per_opportunity(op_target), var)

    def test_mips_per_opportunity(self):
        op_id = "link::dafc73bd-8c95-11ef-944e-41a8eb05f654"
        op_name = "Accurate assessment of land-atmosphere coupling"
        op_target = self.dr.find_element("opportunities", op_id)
        mips = [self.dr.find_element("mips", id)
                for id in ["link::527f5c6d-8c97-11ef-944e-41a8eb05f654", "link::527f5c74-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c75-8c97-11ef-944e-41a8eb05f654", "link::527f5c76-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c77-8c97-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.find_mips_per_opportunity(op_id), mips)
        self.assertListEqual(self.dr.find_mips_per_opportunity(op_name), mips)
        self.assertListEqual(self.dr.find_mips_per_opportunity(op_target), mips)

    def test_opportunities_per_variable(self):
        var_id = "link::83bbfb69-7f07-11ef-9308-b1dd71e64bec"
        var_name = "ocean.zos.tavg-u-hxy-sea.day.GLB"
        var_target = self.dr.find_element("variables", var_id)
        op = [self.dr.find_element("opportunities", id)
              for id in ["link::dafc739e-8c95-11ef-944e-41a8eb05f654", "link::dafc739f-8c95-11ef-944e-41a8eb05f654",
                         "link::dafc73a5-8c95-11ef-944e-41a8eb05f654", ]]
        self.assertListEqual(self.dr.find_opportunities_per_variable(var_id), op)
        self.assertListEqual(self.dr.find_opportunities_per_variable(var_name), op)
        self.assertListEqual(self.dr.find_opportunities_per_variable(var_target), op)

    def test_themes_per_variable(self):
        var_id = "link::83bbfb69-7f07-11ef-9308-b1dd71e64bec"
        var_name = "ocean.zos.tavg-u-hxy-sea.day.GLB"
        var_target = self.dr.find_element("variables", var_id)
        themes = [self.dr.find_element("data_request_themes", id)
                  for id in ["link::527f5c8f-8c97-11ef-944e-41a8eb05f654", "link::527f5c90-8c97-11ef-944e-41a8eb05f654",
                             "link::527f5c91-8c97-11ef-944e-41a8eb05f654", "link::527f5c92-8c97-11ef-944e-41a8eb05f654",
                             "link::527f5c93-8c97-11ef-944e-41a8eb05f654"]
                  ]
        self.assertListEqual(self.dr.find_themes_per_variable(var_id), themes)
        self.assertListEqual(self.dr.find_themes_per_variable(var_name), themes)
        self.assertListEqual(self.dr.find_themes_per_variable(var_target), themes)

    def test_mips_per_variable(self):
        var_id = "link::83bbfb69-7f07-11ef-9308-b1dd71e64bec"
        var_name = "ocean.zos.tavg-u-hxy-sea.day.GLB"
        var_target = self.dr.find_element("variables", var_id)
        mips = [self.dr.find_element("mips", id)
                for id in ["link::527f5c64-8c97-11ef-944e-41a8eb05f654", "link::527f5c65-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c66-8c97-11ef-944e-41a8eb05f654", "link::527f5c6b-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c6c-8c97-11ef-944e-41a8eb05f654", "link::527f5c6d-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c6e-8c97-11ef-944e-41a8eb05f654", "link::527f5c6f-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c70-8c97-11ef-944e-41a8eb05f654", "link::527f5c73-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c74-8c97-11ef-944e-41a8eb05f654", "link::527f5c75-8c97-11ef-944e-41a8eb05f654",
                           "link::527f5c76-8c97-11ef-944e-41a8eb05f654", "link::527f5c83-8c97-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.find_mips_per_variable(var_id), mips)
        self.assertListEqual(self.dr.find_mips_per_variable(var_name), mips)
        self.assertListEqual(self.dr.find_mips_per_variable(var_target), mips)

    def test_opportunities_per_experiment(self):
        exp_id = "link::527f5c46-8c97-11ef-944e-41a8eb05f654"
        exp_name = "hist-piAQ"
        exp_target = self.dr.find_element("experiments", exp_id)
        op = [self.dr.find_element("opportunities", id)
              for id in ["link::dafc739e-8c95-11ef-944e-41a8eb05f654", "link::dafc739f-8c95-11ef-944e-41a8eb05f654",
                         "link::dafc73a5-8c95-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.find_opportunities_per_experiment(exp_id), op)
        self.assertListEqual(self.dr.find_opportunities_per_experiment(exp_name), op)
        self.assertListEqual(self.dr.find_opportunities_per_experiment(exp_target), op)

    def test_themes_per_experiment(self):
        exp_id = "link::527f5c46-8c97-11ef-944e-41a8eb05f654"
        exp_name = "hist-piAQ"
        exp_target = self.dr.find_element("experiments", exp_id)
        themes = [self.dr.find_element("data_request_themes", id)
                  for id in ["link::527f5c8f-8c97-11ef-944e-41a8eb05f654", "link::527f5c90-8c97-11ef-944e-41a8eb05f654",
                             "link::527f5c91-8c97-11ef-944e-41a8eb05f654", "link::527f5c92-8c97-11ef-944e-41a8eb05f654",
                             "link::527f5c93-8c97-11ef-944e-41a8eb05f654"]]
        self.assertListEqual(self.dr.find_themes_per_experiment(exp_id), themes)
        self.assertListEqual(self.dr.find_themes_per_experiment(exp_name), themes)
        self.assertListEqual(self.dr.find_themes_per_experiment(exp_target), themes)

    def test_find_opportunities(self):
        vargrp_id = "link::80ab723b-a698-11ef-914a-613c0433d878"
        exp_id = "link::527f5c46-8c97-11ef-944e-41a8eb05f654"
        list_all = list()
        list_any = [self.dr.find_element("opportunities", id)
                    for id in ["dafc739e-8c95-11ef-944e-41a8eb05f654", "dafc739f-8c95-11ef-944e-41a8eb05f654",
                               "dafc73a5-8c95-11ef-944e-41a8eb05f654", "dafc73bd-8c95-11ef-944e-41a8eb05f654"]
                    ]
        self.assertListEqual(self.dr.find_opportunities(operation="all", variable_group=vargrp_id,
                                                        experiments=[exp_id, ]), list_all)
        self.assertListEqual(self.dr.find_opportunities(operation="any", variable_group=vargrp_id,
                                                        experiments=[exp_id, ]), list_any)

    def test_find_experiments(self):
        op_id = "link::dafc73bd-8c95-11ef-944e-41a8eb05f654"
        expgrp_id = ["link::80ab723e-a698-11ef-914a-613c0433d878", "link::dafc7490-8c95-11ef-944e-41a8eb05f654"]
        list_all = list()
        list_any = [self.dr.find_element("experiments", id)
                    for id in ["link::527f5c3d-8c97-11ef-944e-41a8eb05f654", "link::527f5c3f-8c97-11ef-944e-41a8eb05f654",
                               "link::527f5c53-8c97-11ef-944e-41a8eb05f654", "link::527f5c5a-8c97-11ef-944e-41a8eb05f654",
                               "link::527f5c5b-8c97-11ef-944e-41a8eb05f654", "link::527f5c5c-8c97-11ef-944e-41a8eb05f654",
                               "link::527f5c5d-8c97-11ef-944e-41a8eb05f654", "link::527f5c5e-8c97-11ef-944e-41a8eb05f654",
                               "link::527f5c5f-8c97-11ef-944e-41a8eb05f654", "link::80ab72ae-a698-11ef-914a-613c0433d878",
                               "link::80ab72af-a698-11ef-914a-613c0433d878", "link::80ab72b0-a698-11ef-914a-613c0433d878",
                               "link::80ab72b1-a698-11ef-914a-613c0433d878", "link::80ab72b2-a698-11ef-914a-613c0433d878",
                               "link::80ab72b3-a698-11ef-914a-613c0433d878"]]
        self.assertListEqual(self.dr.find_experiments(operation="all", opportunities=op_id,
                                                      experiment_groups=expgrp_id), list_all)
        self.assertListEqual(self.dr.find_experiments(operation="any", opportunities=op_id,
                                                      experiment_groups=expgrp_id), list_any)

    def test_find_variables(self):
        table_id = "527f5ced-8c97-11ef-944e-41a8eb05f654"
        vars_id = ["83bbfbbc-7f07-11ef-9308-b1dd71e64bec", "83bbfbbd-7f07-11ef-9308-b1dd71e64bec",
                   "8baebea6-4a5b-11e6-9cd2-ac72891c3257", "8bb11ef8-4a5b-11e6-9cd2-ac72891c3257"]
        self.assertListEqual(self.dr.find_variables(operation="all", table_identifier=table_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        tshp_id = "a06034e5-bbca-11ef-9840-9de7167a7ecb"
        vars_id = ["bab942a8-e5dd-11e5-8482-ac72891c3257", "bab955ea-e5dd-11e5-8482-ac72891c3257"]
        self.assertListEqual(self.dr.find_variables(operation="all", temporal_shape=tshp_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        sshp_id = "a6563bca-8883-11e5-b571-ac72891c3257"
        vars_id = ["f2fad86e-c38d-11e6-abc1-1b922e5e1118", ]
        self.assertListEqual(self.dr.find_variables(operation="all", spatial_shape=sshp_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        param_id = "00e77372e8b909d9a827a0790e991fd9"
        vars_id = ["bab2f9d4-e5dd-11e5-8482-ac72891c3257", ]
        self.assertListEqual(self.dr.find_variables(operation="all", physical_parameter=param_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        realm_id = "ocnBgchem"
        vars_id = ["83bbfb7c-7f07-11ef-9308-b1dd71e64bec", "83bbfb7f-7f07-11ef-9308-b1dd71e64bec",
                   "83bbfb94-7f07-11ef-9308-b1dd71e64bec", "ba9f3ac0-e5dd-11e5-8482-ac72891c3257",
                   "ba9f643c-e5dd-11e5-8482-ac72891c3257", "ba9f686a-e5dd-11e5-8482-ac72891c3257",
                   "ba9f91f0-e5dd-11e5-8482-ac72891c3257", "c9180bae-c5e8-11e6-84e6-5404a60d96b5",
                   "c9181982-c5e8-11e6-84e6-5404a60d96b5"]
        self.assertListEqual(self.dr.find_variables(operation="all", modelling_realm=realm_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        bcv_id = "80ab7325-a698-11ef-914a-613c0433d878"
        vars_id = ["bab3c904-e5dd-11e5-8482-ac72891c3257", ]
        self.assertListEqual(self.dr.find_variables(operation="all", **{"esm-bcv": bcv_id}),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        cf_std_id = "3ba74d83-8ca2-11ef-944e-41a8eb05f654"
        vars_id = ["baab0382-e5dd-11e5-8482-ac72891c3257", ]
        self.assertListEqual(self.dr.find_variables(operation="all", cf_standard_name=cf_std_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        cell_methods_id = "a269a4c3-8c9b-11ef-944e-41a8eb05f654"
        vars_id = ["bab1c08c-e5dd-11e5-8482-ac72891c3257", "bab5c7fe-e5dd-11e5-8482-ac72891c3257",
                   "f2fad86e-c38d-11e6-abc1-1b922e5e1118"]
        self.assertListEqual(self.dr.find_variables(operation="all", cell_methods=cell_methods_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

        cell_measure_id = "a269a4f8-8c9b-11ef-944e-41a8eb05f654"
        vars_id = ["baa6cf38-e5dd-11e5-8482-ac72891c3257", "baa6d366-e5dd-11e5-8482-ac72891c3257"]
        self.assertListEqual(self.dr.find_variables(operation="all", cell_measures=cell_measure_id),
                             [self.dr.find_element("variables", var_id) for var_id in vars_id])

    def test_find_priority_per_variable(self):
        var_id = "link::babb20b4-e5dd-11e5-8482-ac72891c3257"
        var = self.dr.find_element("variable", var_id)
        self.assertEqual(self.dr.find_priority_per_variable(var), 2)

    def test_cache_issue(self):
        with tempfile.TemporaryDirectory() as output_dir:
            self.dr.find_variables_per_opportunity(self.dr.get_opportunities()[0])
            self.dr.export_summary("variables", "opportunities",
                                   os.sep.join([output_dir, "var_per_op.csv"]))

    def test_export_summary(self):
        with tempfile.TemporaryDirectory() as output_dir:
            self.dr.export_summary("opportunities", "data_request_themes",
                                   os.sep.join([output_dir, "op_per_th.csv"]))
            self.dr.export_summary("variables", "opportunities",
                                   os.sep.join([output_dir, "var_per_op.csv"]))
            self.dr.export_summary("opportunities", "variables",
                                   os.sep.join([output_dir, "op_per_var.csv"]))
            self.dr.export_summary("experiments", "opportunities",
                                   os.sep.join([output_dir, "exp_per_op.csv"]))
            self.dr.export_summary("variables", "spatial_shape",
                                   os.sep.join([output_dir, "var_per_spsh.csv"]))

    def test_export_data(self):
        with tempfile.TemporaryDirectory() as output_dir:
            self.dr.export_data("opportunities",
                                os.sep.join([output_dir, "op.csv"]),
                                export_columns_request=["name", "lead_theme", "description"])
