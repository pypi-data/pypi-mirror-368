import sys
import types
import unittest
from unittest.mock import patch, mock_open, MagicMock

airflow_exceptions = types.ModuleType("airflow.exceptions")
airflow_exceptions.AirflowException = Exception
sys.modules["airflow.exceptions"] = airflow_exceptions

airflow_settings = types.ModuleType("airflow.settings")
airflow_settings.initialize = lambda: None
airflow_settings.LAZY_LOAD_PROVIDERS = True
sys.modules["airflow.settings"] = airflow_settings

sys.modules["airflow.configuration"] = types.ModuleType("airflow.configuration")

airflow_operators = types.ModuleType("airflow.operators")
airflow_operators_python = types.ModuleType("airflow.operators.python")


class DummyPythonOperator:
    def __init__(self, *args, **kwargs):
        # This dummy operator is intentionally left empty because it is only used
        # to mock Airflow's PythonOperator for testing purposes. No initialization logic is needed.
        pass


airflow_operators_python.PythonOperator = DummyPythonOperator
sys.modules["airflow.operators"] = airflow_operators
sys.modules["airflow.operators.python"] = airflow_operators_python

from regscale.airflow.tasks.init import get_shared_keys, set_shared_config_values  # noqa: E402


class TestInitPy(unittest.TestCase):
    @patch("regscale.airflow.tasks.init.execute_click_command")
    @patch("yaml.safe_load", return_value={"foo": "bar"})
    @patch("pathlib.Path.open", new_callable=mock_open, read_data="foo: bar\n")
    def test_get_shared_keys(self, mock_file, mock_yaml, mock_exec):
        """
        If the YAML and dag_run.conf share a key, we should get that key back and execute the click command once.
        """
        dag_context = {"dag_run": MagicMock(conf={"foo": "baz"})}
        shared_keys = get_shared_keys("dummy.yaml", **dag_context)
        self.assertEqual(shared_keys, ["foo"])
        mock_exec.assert_called_once()

    @patch("regscale.airflow.tasks.init.execute_click_command")
    def test_set_shared_config_values(self, mock_exec):
        """
        When shared keys are found in xcom, set_shared_config_values should call execute_click_command for each.
        """
        dag_context = {
            "dag_run": MagicMock(conf={"foo": "bar", "op_kwargs": {"shared_keys_task": "task1"}}),
            "ti": MagicMock(xcom_pull=MagicMock(return_value=["foo"])),
        }
        set_shared_config_values(shared_keys_task=None, **dag_context)
        mock_exec.assert_called_once()

    def test_set_shared_config_values_raises(self):
        """
        If op_kwargs is missing from dag_run.conf, set_shared_config_values should raise an AirflowException.
        """
        from airflow.exceptions import AirflowException

        dag_context = {"dag_run": MagicMock(conf={})}
        with self.assertRaises(AirflowException):
            set_shared_config_values(shared_keys_task=None, **dag_context)

    @patch("regscale.airflow.tasks.init.execute_click_command")
    def test_set_shared_config_values_warns(self, mock_exec):
        """
        If xcom_pull returns None, set_shared_config_values should log a warning and not call execute_click_command.
        """
        dag_context = {
            "dag_run": MagicMock(conf={"foo": "bar", "op_kwargs": {"shared_keys_task": "task1"}}),
            "ti": MagicMock(xcom_pull=MagicMock(return_value=None)),
        }
        with self.assertLogs(level="WARNING") as log:
            set_shared_config_values(shared_keys_task=None, **dag_context)
        self.assertTrue(any("No shared keys found" in msg for msg in log.output))
        mock_exec.assert_not_called()

    @patch("yaml.safe_load", return_value={"foo": "bar"})
    @patch("pathlib.Path.open", new_callable=mock_open, read_data="foo: bar\n")
    def test_get_shared_keys_logs_error(self, mock_file, mock_yaml):
        """
        If dag_run is missing from the context, get_shared_keys should log an error and raise KeyError.
        """
        with self.assertLogs(level="ERROR") as log, self.assertRaises(KeyError):
            get_shared_keys("dummy.yaml")
        self.assertTrue(any("context contains" in msg for msg in log.output))


if __name__ == "__main__":
    unittest.main()
