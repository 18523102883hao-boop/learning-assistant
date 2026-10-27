import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "workbuddy/experts/learning-partner"


class YiyiRecordsAdapterTests(unittest.TestCase):
    def load_launcher(self):
        path = ROOT / "scripts/start_learning_records.py"
        self.assertTrue(path.is_file(), "缺少真实的固定身份启动器")
        spec = importlib.util.spec_from_file_location("yiyi_launcher", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_native_dependency_and_yiyi_identity(self):
        manifest = json.loads((ROOT / ".codebuddy-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "learning-partner-yiyi")
        self.assertEqual(manifest["defaultInitPrompt"], manifest["quickPrompts"][0])
        self.assertEqual(manifest["dependencies"]["mcpServers"], "./.mcp.json")
        config = json.loads((ROOT / ".mcp.json").read_text())
        self.assertEqual(set(config["mcpServers"]), {"learning-records-yiyi"})
        server = config["mcpServers"]["learning-records-yiyi"]
        self.assertEqual(server["args"], ["${CODEBUDDY_PLUGIN_ROOT}/scripts/start_learning_records.py"])

    def test_fixed_binding_command_rejects_sibling_or_injected_options(self):
        module = self.load_launcher()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "runtime"
            (runtime / ".venv/bin").mkdir(parents=True)
            (runtime / "companion").mkdir()
            (runtime / "companion/mcp_server.py").touch()
            (runtime / "materials").mkdir()
            materials = runtime / "materials/catalog.v3.json"
            materials.write_text("{}")
            python = runtime / ".venv/bin/python"
            python.symlink_to(sys.executable)
            data = root / "student-b"
            data.mkdir()
            (data / "state.sqlite3").touch()
            binding = {"schema_version": 1, "child_id": "student-b", "runtime_root": str(runtime), "python": str(python), "data_root": str(data), "materials": str(materials)}
            command = module.build_command(binding)
            self.assertEqual(command[1:4], ["-I", "-m", "companion.mcp_server"])
            self.assertEqual(command[command.index("--child") + 1], "student-b")
            for patch in ({"child_id": "student-a"}, {"shell": "sh"}, {"python": sys.executable}, {"data_root": str(runtime)}, {"materials": str(data / "catalog.json")}):
                with self.subTest(patch=patch), self.assertRaises(module.BindingError):
                    module.build_command(binding | patch)

    def test_unconfigured_launcher_does_not_create_data_or_fake_success(self):
        self.load_launcher()
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/start_learning_records.py")], env={"HOME": temporary}, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("尚未接通", result.stderr)
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_memory_channels_and_homework_attention_are_consistent(self):
        agent = (ROOT / "agents/learning-partner-yiyi.md").read_text()
        log = (ROOT / "skills/learning-log/SKILL.md").read_text()
        self.assertIn("平台定期", agent + log)
        self.assertIn("child_opt_in=true", log)
        self.assertNotIn("首版平台自动个人记忆须由成人真实关闭", log)
        self.assertNotIn("成人 2026-10-26 确认", agent)
        self.assertIn("以下趣味联想只用于非作业", agent)
        self.assertIn("student-b", agent)


if __name__ == "__main__":
    unittest.main()
