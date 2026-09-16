import json
from pathlib import Path

from app.rego_generator import RegoGenerator
from app.opa_validator import OPAValidator


POLICY_PATH = Path(
    "output/policy_659ea3e2/policy.json"
)

REGO_PATH = Path(
    "output/policy_659ea3e2/policy.rego"
)


def main():

    print("Loading policy...")
    
    with open(
        POLICY_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        policy_data = json.load(file)

    print("Generating Rego...")

    generator = RegoGenerator()

    rego = generator.generate(
        policy_data
    )

    REGO_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REGO_PATH.write_text(
        rego,
        encoding="utf-8"
    )

    print(
        f"Rego generated: {REGO_PATH}"
    )

    print("\nValidating with OPA...")

    validator = OPAValidator()

    result = validator.validate(
        REGO_PATH
    )

    if result["valid"]:
        print("OPA validation: VALID")
    else:
        print("OPA validation: INVALID")

        if result["stderr"]:
            print("\nOPA error:")
            print(result["stderr"])


if __name__ == "__main__":
    main()