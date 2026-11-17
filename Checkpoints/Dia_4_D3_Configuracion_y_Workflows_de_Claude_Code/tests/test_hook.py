import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "proteger_secretos.py"


def ejecutar_hook(evento):
    proceso = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(evento), capture_output=True, text=True, check=True
    )
    return json.loads(proceso.stdout) if proceso.stdout else None


class TestHook(unittest.TestCase):
    def test_denegar_env(self):
        r = ejecutar_hook({"tool_name": "Write", "tool_input": {"file_path": ".env"}})
        self.assertEqual(r["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_denegar_env_windows(self):
        r = ejecutar_hook({"tool_name": "Edit", "tool_input": {"file_path": r"C:\app\.env.production"}})
        self.assertEqual(r["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_denegar_secrets(self):
        r = ejecutar_hook({"tool_name": "Write", "tool_input": {"file_path": "config/secrets.json"}})
        self.assertEqual(r["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_permitir_python_ordinario(self):
        self.assertIsNone(ejecutar_hook({"tool_name": "Edit", "tool_input": {"file_path": "src/calificaciones.py"}}))

    def test_no_intervenir_read(self):
        self.assertIsNone(ejecutar_hook({"tool_name": "Read", "tool_input": {"file_path": ".env"}}))

    def test_bloquear_input_ausente(self):
        r = ejecutar_hook({"tool_name": "Write", "tool_input": {}})
        self.assertEqual(r["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_entrada_no_objeto(self):
        # Se envía JSON válido pero no un objeto: el script debe negar.
        proceso = subprocess.run([sys.executable, str(HOOK_PATH)], input="[]", capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(proceso.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

