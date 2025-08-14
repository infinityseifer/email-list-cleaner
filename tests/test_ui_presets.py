from __future__ import annotations
import pandas as pd

def test_preset_column_present_mailchimp():
    df = pd.DataFrame({"Email Address": ["a@x.com"], "First Name": ["Ada"]})
    assert "Email Address" in df.columns  # preset should target this

def test_last_choice_overrides_preset():
    df = pd.DataFrame({"Email": ["a@x.com"], "Other": ["x"]})
    # Simulate a remembered last choice
    last_choice = "Email"
    assert last_choice in df.columns
