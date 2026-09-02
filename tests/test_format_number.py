import re
import subprocess
from pathlib import Path

APP_JS = Path(__file__).resolve().parent.parent / "frontend" / "app.js"


def _format_number_source():
    text = APP_JS.read_text(encoding="utf-8")
    match = re.search(
        r"function formatNumber\(value\) \{.*?\n\}",
        text,
        flags=re.DOTALL,
    )
    assert match, "formatNumber was not found in frontend/app.js"
    return match.group(0)


def test_format_number_null_and_zero():
    source = _format_number_source()
    script = (
        source
        + """
const results = {
  nullValue: formatNumber(null),
  undefinedValue: formatNumber(undefined),
  zeroValue: formatNumber(0)
};
if (results.nullValue === "0" || results.undefinedValue === "0") {
  process.stderr.write("null/undefined became 0\\n");
  process.exit(1);
}
if (results.nullValue !== "Not available" || results.undefinedValue !== "Not available") {
  process.stderr.write(JSON.stringify(results) + "\\n");
  process.exit(1);
}
if (results.zeroValue !== "0") {
  process.stderr.write("zero display: " + results.zeroValue + "\\n");
  process.exit(1);
}
process.stdout.write(JSON.stringify(results));
"""
    )
    completed = subprocess.run(
        ["node", "-e", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert '"nullValue":"Not available"' in completed.stdout
    assert '"zeroValue":"0"' in completed.stdout
