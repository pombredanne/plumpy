from unittest import TestCase
from plum.process import Process
from tests.common import ProcessListenerTester
from plum.parallel import MultithreadedEngine


class DummyProcess(Process):
    @staticmethod
    def _define(spec):
        spec.dynamic_input()
        spec.dynamic_output()

    def _run(self, **kwargs):
        self.out("default", 5)


class TestProcess(TestCase):
    def setUp(self):
        self.events_tester = ProcessListenerTester()
        self.proc = DummyProcess()
        self.proc.add_process_listener(self.events_tester)

    def tearDown(self):
        self.proc.remove_process_listener(self.events_tester)

    def test_on_start(self):
        self.proc.on_start(None)
        self.assertTrue(self.events_tester.start)

    def test_on_output_emitted(self):
        self.proc._run()
        self.assertTrue(self.events_tester.emitted)

    def test_on_finalise(self):
        self.proc.on_destroy()
        self.assertTrue(self.events_tester.destroy)

    def test_on_finished(self):
        self.proc.on_finish(None)
        self.assertTrue(self.events_tester.finish)

    def test_dynamic_inputs(self):
        class NoDynamic(Process):
            @staticmethod
            def _define(spec):
                pass

            def _run(self, **kwargs):
                pass

        class WithDynamic(Process):
            @staticmethod
            def _define(spec):
                spec.dynamic_input()

            def _run(self, **kwargs):
                pass

        with self.assertRaises(ValueError):
            NoDynamic.run(inputs={'a': 5})
        WithDynamic.run(inputs={'a': 5})

    def test_inputs(self):
        class Proc(Process):
            @staticmethod
            def _define(spec):
                spec.input('a')

            def _run(self, a):
                pass

        p = Proc()

        # Check that we can't access inputs before creating
        with self.assertRaises(AttributeError):
            p.inputs.a

        # Check that we can access the inputs after creating
        p.on_create(0, {'a': 5})
        self.assertEqual(p.inputs.a, 5)
        with self.assertRaises(AttributeError):
            p.inputs.b

        # Check that we can't access inputs after finishing
        p = Proc()
        p.run(inputs={'a': 5})
        with self.assertRaises(AttributeError):
            p.inputs.a

    def test_run(self):
        engine = MultithreadedEngine()
        results = DummyProcess.run(None, engine)
        self.assertEqual(results['default'], 5)





