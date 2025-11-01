import sys
import os
from streamlit.web import cli as stcli

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath("src"))
    sys.argv=["streamlit", "run", "src/app/main.py"]
    stcli.main()
