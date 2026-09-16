import subprocess
from pathlib import Path


class OPAValidator:

    def __init__(self, opa_command="opa"):
        self.opa_command = opa_command

    def validate(self, rego_path):
        rego_path = Path(rego_path)

        if not rego_path.exists():
            raise FileNotFoundError(
                f"Rego file not found: {rego_path}"
            )

        result = subprocess.run(
            [
                self.opa_command,
                "check",
                str(rego_path)
            ],
            capture_output=True,
            text=True
        )

        return {
            "valid": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return_code": result.returncode
        }